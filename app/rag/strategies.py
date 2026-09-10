"""
11 RAG strategies, sharing the common pipeline:
Query -> Retrieval -> Reranking -> Context Filtering -> LLM -> Grounded Response -> Verification
Each strategy customizes one or more stages. No SQL RAG is implemented (per spec).
"""
import time
from app.rag.embeddings import embed_text
from app.rag import vectorstore
from app.rag.reranker import rerank
from app.tools.llm_client import complete
from app.observability.tracing import trace_retrieval
from app.governance.guardrails import check_groundedness

NAMESPACE = "default"


def _retrieve(query, top_k=5, namespace=NAMESPACE, metadata_filter=None):
    start = time.time()
    vec = embed_text(query)
    results = vectorstore.query(namespace, vec, top_k=top_k, metadata_filter=metadata_filter)
    trace_retrieval(query, "vector_search", len(results), (time.time() - start) * 1000, True)
    return results


def _context_filter(results, min_score=0.15):
    return [r for r in results if r.get("rerank_score", r["score"]) >= min_score] or results[:2]


def _build_context(results):
    return "\n\n".join(f"[{i+1}] {r['metadata'].get('text', '')}" for i, r in enumerate(results))


def _generate(query, context, agent, system_extra=""):
    system = ("You are NeuraGuard's grounded RAG assistant. Answer ONLY using the provided context. "
               "If the context is insufficient, say so explicitly. " + system_extra)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nGrounded answer:"
    return complete(prompt, system=system, agent=agent)


def _package(strategy, query, results, answer):
    groundedness = check_groundedness(answer, [r["metadata"].get("text", "") for r in results])
    return {
        "strategy": strategy,
        "query": query,
        "retrieved_documents": [
            {"id": r["id"], "score": round(r["score"], 4), "rerank_score": round(r.get("rerank_score", r["score"]), 4),
             "text": r["metadata"].get("text", ""), "filename": r["metadata"].get("filename")}
            for r in results
        ],
        "context_used": _build_context(results),
        "answer": answer,
        "groundedness": groundedness,
    }


def naive_rag(query):
    results = _retrieve(query, top_k=3)
    context = _build_context(results)
    answer = _generate(query, context, agent="rag_naive")
    return _package("naive", query, results, answer)


def advanced_rag(query):
    rewritten = complete(f"Rewrite this search query to maximize retrieval recall, return only the rewritten query: {query}",
                          agent="rag_advanced")
    results = _retrieve(rewritten.strip() or query, top_k=8)
    results = rerank(query, results)
    results = _context_filter(results)
    answer = _generate(query, _build_context(results), agent="rag_advanced")
    return _package("advanced", query, results, answer)


def hybrid_rag(query):
    dense_results = _retrieve(query, top_k=8)
    query_terms = set(query.lower().split())
    for r in dense_results:
        text_terms = set(r["metadata"].get("text", "").lower().split())
        lexical = len(query_terms & text_terms) / max(len(query_terms), 1)
        r["score"] = 0.6 * r["score"] + 0.4 * lexical
    dense_results.sort(key=lambda r: r["score"], reverse=True)
    results = rerank(query, dense_results)[:5]
    answer = _generate(query, _build_context(results), agent="rag_hybrid")
    return _package("hybrid", query, results, answer)


def agentic_rag(query, max_iterations=2):
    all_results = []
    current_query = query
    for _ in range(max_iterations):
        results = _retrieve(current_query, top_k=4)
        all_results.extend(results)
        decision = complete(
            f"Given the question '{query}' and retrieved snippets: {_build_context(results)[:800]}, "
            "do you have enough information to answer confidently? Reply YES or NO only.",
            agent="rag_agentic",
        )
        if "yes" in decision.lower():
            break
        current_query = complete(f"Generate a follow-up search query to fill remaining gaps for: {query}", agent="rag_agentic")
    dedup = {r["id"]: r for r in all_results}
    results = rerank(query, list(dedup.values()))[:5]
    answer = _generate(query, _build_context(results), agent="rag_agentic")
    return _package("agentic", query, results, answer)


def multi_agent_rag(query):
    results = _retrieve(query, top_k=6)
    results = rerank(query, results)[:4]
    draft = _generate(query, _build_context(results), agent="rag_multi_agent_synth")
    critique = complete(f"Critique this answer for unsupported claims given the question '{query}': {draft}",
                         agent="rag_multi_agent_critic")
    final = complete(f"Revise the answer using this critique. Answer: {draft}\nCritique: {critique}\nRevised grounded answer:",
                      agent="rag_multi_agent_synth")
    return _package("multi_agent", query, results, final)


