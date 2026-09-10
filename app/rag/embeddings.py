"""Embeddings provider: Azure OpenAI if configured, else local sentence-transformers,
else a deterministic hash-based embedding so the platform always runs (mock mode / CI)."""
import hashlib
import math
from app.config import settings

_st_model = None


def _hash_embedding(text: str, dim: int = None) -> list[float]:
    dim = dim or settings.pinecone_dimension
    vec = [0.0] * dim
    for i, tok in enumerate(text.lower().split()):
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _get_st_model():
    global _st_model
    if _st_model is None:
        from sentence_transformers import SentenceTransformer
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _st_model


def embed_text(text: str) -> list[float]:
    if settings.mock_mode:
        return _hash_embedding(text)

    if settings.azure_openai_endpoint and settings.azure_openai_api_key and settings.azure_openai_embedding_deployment:
        try:
            from openai import AzureOpenAI
            client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
            )
            resp = client.embeddings.create(model=settings.azure_openai_embedding_deployment, input=text)
            return resp.data[0].embedding
        except Exception:
            pass

    try:
        model = _get_st_model()
        return model.encode(text).tolist()
    except Exception:
        return _hash_embedding(text)


def embed_batch(texts: list[str]) -> list[list[float]]:
    return [embed_text(t) for t in texts]
