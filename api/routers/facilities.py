"""Facilities router — GET /api/facilities/{facility_id}"""
import json
from fastapi import APIRouter, HTTPException
from typing import Optional

from api.mock_data import (
    is_local_mode, MOCK_FACILITIES, MOCK_TRUST_SCORES,
    MOCK_CONTRADICTIONS, MOCK_STRUCTURED
)

router = APIRouter()


def get_spark():
    """Get Spark session - returns None if running locally."""
    if is_local_mode():
        return None
    from pyspark.sql import SparkSession
    return SparkSession.builder.getOrCreate()


@router.get("/facilities/{facility_id}")
async def get_facility(facility_id: str):
    """Get detailed facility information."""

    if is_local_mode():
        # Use mock data
        facility = next((f for f in MOCK_FACILITIES if f["facility_id"] == facility_id), None)
        if not facility:
            raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")

        trust_data = MOCK_TRUST_SCORES.get(facility_id, {})
        structured = MOCK_STRUCTURED.get(facility_id, {})
        contradictions = MOCK_CONTRADICTIONS.get(facility_id, [])

        return {
            **facility,
            "verified_capabilities": structured.get("verified_capabilities", []),
            "staff": structured.get("staff", []),
            "equipment": structured.get("equipment", []),
            "trust_score": trust_data.get("trust_score"),
            "citations": [],
            "contradictions": contradictions,
        }

    # Databricks mode
    try:
        spark = get_spark()
        raw_df = spark.table("workspace.veritas_dev.facilities_raw")
        raw_row = raw_df.filter(raw_df.facility_id == facility_id).collect()

        if not raw_row:
            raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")

        raw = raw_row[0]

        structured_df = spark.table("workspace.veritas_dev.facilities_structured")
        structured_row = structured_df.filter(structured_df.facility_id == facility_id).collect()

        capabilities = []
        staff = []
        equipment = []

        if structured_row:
            s = structured_row[0]
            capabilities = json.loads(s.verified_capabilities_json) if s.verified_capabilities_json else []
            staff = json.loads(s.staff_json) if s.staff_json else []
            equipment = json.loads(s.equipment_json) if s.equipment_json else []

        trust_df = spark.table("workspace.veritas_dev.trust_scores")
        trust_row = trust_df.filter(trust_df.facility_id == facility_id).collect()
        trust_score = trust_row[0].trust_score if trust_row else None

        contras_df = spark.table("workspace.veritas_dev.contradictions")
        contradictions = [
            {
                "claim": c.claim,
                "evidence_gap": c.evidence_gap,
                "trust_impact": c.trust_impact,
                "severity": c.severity,
            }
            for c in contras_df.filter(contras_df.facility_id == facility_id).collect()
        ]

        return {
            "facility_id": raw.facility_id,
            "facility_name": raw.facility_name,
            "state": raw.state,
            "district": raw.district,
            "pin_code": raw.pin_code,
            "latitude": raw.latitude,
            "longitude": raw.longitude,
            "facility_type": raw.facility_type,
            "bed_count": raw.bed_count,
            "verified_capabilities": capabilities,
            "staff": staff,
            "equipment": equipment,
            "trust_score": trust_score,
            "contradictions": contradictions,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/facilities")
async def list_facilities(
    state: Optional[str] = None,
    district: Optional[str] = None,
    facility_type: Optional[str] = None,
    min_trust_score: Optional[int] = None,
    limit: int = 100,
):
    """List facilities with optional filters."""

    if is_local_mode():
        # Use mock data
        facilities = MOCK_FACILITIES.copy()

        if state:
            facilities = [f for f in facilities if f["state"].lower() == state.lower()]
        if district:
            facilities = [f for f in facilities if f["district"].lower() == district.lower()]
        if facility_type:
            facilities = [f for f in facilities if facility_type.lower() in f["facility_type"].lower()]
        if min_trust_score:
            facilities = [
                f for f in facilities
                if MOCK_TRUST_SCORES.get(f["facility_id"], {}).get("trust_score", 0) >= min_trust_score
            ]

        return {
            "count": len(facilities[:limit]),
            "facilities": [
                {
                    "facility_id": f["facility_id"],
                    "facility_name": f["facility_name"],
                    "state": f["state"],
                    "district": f["district"],
                    "facility_type": f["facility_type"],
                    "latitude": f["latitude"],
                    "longitude": f["longitude"],
                    "trust_score": MOCK_TRUST_SCORES.get(f["facility_id"], {}).get("trust_score"),
                }
                for f in facilities[:limit]
            ]
        }

    # Databricks mode
    try:
        spark = get_spark()
        df = spark.table("workspace.veritas_dev.facilities_raw")

        if state:
            df = df.filter(df.state == state)
        if district:
            df = df.filter(df.district == district)
        if facility_type:
            df = df.filter(df.facility_type == facility_type)

        rows = df.limit(limit).collect()

        return {
            "count": len(rows),
            "facilities": [
                {
                    "facility_id": r.facility_id,
                    "facility_name": r.facility_name,
                    "state": r.state,
                    "district": r.district,
                    "facility_type": r.facility_type,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                }
                for r in rows
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
