"""Cross-encoder-style reranking (lexical-overlap heuristic; deterministic and
network-free). Swap in a real cross-encoder model in production if desired."""

def rerank(query: str, results: list[dict]) -> list[dict]:
    query_terms = set(query.lower().split())
    for r in results:
        text = r["metadata"].get("text", "")
        text_terms = set(text.lower().split())
        overlap = len(query_terms & text_terms)
        r["rerank_score"] = r["score"] * 0.7 + (overlap / max(len(query_terms), 1)) * 0.3
    return sorted(results, key=lambda r: r["rerank_score"], reverse=True)
