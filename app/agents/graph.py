"""LangGraph StateGraph wiring the Supervisor + 7 specialist agents with
dynamic conditional routing (never forces every request through every agent)."""
import uuid
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.agents import (
    supervisor_agent, research_agent, rag_agent, data_analysis_agent,
    vision_agent, risk_agent, compliance_agent, verification_agent,
)

# Fixed dependency order the supervisor's required_agents list is executed in.
ORDER = ["research", "rag", "data_analysis", "vision", "risk", "compliance", "verification"]

NODE_FUNCS = {
    "research": research_agent,
    "rag": rag_agent,
    "data_analysis": data_analysis_agent,
    "vision": vision_agent,
    "risk": risk_agent,
    "compliance": compliance_agent,
    "verification": verification_agent,
}


def _make_router(agent_name: str):
    """Returns the name of the next required agent in ORDER after agent_name, or END."""
    def router(state: AgentState) -> str:
        required = state.get("required_agents", [])
        idx = ORDER.index(agent_name)
        for nxt in ORDER[idx + 1:]:
            if nxt in required:
                return nxt
        return END
    return router


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_agent)
    for name, fn in NODE_FUNCS.items():
        graph.add_node(name, fn)

    graph.set_entry_point("supervisor")

    def supervisor_router(state: AgentState) -> str:
        required = state.get("required_agents", [])
        for nxt in ORDER:
            if nxt in required:
                return nxt
        return END

    graph.add_conditional_edges("supervisor", supervisor_router, {**{n: n for n in ORDER}, END: END})

    for name in ORDER:
        graph.add_conditional_edges(name, _make_router(name), {**{n: n for n in ORDER}, END: END})

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_agentic_workflow(user_query: str, chat_history: list[dict] | None = None, request_id: str | None = None) -> AgentState:
    request_id = request_id or f"req_{uuid.uuid4().hex[:10]}"
    initial_state: AgentState = {
        "request_id": request_id,
        "user_query": user_query,
        "chat_history": chat_history or [],
        "agent_path": [],
        "errors": [],
    }
    graph = get_graph()
    result = graph.invoke(initial_state)
    return result
