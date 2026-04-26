# Databricks notebook source
# MAGIC %md
# MAGIC # Stage 4 — Geographic Computation
# MAGIC
# MAGIC Computes nearest verified facility for each PIN code × capability.
# MAGIC Powers the choropleth map showing medical desert severity.
# MAGIC
# MAGIC **Source:** Section 2.4 Stage 4 of VERITAS_PRD_TRD.md

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

RAW_TABLE = "workspace.veritas_dev.facilities_raw"
STRUCTURED_TABLE = "workspace.veritas_dev.facilities_structured"
TRUST_TABLE = "workspace.veritas_dev.trust_scores"
TARGET_TABLE = "workspace.veritas_dev.geo_lookup"
MIN_TRUST_SCORE = 60  # Minimum trust score to be "verified"
MIN_CONFIDENCE = 0.7  # Minimum capability confidence
OVERWRITE = True

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

import sys
sys.path.insert(0, '/Workspace/Repos/harshitagarwal048@gmail.com/Veritas-AI-Lifeline')

# Force fresh import
modules_to_remove = [key for key in sys.modules.keys() if 'pipelines' in key]
for mod in modules_to_remove:
    del sys.modules[mod]

from pipelines.geographic import run_geographic_computation, preview_geo_lookup

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Prerequisites

# COMMAND ----------

# Check that extraction is complete
structured_count = spark.table(STRUCTURED_TABLE).count()
print(f"Structured facilities: {structured_count}")

if structured_count == 0:
    raise Exception("Stage 2 extraction not complete!")

# Check if trust scores exist
try:
    trust_count = spark.table(TRUST_TABLE).count()
    print(f"Trust scores: {trust_count}")
except:
    print("Trust scores not yet computed (will use defaults)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run Geographic Computation

# COMMAND ----------

stats = run_geographic_computation(
    spark=spark,
    raw_table=RAW_TABLE,
    structured_table=STRUCTURED_TABLE,
    trust_table=TRUST_TABLE,
    target_table=TARGET_TABLE,
    min_trust_score=MIN_TRUST_SCORE,
    min_confidence=MIN_CONFIDENCE,
    overwrite=OVERWRITE,
)

# COMMAND ----------

# Print summary
print("\n" + "="*60)
print("GEOGRAPHIC COMPUTATION SUMMARY")
print("="*60)
print(f"Total facilities: {stats['total_facilities']}")
print(f"Unique PIN codes: {stats['unique_pin_codes']}")
print(f"Capabilities computed: {stats['capabilities_computed']}")
print(f"Total lookups: {stats['total_lookups']}")
print(f"\nDesert severity distribution:")
for severity, count in stats['severity_distribution'].items():
    pct = 100 * count / stats['total_lookups'] if stats['total_lookups'] > 0 else 0
    print(f"  {severity}: {count} ({pct:.1f}%)")
print("="*60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Preview Results

# COMMAND ----------

# Preview emergency surgery
preview_geo_lookup(spark, TARGET_TABLE, "emergency_surgery")

# COMMAND ----------

# Preview dialysis
preview_geo_lookup(spark, TARGET_TABLE, "dialysis")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Medical Desert Analysis

# COMMAND ----------

# Show the worst medical deserts (red zones)
df = spark.table(TARGET_TABLE)

print("PIN codes with worst access (>100km to any verified facility):")
red_zones = df.filter(df.desert_severity == "red") \
    .groupBy("pin_code") \
    .count() \
    .orderBy("count", ascending=False)

red_zones.show(20)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC Geographic lookup is now ready for the choropleth map.
# MAGIC Proceed to Stage 5 (Vector Indexing) for semantic search.
