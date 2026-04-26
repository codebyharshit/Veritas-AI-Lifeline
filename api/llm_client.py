"""LLM client for Veritas — Databricks AI Gateway via OpenAI-compatible interface."""
import mlflow
from openai import OpenAI
from databricks.sdk import WorkspaceClient

# Free MLflow tracing for every chat completion / embedding call.
# This satisfies the "MLflow tracing as product feature" differentiator.
try:
    mlflow.openai.autolog()
except AttributeError:
    # Older MLflow versions may not have openai.autolog
    try:
        mlflow.autolog()
    except Exception:
        pass  # Tracing not available, continue without it

# Single source of truth for model assignments.
MODEL_CHAT = "databricks-meta-llama-3-3-70b-instruct"
MODEL_EMBEDDING = "databricks-bge-large-en"


def get_llm_client() -> OpenAI:
    """Returns an OpenAI-compatible client pointed at Databricks AI Gateway."""
    w = WorkspaceClient()
    auth = w.config.authenticate()
    token = auth["Authorization"].replace("Bearer ", "")
    return OpenAI(
        api_key=token,
        base_url=f"{w.config.host}/serving-endpoints",
    )
