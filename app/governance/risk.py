"""Explainable 0-100 AI risk scoring + governance decision engine."""
import time
import uuid
from app.governance.detectors import run_all_detectors
from app.governance.policy import evaluate_policies
from app.config import settings
from app.storage import insert
from app.observability.tracing import trace_security_event

WEIGHTS = {
    "pii": 25,
    "prompt_injection": 30,
    "jailbreak": 30,
    "tool_abuse": 35,
    "exfiltration": 35,
    "sensitive_data": 20,
}


def compute_risk_score(detections: dict) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    for key, weight in WEIGHTS.items():
        if detections.get(key, {}).get("detected"):
            score += weight
            matched = detections[key].get("matched") or detections[key].get("types")
            reasons.append(f"{key} detected ({matched})")
    return min(score, 100), reasons


def govern_request(text: str, request_id: str | None = None, source: str = "user_input") -> dict:
    request_id = request_id or f"req_{uuid.uuid4().hex[:10]}"
    detections = run_all_detectors(text)
    score, reasons = compute_risk_score(detections)
    fired_policies = evaluate_policies(detections)

    decision = "APPROVED"
    if any(p["action"] == "BLOCK" for p in fired_policies) or score >= settings.risk_block_threshold:
        decision = "BLOCKED"
    elif any(p["action"] == "REVIEW_REQUIRED" for p in fired_policies) or score >= settings.risk_review_threshold:
        decision = "REVIEW_REQUIRED"

    result = {
        "request_id": request_id,
        "risk_score": score,
        "decision": decision,
        "pii_detected": detections["pii"]["detected"],
        "prompt_injection": detections["prompt_injection"]["detected"],
        "jailbreak_detected": detections["jailbreak"]["detected"],
        "tool_abuse_detected": detections["tool_abuse"]["detected"],
        "exfiltration_detected": detections["exfiltration"]["detected"],
        "policy_violation": bool(fired_policies),
        "fired_policies": fired_policies,
        "reasons": reasons,
        "reason": "; ".join(reasons) if reasons else "No risk indicators detected",
        "source": source,
        "ts": time.time(),
    }
    insert("governance_audit", result)
    if decision != "APPROVED":
        trace_security_event("governance_decision", result)
    return result
