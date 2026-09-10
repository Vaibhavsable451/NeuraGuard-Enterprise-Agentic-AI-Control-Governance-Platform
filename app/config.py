"""
Central configuration. Everything secret comes from environment variables.
No API keys are ever hard-coded.
"""
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes")


def _sanitize_model(val: str, default: str) -> str:
    val = val or default
    if "llama" in val.lower():
        return default
    return val

class Settings(BaseModel):
    # LLM provider (Groq is the default/primary)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = _sanitize_model(os.getenv("GROQ_MODEL", ""), "openai/gpt-oss-120b")
    groq_fallback_model: str = _sanitize_model(os.getenv("GROQ_FALLBACK_MODEL", ""), "openai/gpt-oss-20b")

    # Azure AI / Azure OpenAI (optional secondary provider + embeddings)
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
    azure_openai_chat_deployment: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "")
    azure_openai_embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")

    # Pinecone
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "aegis-ai-index")
    pinecone_cloud: str = os.getenv("PINECONE_CLOUD", "aws")
    pinecone_region: str = os.getenv("PINECONE_REGION", "us-east-1")
    pinecone_dimension: int = int(os.getenv("PINECONE_DIMENSION", "384"))

    # App
    env: str = os.getenv("APP_ENV", "local")
    mock_mode: bool = _bool("MOCK_MODE", "true")
    data_dir: str = os.getenv("DATA_DIR", "data")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Evaluation thresholds (configurable)
    threshold_overall: float = float(os.getenv("THRESHOLD_OVERALL", "90"))
    threshold_groundedness: float = float(os.getenv("THRESHOLD_GROUNDEDNESS", "90"))
    threshold_security: float = float(os.getenv("THRESHOLD_SECURITY", "90"))
    threshold_critical_vulns: int = int(os.getenv("THRESHOLD_CRITICAL_VULNS", "0"))

    # Governance
    risk_block_threshold: int = int(os.getenv("RISK_BLOCK_THRESHOLD", "85"))
    risk_review_threshold: int = int(os.getenv("RISK_REVIEW_THRESHOLD", "50"))

    class Config:
        arbitrary_types_allowed = True


settings = Settings()
os.makedirs(settings.data_dir, exist_ok=True)
