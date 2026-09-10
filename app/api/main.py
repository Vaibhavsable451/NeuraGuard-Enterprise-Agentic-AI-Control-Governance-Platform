"""AegisAI FastAPI backend. Every endpoint from the spec, wired end-to-end
to the governance, RAG, agent, evaluation, observability, finops, incident
and approval modules."""
import logging
from typing import Any, Dict
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.schemas import (
    ChatRequest,
    RagQueryRequest,
    DocumentUploadRequest,
    AgentRunRequest,
    GovernanceCheckRequest,
    ApprovalCreateRequest,
    ApprovalDecisionRequest,
    EvaluationRunRequest,
)
from app.incidents.engine import (
    detect_incidents,
    list_incidents,
    get_incident,
    open_incident,
    apply_self_healing,
)
from app.config import settings
from app.memory.approval_queue import enqueue_approval, list_pending, list_all, decide
from app.rag.strategies import run_strategy, STRATEGY_REGISTRY
from app.rag.ingestion import ingest_document
from app.rag import vectorstore
from app.agents.graph import run_agentic_workflow
from app.governance.risk import govern_request
from app.governance.guardrails import output_guardrail
from app.storage import all_records
from app.evaluation.evaluator import run_full_evaluation, evaluate_rag, evaluate_agents, evaluate_safety
from app.observability.tracing import get_metrics, trace_request, new_trace_id
from app.finops.cost import get_cost_summary


logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("aegis.api")

app = FastAPI(title="NeuraGuard", description="Enterprise Agentic AI Control & Governance Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to NeuraGuard API Server",
        "docs": "/docs",
        "health": "/health"
    }

class IncidentCreateRequest(BaseModel):
    kind: str
    description: str
    severity: str = "medium"
    root_cause: str
    impact: str

def _governed(text: str, source: str) -> dict:
    assessment = govern_request(text, source=source)
    if assessment["decision"] == "REVIEW_REQUIRED":
        enqueue_approval(text, assessment["risk_score"], [], assessment["reason"])
    return assessment


# --- Health -----------------------------------------------------------
# --- Health -----------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "NeuraGuard",
        "version": "1.0.0"
    }


@app.get("/ready")
def ready():
    return {"status": "ready", "mock_mode": settings.mock_mode}


# --- Chat ---------------------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    request_id = new_trace_id()
    trace_request(request_id, "/chat", {"message": req.message})

    governance = _governed(req.message, source="chat")
    if governance["decision"] == "BLOCKED":
        return {"request_id": request_id, "governance": governance, "response": None,
                "governance_decision": governance["decision"], "risk_score": governance["risk_score"],
                "message": "This request was blocked by NeuraGuard governance policies."}

    result = run_agentic_workflow(req.message, req.chat_history, request_id=request_id)
    filtered = output_guardrail(result.get("final_response", ""))

    return {
        "request_id": request_id,
        "response": filtered["filtered_text"],
        "agent_path": result.get("agent_path", []),
        "sources": result.get("rag_result", {}).get("retrieved_documents", []),
        "citations": [d["filename"] for d in result.get("rag_result", {}).get("retrieved_documents", []) if d.get("filename")],
        "confidence": result.get("verification", {}).get("score"),
        "risk_score": governance["risk_score"],
        "governance_decision": governance["decision"],
        "output_was_redacted": filtered["was_modified"],
    }


# --- RAG ------------------------------------------------------------------
@app.post("/rag/query")
def rag_query(req: RagQueryRequest):
    if req.strategy not in STRATEGY_REGISTRY:
        raise HTTPException(400, f"Unknown strategy. Available: {list(STRATEGY_REGISTRY)}")
    kwargs = {}
    if req.strategy == "conversational" and req.chat_history:
        kwargs["chat_history"] = req.chat_history
    if req.strategy == "multimodal" and req.image_caption:
        kwargs["image_caption"] = req.image_caption
    return run_strategy(req.strategy, req.query, **kwargs)


@app.post("/documents/upload")
def documents_upload(req: DocumentUploadRequest):
    return ingest_document(req.filename, req.text, req.metadata, req.namespace or "default")


@app.get("/rag/status")
def rag_status():
    """Vector store health — backend type, dimension, total vectors."""
    return vectorstore.get_status()


@app.get("/rag/documents")
def rag_documents(namespace: str = "default", top_k: int = 50):
    """List all indexed documents (returns top-k by cosine score against zero-vector)."""
    results = vectorstore.query(namespace, [0.0] * 384, top_k=top_k)
    seen, docs = set(), []
    for r in results:
        fname = r["metadata"].get("filename", "unknown")
        if fname not in seen:
            seen.add(fname)
            docs.append({
                "filename": fname,
                "chunk_index": r["metadata"].get("chunk_index", 0),
                "namespace": namespace,
                "preview": r["metadata"].get("text", "")[:200]
            })
    return {"namespace": namespace, "documents": docs, "total_chunks": len(results)}


