from app.finops.cost import record_token_usage, get_cost_summary


def test_record_and_summarize_cost():
    record_token_usage("llama-3.1-8b-instant", 100, 50, agent="test_agent", workflow="test_wf", request_id="r1")
    summary = get_cost_summary()
    assert summary["total_cost"] >= 0
    assert "test_agent" in summary["cost_per_agent"]
