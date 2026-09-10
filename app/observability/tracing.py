"""Lightweight internal Observability Engine (no MLflow)."""
import time
import uuid
from typing import Any
from app.storage import insert, all_records


def _now() -> float:
    return time.time()


def new_trace_id() -> str:
    return f"trace_{uuid.uuid4().hex[:12]}"


def trace_request(request_id: str, endpoint: str, payload: dict[str, Any]) -> None:
    insert("traces_requests", {
        "request_id": request_id, "endpoint": endpoint, "payload": payload, "ts": _now(),
    })


def trace_agent(request_id: str, agent: str, status: str, duration_ms: float, detail: dict[str, Any] | None = None) -> None:
    insert("traces_agents", {
        "request_id": request_id, "agent": agent, "status": status,
        "duration_ms": duration_ms, "detail": detail or {}, "ts": _now(),
    })


def trace_llm_call(agent: str, model: str, prompt: str, response: str, latency_ms: float) -> None:
    insert("traces_llm", {
        "agent": agent, "model": model, "prompt_chars": len(prompt),
        "response_chars": len(response), "latency_ms": latency_ms, "ts": _now(),
    })


def trace_retrieval(query: str, strategy: str, num_results: int, latency_ms: float, success: bool) -> None:
    insert("traces_retrieval", {
        "query": query, "strategy": strategy, "num_results": num_results,
        "latency_ms": latency_ms, "success": success, "ts": _now(),
    })


def trace_tool_call(tool: str, agent: str, success: bool, detail: dict[str, Any] | None = None) -> None:
    insert("traces_tools", {
        "tool": tool, "agent": agent, "success": success, "detail": detail or {}, "ts": _now(),
    })


def trace_error(component: str, error: str, request_id: str | None = None) -> None:
    insert("traces_errors", {"component": component, "error": error, "request_id": request_id, "ts": _now()})


def trace_security_event(kind: str, detail: dict[str, Any]) -> None:
    insert("traces_security", {"kind": kind, "detail": detail, "ts": _now()})


def get_metrics() -> dict[str, Any]:
    requests = all_records("traces_requests")
    agents = all_records("traces_agents")
    llm = all_records("traces_llm")
    retrieval = all_records("traces_retrieval")
    errors = all_records("traces_errors")

    avg_llm_latency = sum(r["latency_ms"] for r in llm) / len(llm) if llm else 0
    failed_agents = [a for a in agents if a["status"] == "failed"]
    failed_retrieval = [r for r in retrieval if not r["success"]]

    return {
        "total_requests": len(requests),
        "total_agent_runs": len(agents),
        "agent_failures": len(failed_agents),
        "total_llm_calls": len(llm),
        "avg_llm_latency_ms": round(avg_llm_latency, 2),
        "total_retrievals": len(retrieval),
        "retrieval_failures": len(failed_retrieval),
        "total_errors": len(errors),
        "security_events": len(all_records("traces_security")),
    }