# --- Agents -----------------------------------------------------------
@app.post("/agents/run")
def agents_run(req: AgentRunRequest):
    result = run_agentic_workflow(req.query, req.chat_history)
    return {
        "request_id": result.get("request_id"), "agent_path": result.get("agent_path", []),
        "final_response": result.get("final_response"), "errors": result.get("errors", []),
        "risk_assessment": result.get("risk_assessment"), "compliance_assessment": result.get("compliance_assessment"),
        "verification": result.get("verification"),
    }


@app.get("/agents/status")
def agents_status():
    traces = all_records("traces_agents")
    by_agent: Dict[str, Dict[str, Any]] = {}
    for t in traces:
        entry = by_agent.setdefault(t["agent"], {"runs": 0, "failures": 0, "avg_duration_ms": 0.0, "_durations": []})
        entry["runs"] += 1
        if t["status"] == "failed":
            entry["failures"] += 1
        entry["_durations"].append(float(t["duration_ms"]))
    for a in by_agent.values():
        durations: list[float] = a["_durations"]
        a["avg_duration_ms"] = round(sum(durations) / len(durations), 2) if durations else 0.0
        a.pop("_durations", None)
    return {"agents": by_agent}




# --- Governance ---------------------------------------------------------
@app.post("/governance/check")
def governance_check(req: GovernanceCheckRequest):
    return _governed(req.text, req.source or "api")


@app.get("/governance/audit")
def governance_audit():
    return {"audit_log": all_records("governance_audit")}


# --- Evaluation -----------------------------------------------------------
@app.post("/evaluation/run")
def evaluation_run(req: EvaluationRunRequest):
    if req.scope == "rag":
        return evaluate_rag(req.strategy or "naive")
    if req.scope == "agents":
        return evaluate_agents()
    if req.scope == "safety":
        return evaluate_safety()
    return run_full_evaluation()


@app.get("/evaluation/results")
def evaluation_results():
    return {"runs": all_records("evaluation_runs"), "results": all_records("evaluation_results")}


# --- Observability --------------------------------------------------------
@app.get("/observability/traces")
def observability_traces():
    return {
        "requests": all_records("traces_requests")[-100:],
        "agents": all_records("traces_agents")[-100:],
        "llm": all_records("traces_llm")[-100:],
        "retrieval": all_records("traces_retrieval")[-100:],
        "tools": all_records("traces_tools")[-100:],
        "errors": all_records("traces_errors")[-100:],
        "security": all_records("traces_security")[-100:],
    }


@app.get("/observability/metrics")
def observability_metrics():
    return get_metrics()


# --- FinOps -------------------------------------------------------------
@app.get("/finops/cost")
def finops_cost():
    return get_cost_summary()


@app.get("/finops/usage")
def finops_usage():
    return {"usage_records": all_records("finops_usage")[-200:]}


# --- Incidents --------------------------------------------------------
# --- Incidents --------------------------------------------------------

@app.post("/incidents")
def incidents_create(req: IncidentCreateRequest):
    incident = open_incident(
        kind=req.kind,
        description=req.description,
        severity=req.severity,
        root_cause=req.root_cause,
        impact=req.impact,
    )
    return incident


@app.get("/incidents")
def incidents_list():
    detect_incidents()
    return {"incidents": list_incidents()}


@app.get("/incidents/{incident_id}")
def incidents_get(incident_id: str):
    inc = get_incident(incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    return inc


@app.post("/incidents/{incident_id}/self-heal")
def incidents_self_heal(incident_id: str):
    try:
        return apply_self_healing(incident_id)
    except ValueError:
        raise HTTPException(404, "Incident not found")
# --- Approvals ----------------------------------------------------------
@app.post("/approvals")
def approvals_create(req: ApprovalCreateRequest):
    return enqueue_approval(
        req.request_text,
        req.risk_score,
        [],
        req.reason,
    )
@app.get("/approvals")
def approvals_list():
    return {
        "pending": list_pending(),
        "all": list_all(),
    }


@app.post("/approvals/{approval_id}/approve")
def approvals_approve(
    approval_id: str,
    req: ApprovalDecisionRequest,
):
    result = decide(
        approval_id,
        True,
        req.reviewer,
        req.reason,
    )

    if not result:
        raise HTTPException(404, "Approval not found")

    return result


@app.post("/approvals/{approval_id}/reject")
def approvals_reject(
    approval_id: str,
    req: ApprovalDecisionRequest,
):
    result = decide(
        approval_id,
        False,
        req.reviewer,
        req.reason,
    )

    if not result:
        raise HTTPException(404, "Approval not found")

    return result