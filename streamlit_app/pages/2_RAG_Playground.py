import streamlit as st
from utils import page_setup, api_post, api_get

st.set_page_config(
    page_title="RAG Playground — NeuraGuard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
page_setup("RAG Playground", "🔍")

st.markdown("## 🔍 RAG Strategy Playground")
st.caption("Test and compare all 11 enterprise RAG retrieval pipelines in real-time.")

# ─── Vector Store Status Bar ─────────────────────────────────────────────────
vs = api_get("/rag/status") or {}
backend   = vs.get("backend", "Unknown")
index_nm  = vs.get("index_name", "–")
dim       = vs.get("dimension", "–")
total_vec = vs.get("total_vectors", 0)
pinecone_ok = vs.get("pinecone_configured", False)
mock_mode   = vs.get("mock_mode", True)

if mock_mode or not pinecone_ok:
    badge_color = "#f59e0b"   # amber  – local / mock
    badge_text  = "🟡 In-Memory (Mock Mode)"
elif "Pinecone" in backend:
    badge_color = "#10b981"   # green  – live Pinecone
    badge_text  = "🟢 Pinecone Live"
else:
    badge_color = "#3b82f6"   # blue   – some real backend
    badge_text  = "🔵 Connected"

st.markdown(f"""
<div style="display:flex;gap:14px;align-items:center;background:rgba(16,185,129,0.07);
            border:1px solid rgba(16,185,129,0.2);border-radius:12px;
            padding:10px 18px;margin-bottom:14px;">
  <span style="font-size:0.82rem;color:{badge_color};font-weight:700;">{badge_text}</span>
  <span style="color:#64748b;font-size:0.78rem;">|</span>
  <span style="color:#94a3b8;font-size:0.82rem;">Backend: <b style="color:#e2e8f0;">{backend}</b></span>
  <span style="color:#64748b;font-size:0.78rem;">|</span>
  <span style="color:#94a3b8;font-size:0.82rem;">Index: <b style="color:#e2e8f0;">{index_nm}</b></span>
  <span style="color:#64748b;font-size:0.78rem;">|</span>
  <span style="color:#94a3b8;font-size:0.82rem;">Dim: <b style="color:#e2e8f0;">{dim}</b></span>
  <span style="color:#64748b;font-size:0.78rem;">|</span>
  <span style="color:#94a3b8;font-size:0.82rem;">Vectors Indexed: <b style="color:#10b981;">{total_vec}</b></span>
</div>
""", unsafe_allow_html=True)

# ─── Document Ingestion ───────────────────────────────────────────────────────
with st.expander("📤 Ingest New Document / Policy into Vector DB", expanded=False):
    st.caption("Upload text or paste raw documents — they will be chunked, embedded, and indexed.")
    col_u1, col_u2 = st.columns([1, 2])
    with col_u1:
        doc_filename  = st.text_input("Document Name", "Company_Policy_2026.txt")
        doc_namespace = st.text_input("Namespace", "default")
    with col_u2:
        doc_text = st.text_area(
            "Document Content",
            "Enterprise Data Retention Policy: All logs, chat histories, and vector embeddings "
            "must be retained for 90 days, after which automated AES-256 purging scripts delete "
            "customer telemetry in compliance with GDPR Article 17.",
            height=100,
        )

    if st.button("📥 Ingest Document into Vector Store", key="btn_ingest"):
        with st.spinner("Parsing, chunking, and embedding document…"):
            ingest_resp = api_post("/documents/upload", {
                "filename":  doc_filename,
                "text":      doc_text,
                "metadata":  {"source": "rag_playground_upload"},
                "namespace": doc_namespace,
            })
        if ingest_resp:
            chunks = ingest_resp.get("chunks_ingested", 1)
            st.success(f"✅ '{doc_filename}' ingested! {chunks} chunk(s) stored in **{doc_namespace}** namespace.")
            st.rerun()
        else:
            st.error("❌ Ingestion failed. Is the backend running?")

# ─── Document Library ────────────────────────────────────────────────────────
with st.expander("📚 Indexed Document Library", expanded=(total_vec > 0)):
    lib_ns = st.text_input("Namespace to inspect", "default", key="lib_ns")
    if st.button("🔄 Refresh Library", key="btn_refresh_lib"):
        st.session_state["doc_lib_cache"] = None

    if "doc_lib_cache" not in st.session_state or st.session_state.get("doc_lib_cache") is None:
        st.session_state["doc_lib_cache"] = api_get(f"/rag/documents?namespace={lib_ns}&top_k=50")

    lib_data = st.session_state.get("doc_lib_cache") or {}
    lib_docs  = lib_data.get("documents", [])
    lib_total = lib_data.get("total_chunks", 0)

    if not lib_docs:
        st.info("No documents indexed yet in this namespace. Ingest one above ☝️")
    else:
        st.caption(f"**{lib_total}** total chunks across **{len(lib_docs)}** unique documents.")
        for i, doc in enumerate(lib_docs, 1):
            with st.expander(f"📄 {doc['filename']}  (chunk #{doc.get('chunk_index', 0)})"):
                st.markdown(f"```\n{doc.get('preview', '(empty)')}\n```")

st.divider()

# ─── Strategy Selector + Query ───────────────────────────────────────────────
STRATEGIES = [
    "naive", "advanced", "hybrid", "agentic", "multi_agent", "graph",
    "multimodal", "conversational", "self_rag", "corrective", "modular",
]
STRATEGY_DESC = {
    "naive":         "Basic similarity search with top-k retrieval.",
    "advanced":      "Semantic chunking + reranker pipeline.",
    "hybrid":        "Dense + sparse (BM25) fusion retrieval.",
    "agentic":       "LLM-driven query planning and retrieval.",
    "multi_agent":   "Multiple specialized retrieval agents.",
    "graph":         "Graph-traversal knowledge retrieval.",
    "multimodal":    "Text + image caption retrieval.",
    "conversational":"History-aware contextual retrieval.",
    "self_rag":      "Self-critiquing RAG with reflection loop.",
    "corrective":    "Corrective RAG with web fallback.",
    "modular":       "Composable modular RAG pipeline.",
}

col_left, col_right = st.columns([1, 2])
with col_left:
    strategy = st.selectbox("RAG Strategy", STRATEGIES, index=2)   # default: hybrid
    st.markdown(f"""
    <div class="glass glass-blue" style="padding:10px 14px;margin-top:4px;">
        <span style="color:#94a3b8;font-size:0.85rem;">{STRATEGY_DESC.get(strategy, '')}</span>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    query = st.text_area(
        "Query",
        "What does our policy say about data retention and GDPR compliance?",
        height=90,
    )
    run = st.button("🚀 Run Benchmark", key="btn_run_rag")

# ─── Run RAG Pipeline ────────────────────────────────────────────────────────
if run:
    with st.spinner(f"Running **{strategy}** pipeline…"):
        result = api_post("/rag/query", {"query": query, "strategy": strategy})

    if not result:
        st.error("❌ No response from backend. Make sure the FastAPI server is running on port 8000.")
    else:
        st.divider()

        # Answer block
        raw_ans = result.get("answer", "No answer returned.")
        if raw_ans.startswith("Answer: "):
            raw_ans = raw_ans[8:].strip()

        st.markdown("### 💡 Answer")
        st.markdown(f"""
        <div class="glass glass-green" style="font-size:1.02rem;line-height:1.7;white-space:pre-wrap;">
{raw_ans}
        </div>
        """, unsafe_allow_html=True)

        # Metrics row
        g      = result.get("groundedness", {})
        score  = g.get("score", 0.0)
        grounded = g.get("grounded", False)
        docs_ret  = result.get("retrieved_documents", [])

        c1, c2, c3 = st.columns(3)
        c1.metric("Groundedness Score",
                  f"{score:.2f}" if isinstance(score, (float, int)) else "–")
        c2.metric("Factually Grounded",
                  "✅ Yes" if grounded else "⚠️ No")
        c3.metric("Docs Retrieved", len(docs_ret))

        if total_vec == 0 and not grounded:
            st.warning(
                "⚠️ **Groundedness is 0 because your vector store is empty.**  \n"
                "Use the **Ingest Document** panel above to add policies/PDFs, then re-run the query."
            )

        # Retrieved documents
        if docs_ret:
            st.markdown("### 📄 Retrieved Documents")
            for i, d in enumerate(docs_ret, 1):
                fname = d.get("filename", "doc")
                sim   = d.get("score", 0.0)
                with st.expander(f"Document #{i} — {fname}  |  similarity: {sim:.3f}"):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(d.get("text", "")[:500])
                    with col_b:
                        st.metric("Similarity",   f"{sim:.3f}")
                        st.metric("Rerank Score",  f"{d.get('rerank_score', 0):.3f}")
        else:
            st.info(
                "No documents were retrieved for this query.  \n"
                "**Tip:** Ingest at least one document into the vector store first."
            )

        # Context sent to LLM
        with st.expander("🧩 Context Sent to LLM"):
            ctx = result.get("context_used", "(empty)")
            st.code(ctx if ctx else "(No context — vector store is empty)", language="markdown")
