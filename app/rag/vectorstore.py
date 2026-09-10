"""Pinecone vector store wrapper with an in-memory fallback for local dev/CI
(so the app never hard-fails without a live Pinecone API key)."""
import uuid
import math
from app.config import settings

_in_memory_store: dict[str, dict[str, dict]] = {}  # namespace -> {id: {values, metadata}}
_pinecone_index = None


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-9
    nb = math.sqrt(sum(y * y for y in b)) or 1e-9
    return dot / (na * nb)


def _get_index():
    global _pinecone_index
    if settings.mock_mode or not settings.pinecone_api_key:
        return None
    if _pinecone_index is not None:
        return _pinecone_index
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=settings.pinecone_api_key)
    existing = [i["name"] for i in pc.list_indexes()]
    if settings.pinecone_index_name not in existing:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.pinecone_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
        )
    _pinecone_index = pc.Index(settings.pinecone_index_name)
    return _pinecone_index


def upsert(namespace: str, vectors: list[dict]) -> int:
    """vectors: [{id, values, metadata}]"""
    index = _get_index()
    if index is None:
        ns = _in_memory_store.setdefault(namespace, {})
        for v in vectors:
            ns[v["id"]] = {"values": v["values"], "metadata": v["metadata"]}
        return len(vectors)
    index.upsert(vectors=[(v["id"], v["values"], v["metadata"]) for v in vectors], namespace=namespace)
    return len(vectors)


def query(namespace: str, vector: list[float], top_k: int = 5, metadata_filter: dict | None = None) -> list[dict]:
    index = _get_index()
    if index is None:
        ns = _in_memory_store.get(namespace, {})
        results = []
        for doc_id, doc in ns.items():
            if metadata_filter and not all(doc["metadata"].get(k) == v for k, v in metadata_filter.items()):
                continue
            score = _cosine(vector, doc["values"])
            results.append({"id": doc_id, "score": score, "metadata": doc["metadata"]})
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    resp = index.query(vector=vector, top_k=top_k, namespace=namespace, filter=metadata_filter, include_metadata=True)
    return [{"id": m.id, "score": m.score, "metadata": m.metadata} for m in resp.matches]


def delete(namespace: str, ids: list[str]) -> None:
    index = _get_index()
    if index is None:
        ns = _in_memory_store.get(namespace, {})
        for i in ids:
            ns.pop(i, None)
        return
    index.delete(ids=ids, namespace=namespace)


def get_status() -> dict:
    index = _get_index()
    if index is None:
        count = sum(len(ns) for ns in _in_memory_store.values())
        return {
            "backend": "In-Memory Cosine Vector DB",
            "index_name": "local-in-memory",
            "dimension": 384,
            "total_vectors": count,
            "pinecone_configured": bool(settings.pinecone_api_key),
            "mock_mode": settings.mock_mode
        }
    try:
        stats = index.describe_index_stats()
        return {
            "backend": "Pinecone Cloud DB",
            "index_name": settings.pinecone_index_name,
            "dimension": settings.pinecone_dimension,
            "total_vectors": getattr(stats, "total_vector_count", 0),
            "pinecone_configured": True,
            "mock_mode": settings.mock_mode
        }
    except Exception:
        count = sum(len(ns) for ns in _in_memory_store.values())
        return {
            "backend": "In-Memory Cosine Vector DB (Fallback)",
            "index_name": settings.pinecone_index_name,
            "dimension": 384,
            "total_vectors": count,
            "pinecone_configured": bool(settings.pinecone_api_key),
            "mock_mode": settings.mock_mode
        }


def new_id() -> str:
    return uuid.uuid4().hex
