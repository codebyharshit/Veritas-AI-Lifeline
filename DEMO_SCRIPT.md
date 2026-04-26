# Veritas Demo Script
## Hack-Nation 5th Global AI Hackathon — Databricks Track

**Duration:** 5 minutes
**Presenter:** [Your Name]

---

## OPENING (30 seconds)

> "India has 10,000+ healthcare facilities — but the data is a mess. Facilities self-report capabilities. No one verifies. A hospital claims '24/7 emergency surgery' but their surgeon only works weekdays.

> **Health departments can't plan. Policymakers can't allocate budgets. NGOs don't know where to intervene.**

> We built **Veritas** — an AI-powered verification layer that scores facility trustworthiness and identifies medical deserts."

---

## THE PROBLEM (30 seconds)

**[Show Map Tab - zoom to Bihar/UP region]**

> "See these red zones? These are **medical deserts** — areas where the nearest verified emergency surgery is over 100km away.

> The problem isn't just distance. It's **trust**. Facilities claim capabilities they don't have. There's no verification system."

**Key stats to mention:**
- 10,000 facilities processed
- 56 critical contradictions found
- Some facilities claim 24/7 surgery but have "limited weekend staff"

---

## THE SOLUTION (1 minute)

> "Veritas is a 5-stage AI pipeline built on Databricks:"

**[Show architecture slide or describe verbally]**

| Stage | What it does |
|-------|--------------|
| 1. Ingestion | Load 10,000 facility records into Delta Lake |
| 2. Extraction | LLM extracts structured capabilities from messy text |
| 3. Trust Debate | **3-agent debate** — Advocate, Skeptic, Judge — scores each facility |
| 4. Geographic | Calculate distances to find medical deserts |
| 5. Vector Index | Embeddings for semantic search |

> "The magic is Stage 3 — our **multi-agent trust debate**."

---

## LIVE DEMO: TRUST DEBATE (1.5 minutes)

**[Click on Facility Inspector Tab]**

**[Search for "AIIMS Patna" or facility f003]**

> "Let's look at AIIMS Patna. It claims emergency surgery capability."

**[Show the trust score: 62/100]**

> "See this score? It's not just a number. Click to see the full debate:"

**[Show the debate transcript]**

- **Advocate:** "Premier government hospital with 750 beds, emergency surgery available..."
- **Skeptic:** "WAIT — the notes say 'limited staff on weekends.' That contradicts 24/7 surgery. **Minus 15 points.**"
- **Judge:** "Valid concern. Score: 62/100. Use for weekday emergencies only."

> "Every score is **explainable**. You can trace exactly why a facility got its rating."

---

## LIVE DEMO: NATURAL LANGUAGE QUERY (1 minute)

**[Click on Ask Tab]**

**[Type: "hospitals in Bihar with low trust scores"]**

> "Health administrators can query in natural language. Watch:"

**[Show results]**

> "Instantly surfaces facilities that need inspection or intervention."

**[Type another query: "dialysis facilities in Maharashtra"]**

> "Planning a dialysis expansion program? Query shows existing capacity and trust levels — so you know where gaps exist."

---

## DATABRICKS DIFFERENTIATORS (30 seconds)

> "Why Databricks?"

1. **Delta Lake** — ACID transactions on 10,000 facility records
2. **Unity Catalog** — Governance and lineage tracking
3. **MLflow Tracing** — Every LLM call is traced and auditable
4. **Model Serving** — Llama 3.3 70B for debates, BGE-Large for embeddings

> "This isn't just a demo — it's production-ready architecture."

---

## CLOSING (30 seconds)

> "Veritas turns unverified claims into **trusted, explainable scores**.

> For **State Health Departments:** Identify where to build new facilities.
> For **Policymakers:** See medical deserts and allocate budgets.
> For **NGOs:** Target interventions where they're needed most.
> For **Hospital Networks:** Verify partner facility claims before referrals.

> **The infrastructure layer Indian healthcare administration needs.**"

---

## Q&A PREP

**Likely questions:**

1. **"How accurate is the trust scoring?"**
   > "The 3-agent debate catches contradictions humans miss. We found 56 critical issues in 10,000 facilities — like oncology departments 'under construction' being listed as available."

2. **"How does it scale?"**
   > "Delta Lake handles millions of records. We processed 10,000 in under 30 minutes. The LLM calls are parallelized with rate limiting."

3. **"What's the business model?"**
   > "B2G — State health departments pay for verified facility data and medical desert analysis. B2B — Hospital networks use it for credentialing and referral verification. NGOs license it for intervention planning."

4. **"Why not just use RAG?"**
   > "RAG retrieves. Veritas **verifies**. The multi-agent debate is adversarial — it actively looks for contradictions."

---

## BACKUP DEMO POINTS

If you have extra time:

- **Show MLflow traces** (if Databricks access available)
- **Show a contradiction** — AIIMS Patna's "oncology under construction" vs "oncology available"
- **Show the color-coded map** — green/yellow/red zones
- **Pincode lookup** — type a pincode, see nearest facilities

---

## TECH STACK SUMMARY

| Component | Technology |
|-----------|------------|
| Data Lake | Delta Lake on Databricks |
| LLM | Llama 3.3 70B (Databricks Model Serving) |
| Embeddings | BGE-Large-EN |
| Observability | MLflow Tracing |
| Backend | FastAPI (Vercel) |
| Frontend | Streamlit (Streamlit Cloud) |
| Pipeline | 5-stage Python notebooks |

---

**Good luck! You've got this.**
