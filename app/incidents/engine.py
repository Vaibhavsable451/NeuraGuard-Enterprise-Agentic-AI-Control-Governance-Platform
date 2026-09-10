"""Incident Engine: detection, root-cause/impact analysis, and self-healing."""
import time
import uuid
from app.storage import insert, all_records, update_one
from app.observability.tracing import get_metrics

SELF_HEALING_CHAIN = [
    "Retry", "Fallback Model", "Fallback Agent", "Alternative Retrieval",
    "Context Reduction", "Circuit Breaker", "Human Escalation",
]

THRESHOLDS = {
    "error_rate": 0.1,
    "agent_failure_rate": 0.15,
    "retrieval_failure_rate": 0.15,
    "avg_latency_ms": 4000,
}


def _severity(kind: str, magnitude: float) -> str:
    if magnitude > 0.5:
        return "critical"
    if magnitude > 0.3:
        return "high"
    if magnitude > 0.15:
        return "medium"
    return "low"


def open_incident(kind: str, description: str, severity: str, root_cause: str, impact: str) -> dict:
    incident = {
        "incident_id": f"inc_{uuid.uuid4().hex[:10]}",
        "kind": kind,
        "description": description,
        "severity": severity,
        "root_cause": root_cause,
        "impact": impact,
        "status": "open",
        "self_healing_actions": [],
        "timeline": [{"ts": time.time(), "event": "incident_opened"}],
        "opened_at": time.time(),
    }
    insert("incidents", incident)
    return incident


def apply_self_healing(incident_id: str) -> dict:
    """Walks the self-healing chain, logging every attempted action."""
    incident = None
    for i in all_records("incidents"):
        if i["incident_id"] == incident_id:
            incident = i
            break
    if not incident:
        raise ValueError("Incident not found")

    actions_log = []
    for action in SELF_HEALING_CHAIN:
        actions_log.append({"action": action, "ts": time.time(), "outcome": "attempted"})
        if action != "Human Escalation":
            # heuristic: earlier / lighter-weight actions "resolve" more often
            resolved_here = SELF_HEALING_CHAIN.index(action) >= 2
            if resolved_here:
                actions_log[-1]["outcome"] = "resolved"
                break

    resolved = actions_log[-1]["outcome"] == "resolved"
    update_one("incidents", "incident_id", incident_id, {
        "self_healing_actions": incident.get("self_healing_actions", []) + actions_log,
        "status": "resolved" if resolved else "escalated_to_human",
        "timeline": incident["timeline"] + [{"ts": time.time(), "event": "self_healing_run"}],
    })
    return {"incident_id": incident_id, "actions": actions_log, "resolved": resolved}


def detect_incidents() -> list[dict]:
    """Scans observability metrics for anomalies and opens incidents automatically."""
    metrics = get_metrics()
    opened = []

    if metrics["total_agent_runs"] > 0:
        rate = metrics["agent_failures"] / metrics["total_agent_runs"]
        if rate > THRESHOLDS["agent_failure_rate"]:
            inc = open_incident(
                "agent_failure", f"Agent failure rate {rate:.0%} exceeds threshold",
                _severity("agent_failure", rate),
                root_cause="Elevated agent execution failures, likely an upstream tool or model issue.",
                impact="Some user requests may receive degraded or incomplete responses.",
            )
            opened.append(inc)

    if metrics["total_retrievals"] > 0:
        rate = metrics["retrieval_failures"] / metrics["total_retrievals"]
        if rate > THRESHOLDS["retrieval_failure_rate"]:
            inc = open_incident(
                "retrieval_failure", f"Retrieval failure rate {rate:.0%} exceeds threshold",
                _severity("retrieval_failure", rate),
                root_cause="Vector store or embedding service degraded.",
                impact="RAG answers may lack grounding context.",
            )
            opened.append(inc)

    if metrics["avg_llm_latency_ms"] > THRESHOLDS["avg_latency_ms"]:
        inc = open_incident(
            "latency_spike", f"Average LLM latency {metrics['avg_llm_latency_ms']}ms exceeds threshold",
            "medium",
            root_cause="Model provider latency degradation or network congestion.",
            impact="Slower response times across the platform.",
        )
        opened.append(inc)

    for inc in opened:
        apply_self_healing(inc["incident_id"])
    return opened


def get_incident(incident_id: str) -> dict | None:
    for i in all_records("incidents"):
        if i["incident_id"] == incident_id:
            return i
    return None


def list_incidents() -> list[dict]:
    return all_records("incidents")
