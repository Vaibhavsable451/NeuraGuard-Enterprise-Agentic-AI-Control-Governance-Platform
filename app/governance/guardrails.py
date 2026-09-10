"""Input/output guardrails: hallucination detection, groundedness checking,
claim verification, sensitive-info filtering on outputs."""
import re
from app.governance.detectors import run_all_detectors, PII_PATTERNS


def check_groundedness(answer: str, context_chunks: list[str]) -> dict:
    """Heuristic groundedness: fraction of answer sentences whose key terms
    appear in the retrieved context."""
    if not context_chunks:
        return {"score": 0.0, "grounded": False, "reason": "No context was retrieved to ground this answer."}

    context_terms = set(" ".join(context_chunks).lower().split())
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
    if not sentences:
        return {"score": 1.0, "grounded": True, "reason": "Empty answer."}

    supported = 0
    for s in sentences:
        terms = set(s.lower().split())
        overlap = len(terms & context_terms) / max(len(terms), 1)
        if overlap >= 0.2:
            supported += 1
    score = supported / len(sentences)
    return {"score": round(score, 2), "grounded": score >= 0.5,
             "reason": f"{supported}/{len(sentences)} sentences supported by retrieved context."}


def input_guardrail(text: str) -> dict:
    detections = run_all_detectors(text)
    blocked = detections["jailbreak"]["detected"] or detections["prompt_injection"]["detected"]
    return {"allowed": not blocked, "detections": detections}


def output_guardrail(text: str) -> dict:
    """Redact detected PII/secrets from a model output before it reaches the user."""
    redacted = text
    for kind, pattern in PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{kind.upper()}]", redacted)
    changed = redacted != text
    return {"filtered_text": redacted, "was_modified": changed}


def verify_claims(answer: str, context_chunks: list[str]) -> dict:
    groundedness = check_groundedness(answer, context_chunks)
    hallucination_risk = "LOW" if groundedness["score"] >= 0.7 else ("MEDIUM" if groundedness["score"] >= 0.4 else "HIGH")
    return {**groundedness, "hallucination_risk": hallucination_risk}
