"""Document Upload -> Parsing -> Chunking -> Metadata -> Embeddings -> Pinecone."""
import time
from app.rag.embeddings import embed_batch
from app.rag import vectorstore
from app.observability.tracing import trace_retrieval

DEFAULT_NAMESPACE = "default"


def parse_document(filename: str, raw_text: str) -> str:
    """Parsing stage. For real PDFs/docx a richer parser would plug in here;
    this handles plain text/markdown natively and is the extension point."""
    return raw_text.strip()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def ingest_document(filename: str, raw_text: str, extra_metadata: dict | None = None,
                     namespace: str = DEFAULT_NAMESPACE) -> dict:
    parsed = parse_document(filename, raw_text)
    chunks = chunk_text(parsed)
    if not chunks:
        return {"filename": filename, "chunks_ingested": 0}

    embeddings = embed_batch(chunks)
    vectors = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        metadata = {
            "filename": filename, "chunk_index": i, "text": chunk,
            "ingested_at": time.time(), **(extra_metadata or {}),
        }
        vectors.append({"id": f"{filename}-{i}-{vectorstore.new_id()[:8]}", "values": emb, "metadata": metadata})

    vectorstore.upsert(namespace, vectors)
    return {"filename": filename, "chunks_ingested": len(vectors), "namespace": namespace}


SEED_DOCUMENTS = [
    {
        "filename": "NeuraGuard_Data_Retention_and_GDPR_Compliance_Policy.pdf",
        "text": (
            "NeuraGuard Enterprise Security & Compliance Policy (SEC-GDPR-2026):\n"
            "1. Data Retention: All customer queries, chat interactions, vector embeddings, and telemetry logs "
            "are strictly retained for a maximum of 90 days. After 90 days, automated purging scripts securely "
            "delete raw inputs and vectors from both primary database storage and Pinecone vector indexes using AES-256 criteria.\n"
            "2. GDPR Article 17 Compliance: Customers maintain the full 'Right to Erasure'. Data deletion requests "
            "submitted to compliance@neuraguard.ai trigger an automated hard-delete across all vector namespaces within 24 hours.\n"
            "3. PII & Sensitive Guardrails: Before any prompt or query is routed to LLM model providers, NeuraGuard "
            "redaction guardrails automatically detect and strip Personally Identifiable Information (PII) including "
            "Social Security Numbers, credit card details, API tokens, passwords, and Protected Health Information (PHI)."
        )
    },
    {
        "filename": "NeuraGuard_FinOps_and_Model_Governance_Policy.pdf",
        "text": (
            "NeuraGuard FinOps & AI Budget Governance Policy (FIN-2026-04):\n"
            "1. Monthly Spending Cap: Total organization API expenditure across Groq, Azure OpenAI, and LLM endpoints "
            "is capped at $500/month. Budget anomaly alerts fire when daily spending exceeds $25.\n"
            "2. Dynamic Model Selection: Routine classification and search queries are routed to cost-efficient models "
            "(openai/gpt-oss-20b). Complex multi-step reasoning queries use openai/gpt-oss-120b.\n"
            "3. Token Optimization: RAG retrieval pipelines enforce reranking and context compression to restrict context "
            "windows to under 1,500 tokens per prompt."
        )
    },
    {
        "filename": "NeuraGuard_Security_Prompt_Injection_Guardrails.pdf",
        "text": (
            "NeuraGuard Security & Guardrails Framework (SEC-INJ-001):\n"
            "1. Prompt Injection Protection: Input streams are scanned against 45 attack vectors including jailbreaks, "
            "system prompt overrides, instruction hijacking, and secret key exfiltration.\n"
            "2. Automated Blocking: Any request exceeding a risk score threshold of 85 is immediately blocked by the "
            "governance engine before agent graph execution."
        )
    },
    {
        "filename": "NeuraGuard_Multi_Agent_Routing_SLA_Specification.pdf",
        "text": (
            "NeuraGuard Multi-Agent Control Plane Specification (AGENT-SLA-v2):\n"
            "1. Agent Architecture: The platform runs an 8-agent LangGraph network comprising Supervisor, Research, RAG, "
            "Data Analysis, Vision, Risk, Compliance, and Verification agents.\n"
            "2. Latency SLAs: End-to-end multi-agent graph execution target SLA is under 2,500ms."
        )
    }
]


def seed_default_documents():
    """Seed initial enterprise documents into vector store if empty."""
    try:
        existing = vectorstore.query(DEFAULT_NAMESPACE, [0.0]*384, top_k=1)
        if not existing:
            for doc in SEED_DOCUMENTS:
                ingest_document(doc["filename"], doc["text"], namespace=DEFAULT_NAMESPACE)
    except Exception as e:
        print(f"Warning: Seed documents failed: {e}")


# Auto-seed on module import
seed_default_documents()
