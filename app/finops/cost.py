"""FinOps: token/cost tracking, per-request/agent/workflow cost, anomaly detection."""
import time
import statistics
from app.storage import insert, all_records

# $ per 1K tokens, illustrative pricing table (override via env in a real deployment)
PRICING = {
    "openai/gpt-oss-120b": {"input": 0.00059, "output": 0.00079},
    "openai/gpt-oss-20b": {"input": 0.00005, "output": 0.00008},
    "llama-3.3-70b-versatile": {"input": 0.00059, "output": 0.00079},
    "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
    "mock": {"input": 0.0, "output": 0.0},
}
DEFAULT_PRICE = {"input": 0.0005, "output": 0.0007}


def _price(model: str) -> dict:
    return PRICING.get(model, DEFAULT_PRICE)


def record_token_usage(model: str, input_tokens: int, output_tokens: int,
                        agent: str = "unknown", workflow: str = "unknown",
                        request_id: str = "unknown") -> dict:
    price = _price(model)
    cost = (input_tokens / 1000) * price["input"] + (output_tokens / 1000) * price["output"]
    record = {
        "model": model, "input_tokens": input_tokens, "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens, "cost": round(cost, 6),
        "agent": agent, "workflow": workflow, "request_id": request_id, "ts": time.time(),
    }
    insert("finops_usage", record)
    return record


def get_cost_summary() -> dict:
    records = all_records("finops_usage")
    if not records:
        return {
            "total_cost": 0, "daily_cost": 0, "monthly_cost": 0,
            "cost_per_request": 0, "cost_per_agent": {}, "cost_per_workflow": {},
            "anomalies": [], "recommendations": ["No usage recorded yet."],
        }

    total_cost = sum(r["cost"] for r in records)
    now = time.time()
    daily = sum(r["cost"] for r in records if now - r["ts"] < 86400)
    monthly = sum(r["cost"] for r in records if now - r["ts"] < 30 * 86400)

    by_agent: dict[str, float] = {}
    by_workflow: dict[str, float] = {}
    for r in records:
        by_agent[r["agent"]] = by_agent.get(r["agent"], 0) + r["cost"]
        by_workflow[r["workflow"]] = by_workflow.get(r["workflow"], 0) + r["cost"]

    requests = {r["request_id"] for r in records}
    cost_per_request = total_cost / len(requests) if requests else 0

    costs = [r["cost"] for r in records]
    anomalies = []
    if len(costs) >= 5:
        mean = statistics.mean(costs)
        stdev = statistics.pstdev(costs) or 0.000001
        for r in records:
            if r["cost"] > mean + 3 * stdev:
                anomalies.append({"request_id": r["request_id"], "cost": r["cost"], "reason": "cost > mean + 3*stdev"})

    recommendations = []
    if by_workflow:
        most_expensive = max(by_workflow, key=by_workflow.get)
        recommendations.append(f"'{most_expensive}' is your most expensive workflow — consider routing it to the smaller fallback model or caching retrieval results.")
    if any(r["model"] != "llama-3.1-8b-instant" and r["total_tokens"] < 200 for r in records):
        recommendations.append("Several short completions used the larger model — route short/simple requests to the fallback model to cut cost.")

    return {
        "total_cost": round(total_cost, 4),
        "daily_cost": round(daily, 4),
        "monthly_cost": round(monthly, 4),
        "cost_per_request": round(cost_per_request, 6),
        "cost_per_agent": {k: round(v, 4) for k, v in by_agent.items()},
        "cost_per_workflow": {k: round(v, 4) for k, v in by_workflow.items()},
        "anomalies": anomalies,
        "recommendations": recommendations or ["Cost usage looks stable."],
    }
