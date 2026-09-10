from app.rag.ingestion import ingest_document, chunk_text
from app.rag.strategies import naive_rag, hybrid_rag, modular_rag


def test_chunking_produces_chunks():
    chunks = chunk_text("word " * 1000, chunk_size=800, overlap=100)
    assert len(chunks) > 1


def test_ingest_and_naive_rag():
    ingest_document("policy.txt", "Our data retention policy requires deleting logs after 90 days.", namespace="test_ns")
    result = naive_rag("What is our data retention policy?")
    assert "strategy" in result
    assert result["strategy"] == "naive"
    assert isinstance(result["answer"], str)


def test_hybrid_rag_runs():
    result = hybrid_rag("data retention")
    assert result["strategy"] == "hybrid"


def test_modular_rag_respects_flags():
    result = modular_rag("data retention", use_hybrid=False, use_rerank=False, use_filter=False)
    assert result["modules_used"] == {"hybrid": False, "rerank": False, "filter": False}
