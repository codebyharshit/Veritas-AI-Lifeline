"""Trust router — GET /api/trust/{facility_id}/debate"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from api.mock_data import is_local_mode, MOCK_TRUST_SCORES, MOCK_FACILITIES

router = APIRouter()


def get_spark():
    if is_local_mode():
        return None
    from pyspark.sql import SparkSession
    return SparkSession.builder.getOrCreate()


@router.get("/trust/{facility_id}/debate")
async def get_trust_debate(facility_id: str):
    """Get the full Advocate/Skeptic/Judge debate transcript for a facility."""

    if is_local_mode():
        # Use mock data
        trust_data = MOCK_TRUST_SCORES.get(facility_id)
        if not trust_data:
            raise HTTPException(
                status_code=404,
                detail=f"No trust debate found for facility {facility_id}"
            )

        facility = next((f for f in MOCK_FACILITIES if f["facility_id"] == facility_id), None)
        facility_name = facility["facility_name"] if facility else "Unknown"

        return {
            "facility_id": facility_id,
            "facility_name": facility_name,
            "trust_score": trust_data["trust_score"],
            "advocate_argument": trust_data["advocate_argument"],
            "skeptic_argument": trust_data["skeptic_argument"],
            "judge_reasoning": trust_data["judge_reasoning"],
            "mlflow_trace_url": None,
            "debated_at": "2026-04-26T10:30:00Z",
        }

    # Databricks mode
    try:
        spark = get_spark()

        trust_df = spark.table("workspace.veritas_dev.trust_scores")
        trust_row = trust_df.filter(trust_df.facility_id == facility_id).collect()

        if not trust_row:
            raise HTTPException(
                status_code=404,
                detail=f"No trust debate found for facility {facility_id}"
            )

        t = trust_row[0]

        raw_df = spark.table("workspace.veritas_dev.facilities_raw")
        raw_row = raw_df.filter(raw_df.facility_id == facility_id).collect()
        facility_name = raw_row[0].facility_name if raw_row else "Unknown"

        mlflow_trace_url = None
        if hasattr(t, 'mlflow_run_id') and t.mlflow_run_id:
            mlflow_trace_url = f"/mlflow/#/experiments/0/runs/{t.mlflow_run_id}"

        return {
            "facility_id": facility_id,
            "facility_name": facility_name,
            "trust_score": t.trust_score,
            "advocate_argument": t.advocate_argument,
            "skeptic_argument": t.skeptic_argument,
            "judge_reasoning": t.judge_reasoning,
            "mlflow_trace_url": mlflow_trace_url,
            "debated_at": str(t.debated_at) if t.debated_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trust/stats")
async def get_trust_stats():
    """Get aggregate trust score statistics."""

    if is_local_mode():
        # Use mock data
        scores = [t["trust_score"] for t in MOCK_TRUST_SCORES.values()]
        if not scores:
            return {"total_facilities": 0}

        avg_score = sum(scores) / len(scores)
        return {
            "total_facilities": len(scores),
            "average_score": round(avg_score, 1),
            "min_score": min(scores),
            "max_score": max(scores),
            "stddev": None,
            "distribution": {
                "40-59": len([s for s in scores if 40 <= s < 60]),
                "60-79": len([s for s in scores if 60 <= s < 80]),
                "80-100": len([s for s in scores if 80 <= s <= 100]),
            }
        }

    # Databricks mode
    try:
        spark = get_spark()
        trust_df = spark.table("workspace.veritas_dev.trust_scores")

        from pyspark.sql import functions as F

        stats = trust_df.agg(
            F.count("*").alias("total"),
            F.avg("trust_score").alias("avg_score"),
            F.min("trust_score").alias("min_score"),
            F.max("trust_score").alias("max_score"),
            F.stddev("trust_score").alias("stddev_score"),
        ).collect()[0]

        return {
            "total_facilities": stats.total,
            "average_score": round(stats.avg_score, 1) if stats.avg_score else None,
            "min_score": stats.min_score,
            "max_score": stats.max_score,
            "stddev": round(stats.stddev_score, 1) if stats.stddev_score else None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
