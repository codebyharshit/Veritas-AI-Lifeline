"""LLM client for Veritas — Databricks AI Gateway via OpenAI-compatible interface."""
from api.mock_data import is_local_mode

# Single source of truth for model assignments.
MODEL_CHAT = "databricks-meta-llama-3-3-70b-instruct"
MODEL_EMBEDDING = "databricks-bge-large-en"


def get_llm_client():
    """Returns an OpenAI-compatible client pointed at Databricks AI Gateway.

    Returns None in local mode (mock data doesn't need LLM).
    """
    if is_local_mode():
        return None

    # Only import heavy dependencies when actually needed (Databricks mode)
    import mlflow
    from openai import OpenAI
    from databricks.sdk import WorkspaceClient

    # Free MLflow tracing for every chat completion / embedding call.
    try:
        mlflow.openai.autolog()
    except AttributeError:
        try:
            mlflow.autolog()
        except Exception:
            pass  # Tracing not available, continue without it

    w = WorkspaceClient()
    auth = w.config.authenticate()
    token = auth["Authorization"].replace("Bearer ", "")
    return OpenAI(
        api_key=token,
        base_url=f"{w.config.host}/serving-endpoints",
    )
