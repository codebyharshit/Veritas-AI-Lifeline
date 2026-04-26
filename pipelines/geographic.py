"""Stage 4 — Geographic Computation pipeline for Veritas.

Computes nearest verified facility for each PIN code × capability combination.
Powers the choropleth map showing medical desert severity.
"""
import json
import math
from typing import Optional
from datetime import datetime

import sys
sys.path.insert(0, '/Workspace/Repos/harshitagarwal048@gmail.com/Veritas-AI-Lifeline')


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in km."""
    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_desert_severity(distance_km: float) -> str:
    """Classify distance into desert severity.

    Per Section 1.5:
    - green: < 50 km
    - yellow: 50-100 km
    - red: > 100 km
    """
    if distance_km < 50:
        return "green"
    elif distance_km < 100:
        return "yellow"
    else:
        return "red"


def extract_capabilities_from_json(capabilities_json: str) -> list[str]:
    """Extract capability names from JSON string."""
    if not capabilities_json:
        return []
    try:
        caps = json.loads(capabilities_json)
        return [c.get("capability", "").lower() for c in caps if c.get("capability")]
    except:
        return []


# Standard capability categories for map filtering
CAPABILITY_CATEGORIES = {
    "emergency_surgery": ["emergency surgery", "surgical", "surgery", "operation theater"],
    "dialysis": ["dialysis", "nephrology", "kidney"],
    "oncology": ["oncology", "cancer", "chemotherapy", "radiation therapy"],
    "trauma": ["trauma", "emergency", "accident", "critical care"],
    "obstetrics": ["obstetrics", "maternity", "delivery", "gynecology", "obgyn"],
    "icu": ["icu", "intensive care", "critical care", "ventilator"],
    "pediatrics": ["pediatrics", "children", "child care", "neonatal"],
    "cardiology": ["cardiology", "heart", "cardiac", "ecg", "echocardiography"],
    "orthopedics": ["orthopedics", "bone", "fracture", "joint replacement"],
    "general_medicine": ["general medicine", "internal medicine", "physician"],
}


def matches_capability(facility_capabilities: list[str], target_category: str) -> bool:
    """Check if facility capabilities match a target category."""
    if target_category not in CAPABILITY_CATEGORIES:
        return False

    keywords = CAPABILITY_CATEGORIES[target_category]
    for cap in facility_capabilities:
        for keyword in keywords:
            if keyword in cap.lower():
                return True
    return False


def run_geographic_computation(
    spark,
    raw_table: str = "workspace.veritas_dev.facilities_raw",
    structured_table: str = "workspace.veritas_dev.facilities_structured",
    trust_table: str = "workspace.veritas_dev.trust_scores",
    target_table: str = "workspace.veritas_dev.geo_lookup",
    min_trust_score: int = 60,
    min_confidence: float = 0.7,
    overwrite: bool = True,
) -> dict:
    """
    Compute nearest verified facility for each PIN code × capability.

    A facility is "verified" if:
    - trust_score >= min_trust_score
    - capability confidence >= min_confidence

    Args:
        spark: SparkSession
        raw_table: Source table with raw facility data (has coordinates)
        structured_table: Source table with extracted capabilities
        trust_table: Source table with trust scores
        target_table: Target table for geo_lookup
        min_trust_score: Minimum trust score to be considered verified
        min_confidence: Minimum capability confidence to be considered verified
        overwrite: If True, overwrite existing table

    Returns:
        dict with computation statistics
    """
    print(f"[Stage 4] Starting geographic computation")
    print(f"[Stage 4] Verified = trust_score >= {min_trust_score} AND confidence >= {min_confidence}")

    # Load data
    raw_df = spark.table(raw_table)
    structured_df = spark.table(structured_table)

    # Try to load trust scores, use defaults if not available
    try:
        trust_df = spark.table(trust_table)
        has_trust = True
    except:
        print("[Stage 4] Warning: trust_scores table not found, using default score of 70")
        has_trust = False

    # Join tables
    if has_trust:
        joined = raw_df.join(structured_df, on="facility_id", how="inner") \
                       .join(trust_df.select("facility_id", "trust_score"), on="facility_id", how="left")
    else:
        joined = raw_df.join(structured_df, on="facility_id", how="inner")

    # Collect facilities with coordinates
    facilities = joined.filter(
        joined.latitude.isNotNull() & joined.longitude.isNotNull()
    ).collect()

    print(f"[Stage 4] Found {len(facilities)} facilities with coordinates")

    # Get unique PIN codes
    pin_codes = raw_df.select("pin_code", "latitude", "longitude") \
        .filter(raw_df.latitude.isNotNull() & raw_df.longitude.isNotNull()) \
        .dropDuplicates(["pin_code"]) \
        .collect()

    print(f"[Stage 4] Computing distances for {len(pin_codes)} unique PIN codes")

    # Build facility lookup with capabilities
    facility_data = []
    for f in facilities:
        caps = extract_capabilities_from_json(f.verified_capabilities_json if hasattr(f, 'verified_capabilities_json') else None)
        trust = f.trust_score if hasattr(f, 'trust_score') and f.trust_score else 70

        facility_data.append({
            "facility_id": f.facility_id,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "trust_score": trust,
            "capabilities": caps,
        })

    # Compute geo_lookup for each PIN code × capability
    results = []
    capabilities_to_compute = list(CAPABILITY_CATEGORIES.keys())

    total_computations = len(pin_codes) * len(capabilities_to_compute)
    computed = 0

    for pin in pin_codes:
        pin_lat, pin_lon = pin.latitude, pin.longitude

        for capability in capabilities_to_compute:
            # Find nearest verified facility with this capability
            best_facility = None
            best_distance = float('inf')
            best_trust = 0

            for f in facility_data:
                # Check if facility is verified for this capability
                if f["trust_score"] < min_trust_score:
                    continue
                if not matches_capability(f["capabilities"], capability):
                    continue

                # Calculate distance
                dist = haversine_distance(pin_lat, pin_lon, f["latitude"], f["longitude"])

                if dist < best_distance:
                    best_distance = dist
                    best_facility = f["facility_id"]
                    best_trust = f["trust_score"]

            if best_facility:
                results.append({
                    "pin_code": pin.pin_code,
                    "capability": capability,
                    "nearest_facility_id": best_facility,
                    "distance_km": round(best_distance, 2),
                    "travel_time_minutes": None,  # Would need isochrone API
                    "nearest_trust_score": best_trust,
                    "desert_severity": get_desert_severity(best_distance),
                })

        computed += len(capabilities_to_compute)
        if computed % 1000 == 0:
            print(f"[Stage 4] Progress: {computed}/{total_computations} ({100*computed/total_computations:.1f}%)")

    print(f"[Stage 4] Computed {len(results)} PIN code × capability combinations")

    # Write results
    if results:
        import pandas as pd

        pdf = pd.DataFrame(results)
        sdf = spark.createDataFrame(pdf)

        write_mode = "overwrite" if overwrite else "append"
        sdf.write.format("delta").mode(write_mode).saveAsTable(target_table)
        print(f"[Stage 4] Wrote {len(results)} rows to {target_table}")

    # Compute statistics
    severity_counts = {"green": 0, "yellow": 0, "red": 0}
    for r in results:
        severity_counts[r["desert_severity"]] += 1

    stats = {
        "total_facilities": len(facilities),
        "unique_pin_codes": len(pin_codes),
        "capabilities_computed": len(capabilities_to_compute),
        "total_lookups": len(results),
        "severity_distribution": severity_counts,
    }

    print(f"[Stage 4] Desert severity distribution: {severity_counts}")

    return stats


def preview_geo_lookup(
    spark,
    table_name: str = "workspace.veritas_dev.geo_lookup",
    capability: str = "emergency_surgery",
) -> None:
    """Preview geo_lookup results for a capability."""
    print(f"\n[Preview] Geo lookup for {capability}:")

    df = spark.table(table_name)
    df = df.filter(df.capability == capability)

    print(f"\nTotal PIN codes with {capability}: {df.count()}")

    # Show severity distribution
    df.groupBy("desert_severity").count().show()

    # Show sample
    df.show(10, truncate=False)