def graph_rag(query):
    results = _retrieve(query, top_k=6)
    entities = {}
    for r in results:
        text = r["metadata"].get("text", "")
        words = [w.strip(".,;:()").title() for w in text.split() if w[:1].isupper()]
        for w in words:
            entities.setdefault(w, set()).add(r["id"])
    graph_summary = "; ".join(f"{k} (mentioned in {len(v)} chunk(s))" for k, v in list(entities.items())[:15])
    context = _build_context(results) + f"\n\nEntity graph: {graph_summary}"
    answer = _generate(query, context, agent="rag_graph")
    pkg = _package("graph", query, results, answer)
    pkg["entity_graph"] = graph_summary
    return pkg


def multimodal_rag(query, image_caption=None):
    results = _retrieve(query, top_k=5)
    context = _build_context(results)
    if image_caption:
        context += f"\n\n[Image content]: {image_caption}"
    answer = _generate(query, context, agent="rag_multimodal", system_extra="Some context may describe image content.")
    pkg = _package("multimodal", query, results, answer)
    pkg["image_caption_used"] = image_caption
    return pkg


def conversational_rag(query, chat_history=None):
    chat_history = chat_history or []
    if chat_history:
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in chat_history[-6:])
        standalone = complete(
            f"Given this conversation:\n{history_text}\nRewrite the latest user message as a standalone question:\n{query}",
            agent="rag_conversational",
        )
    else:
        standalone = query
    results = _retrieve(standalone.strip() or query, top_k=5)
    answer = _generate(standalone, _build_context(results), agent="rag_conversational")
    pkg = _package("conversational", query, results, answer)
    pkg["standalone_query"] = standalone
    return pkg


def self_rag(query):
    need = complete(f"Does answering '{query}' require external document retrieval? Reply YES or NO.", agent="rag_self")
    if "no" in need.lower():
        answer = complete(query, system="Answer directly and concisely.", agent="rag_self")
        return _package("self_rag", query, [], answer)
    results = _retrieve(query, top_k=5)
    answer = _generate(query, _build_context(results), agent="rag_self")
    reflection = complete(f"Rate 1-10 how well this answer is supported by context, reply with only the number. Answer: {answer}",
                           agent="rag_self")
    pkg = _package("self_rag", query, results, answer)
    pkg["self_reflection_score"] = reflection.strip()
    return pkg


def corrective_rag(query):
    results = _retrieve(query, top_k=5)
    quality = complete(
        f"Rate the relevance of these snippets to the question '{query}' from 0-100, reply with only the number.\n{_build_context(results)[:1000]}",
        agent="rag_corrective",
    )
    try:
        score = float("".join(c for c in quality if c.isdigit() or c == ".") or 0)
    except ValueError:
        score = 0
    if score < 50:
        rewritten = complete(f"Rewrite this query to be more specific and retrievable: {query}", agent="rag_corrective")
        results = _retrieve(rewritten.strip() or query, top_k=5)
    results = rerank(query, results)[:5]
    answer = _generate(query, _build_context(results), agent="rag_corrective")
    pkg = _package("corrective", query, results, answer)
    pkg["initial_relevance_score"] = score
    return pkg


def modular_rag(query, use_hybrid=True, use_rerank=True, use_filter=True):
    results = _retrieve(query, top_k=8)
    if use_hybrid:
        query_terms = set(query.lower().split())
        for r in results:
            text_terms = set(r["metadata"].get("text", "").lower().split())
            lexical = len(query_terms & text_terms) / max(len(query_terms), 1)
            r["score"] = 0.6 * r["score"] + 0.4 * lexical
        results.sort(key=lambda r: r["score"], reverse=True)
    if use_rerank:
        results = rerank(query, results)
    if use_filter:
        results = _context_filter(results)
    results = results[:5]
    answer = _generate(query, _build_context(results), agent="rag_modular")
    pkg = _package("modular", query, results, answer)
    pkg["modules_used"] = {"hybrid": use_hybrid, "rerank": use_rerank, "filter": use_filter}
    return pkg


STRATEGY_REGISTRY = {
    "naive": naive_rag,
    "advanced": advanced_rag,
    "hybrid": hybrid_rag,
    "agentic": agentic_rag,
    "multi_agent": multi_agent_rag,
    "graph": graph_rag,
    "multimodal": multimodal_rag,
    "conversational": conversational_rag,
    "self_rag": self_rag,
    "corrective": corrective_rag,
    "modular": modular_rag,
}


def run_strategy(name, query, **kwargs):
    fn = STRATEGY_REGISTRY.get(name)
    if not fn:
        raise ValueError(f"Unknown RAG strategy: {name}. Available: {list(STRATEGY_REGISTRY)}")
    return fn(query, **kwargs) if kwargs else fn(query)
