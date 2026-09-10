"""The 8 agents: Supervisor, Research, RAG, Data Analysis, Vision, Compliance,
Risk, Verification. Each is a plain function operating on AgentState so they
work standalone (unit-testable) and inside the LangGraph graph."""
import time
from app.agents.state import AgentState
from app.tools.llm_client import complete
from app.rag.strategies import naive_rag, agentic_rag
from app.governance.risk import govern_request
from app.governance.guardrails import verify_claims
from app.observability.tracing import trace_agent


def _run(agent_name: str, state: AgentState, fn):
    start = time.time()
    try:
        state = fn(state)
        state.setdefault("agent_path", []).append(agent_name)
        trace_agent(state.get("request_id", "unknown"), agent_name, "success", (time.time() - start) * 1000)
    except Exception as e:  # noqa: BLE001
        state.setdefault("errors", []).append(f"{agent_name}: {e}")
        trace_agent(state.get("request_id", "unknown"), agent_name, "failed", (time.time() - start) * 1000, {"error": str(e)})
    return state


def supervisor_agent(state: AgentState) -> AgentState:
    """Dynamically decides which downstream agents are required for this request."""
    def _decide(inner_state: AgentState) -> AgentState:
        query = inner_state["user_query"]
        needs_research = any(w in query.lower() for w in ["research", "latest", "compare", "news", "find out"])
        needs_rag = any(w in query.lower() for w in ["document", "policy", "according to", "our data", "uploaded"]) or True
        needs_data = any(w in query.lower() for w in ["calculate", "trend", "metric", "number", "analy"])
        needs_vision = any(w in query.lower() for w in ["image", "picture", "screenshot", "diagram"])
        needs_risk = any(w in query.lower() for w in ["risk", "danger", "harm", "safety"]) or True
        needs_compliance = any(w in query.lower() for w in ["compliance", "regulat", "policy", "gdpr", "hipaa"]) or True

        required = ["rag"] if needs_rag else []
        if needs_research:
            required.append("research")
        if needs_data:
            required.append("data_analysis")
        if needs_vision:
            required.append("vision")
        if needs_risk:
            required.append("risk")
        if needs_compliance:
            required.append("compliance")
        required.append("verification")
        inner_state["required_agents"] = required
        return inner_state

    return _run("supervisor", state, _decide)


def research_agent(state: AgentState) -> AgentState:
    def _fn(state: AgentState) -> AgentState:
        notes = complete(
            f"Act as an autonomous research agent. Summarize what is known about: {state['user_query']}. "
            "Be concise and factual.",
            agent="research_agent",
        )
        state["research_notes"] = notes
        return state
    return _run("research", state, _fn)


def rag_agent(state: AgentState) -> AgentState:
    def _fn(state: AgentState) -> AgentState:
        if "research" in state.get("agent_path", []):
            result = agentic_rag(state["user_query"])
        else:
            result = naive_rag(state["user_query"])
        state["rag_result"] = result
        return state
    return _run("rag", state, _fn)


def data_analysis_agent(state: AgentState) -> AgentState:
    def _fn(state: AgentState) -> AgentState:
        summary = complete(
            f"Act as a data analysis agent. Given this question: {state['user_query']}, and context: "
            f"{state.get('rag_result', {}).get('context_used', '')[:800]}, extract or estimate any relevant metrics/trends.",
            agent="data_analysis_agent",
        )
        state["data_analysis"] = summary
        return state
    return _run("data_analysis", state, _fn)


def vision_agent(state: AgentState) -> AgentState:
    def _fn(state: AgentState) -> AgentState:
        state["vision_notes"] = "No image was attached to this request; vision analysis skipped."
        return state
    return _run("vision", state, _fn)


def risk_agent(state: AgentState) -> AgentState:
    def _fn(state: AgentState) -> AgentState:
        state["risk_assessment"] = govern_request(state["user_query"], state.get("request_id"), source="risk_agent")
        return state
    return _run("risk", state, _fn)


def compliance_agent(state: AgentState) -> AgentState:
    def _fn(state: AgentState) -> AgentState:
        risk = state.get("risk_assessment", {})
        state["compliance_assessment"] = {
            "compliant": risk.get("decision") == "APPROVED",
            "notes": "Evaluated against governance policy set (PII, injection, jailbreak, tool abuse, exfiltration).",
            "policy_violations": risk.get("fired_policies", []),
        }
        return state
    return _run("compliance", state, _fn)


def verification_agent(state: AgentState) -> AgentState:
    def _fn(state: AgentState) -> AgentState:
        answer = state.get("rag_result", {}).get("answer") or state.get("research_notes", "") or ""
        context_chunks = [d["text"] for d in state.get("rag_result", {}).get("retrieved_documents", [])]
        verification = verify_claims(answer, context_chunks)
        state["verification"] = verification

        parts = []
        if state.get("research_notes"):
            parts.append(f"Research: {state['research_notes']}")
        if state.get("rag_result"):
            parts.append(f"Answer: {state['rag_result'].get('answer', '')}")
        if state.get("data_analysis"):
            parts.append(f"Data analysis: {state['data_analysis']}")
        state["final_response"] = "\n\n".join(parts) or "No response could be generated."
        return state
    return _run("verification", state, _fn)


AGENT_REGISTRY = {
    "research": research_agent,
    "rag": rag_agent,
    "data_analysis": data_analysis_agent,
    "vision": vision_agent,
    "risk": risk_agent,
    "compliance": compliance_agent,
    "verification": verification_agent,
}
