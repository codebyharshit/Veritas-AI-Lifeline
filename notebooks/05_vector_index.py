# Databricks notebook source
# MAGIC %md
# MAGIC # Stage 5 — Vector Indexing
# MAGIC
# MAGIC Creates embeddings for semantic search over facility profiles.
# MAGIC Uses databricks-bge-large-en (1024 dimensions).
# MAGIC
# MAGIC **Source:** Section 2.4 Stage 5 of VERITAS_PRD_TRD.md

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

RAW_TABLE = "workspace.veritas_dev.facilities_raw"
STRUCTURED_TABLE = "workspace.veritas_dev.facilities_structured"
TARGET_TABLE = "workspace.veritas_dev.facility_embeddings"
SAMPLE_SIZE = None  # Set to a number for testing
BATCH_SIZE = 20  # Embeddings per API call
OVERWRITE = True

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

import sys
sys.path.insert(0, '/Workspace/Repos/harshitagarwal048@gmail.com/Veritas-AI-Lifeline')

# Force fresh import
modules_to_remove = [key for key in sys.modules.keys() if 'pipelines' in key or 'api' in key]
for mod in modules_to_remove:
    del sys.modules[mod]

from pipelines.vector_index import run_vector_indexing, preview_embeddings, search_similar

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Prerequisites

# COMMAND ----------

structured_count = spark.table(STRUCTURED_TABLE).count()
print(f"Structured facilities: {structured_count}")

if structured_count == 0:
    raise Exception("Stage 2 extraction not complete!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run Vector Indexing

# COMMAND ----------

stats = run_vector_indexing(
    spark=spark,
    raw_table=RAW_TABLE,
    structured_table=STRUCTURED_TABLE,
    target_table=TARGET_TABLE,
    sample_size=SAMPLE_SIZE,
    batch_size=BATCH_SIZE,
    overwrite=OVERWRITE,
)

# COMMAND ----------

# Print summary
print("\n" + "="*60)
print("VECTOR INDEXING SUMMARY")
print("="*60)
print(f"Total facilities: {stats['total_facilities']}")
print(f"Profiles created: {stats['profiles_created']}")
print(f"Embeddings created: {stats['embeddings_created']}")
print(f"Embedding dimensions: {stats['embedding_dimensions']}")
print("="*60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Preview Results

# COMMAND ----------

preview_embeddings(spark, TARGET_TABLE, num_rows=3)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Semantic Search

# COMMAND ----------

# Test search
query = "emergency surgery hospital in Delhi"
print(f"Query: {query}\n")

results = search_similar(spark, query, TARGET_TABLE, top_k=5)

for i, r in enumerate(results, 1):
    print(f"{i}. Similarity: {r['similarity']:.3f}")
    print(f"   {r['profile_text']}")
    print()

# COMMAND ----------

# Try another query
query = "dialysis center with good equipment"
print(f"Query: {query}\n")

results = search_similar(spark, query, TARGET_TABLE, top_k=5)

for i, r in enumerate(results, 1):
    print(f"{i}. Similarity: {r['similarity']:.3f}")
    print(f"   {r['profile_text']}")
    print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC Vector embeddings are ready for semantic search.
# MAGIC
# MAGIC **For production:** Create a Mosaic AI Vector Search endpoint and Delta sync index:
# MAGIC ```sql
# MAGIC CREATE VECTOR SEARCH INDEX facility_search_index
# MAGIC ON workspace.veritas_dev.facility_embeddings
# MAGIC USING DELTA SYNC
# MAGIC WITH (
# MAGIC   EMBEDDING_MODEL = 'databricks-bge-large-en',
# MAGIC   EMBEDDING_SOURCE_COLUMN = 'profile_text'
# MAGIC )
# MAGIC ```
