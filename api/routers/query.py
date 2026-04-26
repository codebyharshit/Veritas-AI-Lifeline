"""Query router — POST /api/query for natural language facility search."""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import mlflow

from api.mock_data import is_local_mode, MOCK_FACILITIES, MOCK_TRUST_SCORES, MOCK_STRUCTURED

router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    max_results: int = Field(default=5, ge=1, le=20)


class FacilityResult(BaseModel):
    facility_id: str
    facility_name: str
    state: str
    district: str
    distance_km: Optional[float] = None
    trust_score: Optional[int] = None
    justification: str
    matching_capabilities: list[str] = []


class QueryResponse(BaseModel):
    query: str
    results: list[FacilityResult]
    mlflow_trace_id: Optional[str] = None


def get_spark():
    if is_local_mode():
        return None
    from pyspark.sql import SparkSession
    return SparkSession.builder.getOrCreate()


def get_llm_client():
    from api.llm_client import get_llm_client as get_client
    return get_client()


INTENT_PROMPT = """Parse this healthcare facility query into structured search parameters.

Query: {query}

Extract:
- capabilities: list of clinical services needed (e.g. ["emergency surgery", "dialysis"])
- location_state: state name if mentioned (or null)
- location_district: district name if mentioned (or null)
- max_distance_km: maximum distance if mentioned (or null)
- min_trust_score: minimum trust score if mentioned (or null)

Return ONLY this JSON:
{{"capabilities": [...], "location_state": "...", "location_district": "...", "max_distance_km": null, "min_trust_score": null}}"""


EXPLAIN_PROMPT = """Write a one-sentence justification for why this facility matches the query.

Query: {query}
Facility: {facility_name} in {district}, {state}
Capabilities: {capabilities}
Trust Score: {trust_score}

Return only the one-sentence justification, no preamble."""


@router.post("/query", response_model=QueryResponse)
async def query_facilities(request: QueryRequest):
    """
    Natural language query for facilities.

    This runs the Stage 6 LangGraph workflow:
    1. Parse intent
    2. Retrieve candidates
    3. Filter by constraints
    4. Rank by trust + relevance
    5. Critic review
    6. Generate explanations
    """
    if is_local_mode():
        # Simple keyword-based search for local mode
        query_lower = request.query.lower()

        # Score each facility by relevance
        scored_facilities = []
        for f in MOCK_FACILITIES:
            score = 0
            fid = f["facility_id"]
            trust_data = MOCK_TRUST_SCORES.get(fid, {})
            structured = MOCK_STRUCTURED.get(fid, {})

            # Check if location matches
            if f["state"].lower() in query_lower or f["district"].lower() in query_lower:
                score += 30

            # Check if facility type matches
            if f["facility_type"].lower() in query_lower:
                score += 20

            # Check capabilities
            caps = structured.get("verified_capabilities", [])
            cap_names = [c.get("capability", "").lower() for c in caps]
            matching_caps = []
            for cap in cap_names:
                if cap in query_lower or any(word in cap for word in query_lower.split()):
                    score += 25
                    matching_caps.append(cap.title())

            # Check unstructured notes
            notes = f.get("unstructured_notes", "").lower()
            for word in query_lower.split():
                if len(word) > 3 and word in notes:
                    score += 5

            # Factor in trust score
            trust_score = trust_data.get("trust_score", 50)
            score += trust_score // 10

            if score > 0:
                scored_facilities.append({
                    "facility": f,
                    "score": score,
                    "trust_score": trust_score,
                    "matching_caps": matching_caps,
                })

        # Sort by score descending
        scored_facilities.sort(key=lambda x: x["score"], reverse=True)

        # Build results
        results = []
        for item in scored_facilities[:request.max_results]:
            f = item["facility"]
            results.append(FacilityResult(
                facility_id=f["facility_id"],
                facility_name=f["facility_name"],
                state=f["state"],
                district=f["district"],
                trust_score=item["trust_score"],
                justification=f"Matched query '{request.query}' with relevance score {item['score']}. Trust score: {item['trust_score']}/100.",
                matching_capabilities=item["matching_caps"],
            ))

        return QueryResponse(
            query=request.query,
            results=results,
            mlflow_trace_id=None,
        )

    # Databricks mode
    try:
        spark = get_spark()
        client = get_llm_client()

        # Start MLflow trace
        with mlflow.start_run() as run:
            mlflow_trace_id = run.info.run_id

            # Step 1: Parse intent
            from api.llm_client import MODEL_CHAT

            intent_response = client.chat.completions.create(
                model=MODEL_CHAT,
                messages=[{"role": "user", "content": INTENT_PROMPT.format(query=request.query)}],
                temperature=0.1,
                max_tokens=200,
            )

            intent_raw = intent_response.choices[0].message.content

            # Parse intent JSON
            import re
            intent_json = re.search(r'\{.*\}', intent_raw, re.DOTALL)
            if intent_json:
                intent = json.loads(intent_json.group())
            else:
                intent = {"capabilities": [], "location_state": None, "location_district": None}

            # Step 2 & 3: Retrieve and filter
            df = spark.table("workspace.veritas_dev.facilities_raw")

            # Apply location filters
            if intent.get("location_state"):
                df = df.filter(df.state.contains(intent["location_state"]))
            if intent.get("location_district"):
                df = df.filter(df.district.contains(intent["location_district"]))

            # Join with trust scores
            trust_df = spark.table("workspace.veritas_dev.trust_scores")
            df = df.join(trust_df, on="facility_id", how="left")

            # Join with structured data for capability matching
            structured_df = spark.table("workspace.veritas_dev.facilities_structured")
            df = df.join(structured_df, on="facility_id", how="left")

            # Apply min trust score filter
            if intent.get("min_trust_score"):
                df = df.filter(df.trust_score >= intent["min_trust_score"])

            # Step 4: Rank by trust score (descending)
            df = df.orderBy(df.trust_score.desc())

            # Get top candidates
            candidates = df.limit(request.max_results * 2).collect()

            # Step 5 & 6: Generate explanations for top results
            results = []
            for row in candidates[:request.max_results]:
                # Parse capabilities
                caps = []
                if row.verified_capabilities_json:
                    caps_data = json.loads(row.verified_capabilities_json)
                    caps = [c["capability"] for c in caps_data]

                # Generate explanation
                explain_response = client.chat.completions.create(
                    model=MODEL_CHAT,
                    messages=[{"role": "user", "content": EXPLAIN_PROMPT.format(
                        query=request.query,
                        facility_name=row.facility_name,
                        district=row.district,
                        state=row.state,
                        capabilities=", ".join(caps[:5]) if caps else "Not specified",
                        trust_score=row.trust_score or "Not scored",
                    )}],
                    temperature=0.3,
                    max_tokens=100,
                )

                justification = explain_response.choices[0].message.content.strip()

                results.append(FacilityResult(
                    facility_id=row.facility_id,
                    facility_name=row.facility_name,
                    state=row.state,
                    district=row.district,
                    trust_score=row.trust_score,
                    justification=justification,
                    matching_capabilities=caps[:5],
                ))

            return QueryResponse(
                query=request.query,
                results=results,
                mlflow_trace_id=mlflow_trace_id,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
