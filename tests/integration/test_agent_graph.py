from app.agents.graph import run_agentic_workflow


def test_agentic_workflow_produces_response():
    result = run_agentic_workflow("What is our compliance policy on data retention?")
    assert result["final_response"]
    assert "rag" in result["agent_path"]
    assert "verification" in result["agent_path"]


def test_agentic_workflow_does_not_force_every_agent():
    result = run_agentic_workflow("Hello")
    # vision should not run unless an image-related term is present
    assert "vision" not in result.get("required_agents", []) or "vision" in result["agent_path"]
