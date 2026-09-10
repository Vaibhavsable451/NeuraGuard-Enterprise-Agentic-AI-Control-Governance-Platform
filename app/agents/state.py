"""Typed LangGraph state shared across all agents."""
from typing import TypedDict


class AgentState(TypedDict, total=False):
    request_id: str
    user_query: str
    chat_history: list[dict]
    required_agents: list[str]
    agent_path: list[str]
    research_notes: str
    rag_result: dict
    data_analysis: str
    vision_notes: str
    risk_assessment: dict
    compliance_assessment: dict
    verification: dict
    governance_decision: dict
    final_response: str
    errors: list[str]
    trace: list[dict]
