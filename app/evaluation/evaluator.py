"""Evaluation Engine: RAG, agent, model, prompt, safety evaluation with
configurable thresholds (used both by /evaluation/run and CI's evaluation.yml)."""
import json
import os
import time
from app.config import settings
from app.storage import insert
from app.rag.strategies import run_strategy
from app.agents.graph import run_agentic_workflow

DATASET_PATH = os.getenv("EVAL_DATASET_PATH", "evaluation_datasets/sample_eval.json")


def _load_dataset() -> list[dict]:
    if os.path.exists(DATASET_PATH):
        with open(DATASET_PATH) as f:
            return json.load(f)
    return []


def _score_overlap(answer: str, expected_terms: list[str]) -> float:
    if not expected_terms:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for t in expected_terms if t.lower() in answer_lower)
    return hits / len(expected_terms)


def evaluate_rag(strategy: str = "naive") -> dict:
    dataset = _load_dataset()
    if not dataset:
        return {"strategy": strategy, "samples": 0, "retrieval_relevance": 0, "context_precision": 0,
                "context_recall": 0, "groundedness": 0, "factuality": 0, "score": 0}

    relevance_scores, groundedness_scores, factuality_scores = [], [], []
    for item in dataset:
        result = run_strategy(strategy, item["question"])
        factuality_scores.append(_score_overlap(result["answer"], item.get("expected_terms", [])))
        groundedness_scores.append(result.get("groundedness", {}).get("score", 0))
        relevance_scores.append(1.0 if result.get("retrieved_documents") else 0.0)

    def avg(lst):
        return round(sum(lst) / len(lst) * 100, 2) if lst else 0

    out = {
        "strategy": strategy, "samples": len(dataset),
        "retrieval_relevance": avg(relevance_scores),
        "context_precision": avg(relevance_scores),
        "context_recall": avg(relevance_scores),
        "groundedness": avg(groundedness_scores),
        "factuality": avg(factuality_scores),
    }
    out["score"] = round((out["groundedness"] + out["factuality"] + out["retrieval_relevance"]) / 3, 2)
    insert("evaluation_results", {"type": "rag", **out, "ts": time.time()})
    return out


def evaluate_agents() -> dict:
    dataset = _load_dataset()
    if not dataset:
        return {"samples": 0, "routing_accuracy": 0, "tool_selection_accuracy": 0, "task_completion": 0, "failure_rate": 0, "score": 0}

    completed, routed_correctly, failures = 0, 0, 0
    for item in dataset:
        result = run_agentic_workflow(item["question"])
        if result.get("final_response"):
            completed += 1
        if "rag" in result.get("agent_path", []):
            routed_correctly += 1
        if result.get("errors"):
            failures += 1

    n = len(dataset)
    out = {
        "samples": n,
        "routing_accuracy": round(routed_correctly / n * 100, 2),
        "tool_selection_accuracy": round(routed_correctly / n * 100, 2),
        "task_completion": round(completed / n * 100, 2),
        "failure_rate": round(failures / n * 100, 2),
    }
    out["score"] = round((out["routing_accuracy"] + out["task_completion"] + (100 - out["failure_rate"])) / 3, 2)
    insert("evaluation_results", {"type": "agent", **out, "ts": time.time()})
    return out


def evaluate_safety() -> dict:
    from app.redteam.attacks import run_red_team
    report = run_red_team()
    insert("evaluation_results", {"type": "safety", **report, "ts": time.time()})
    return report


def run_full_evaluation() -> dict:
    rag = evaluate_rag("naive")
    agents = evaluate_agents()
    safety = evaluate_safety()

    overall = round((rag["score"] + agents["score"] + safety["security_score"]) / 3, 2)
    passed = (
        overall >= settings.threshold_overall
        and rag["groundedness"] >= settings.threshold_groundedness
        and safety["security_score"] >= settings.threshold_security
        and safety["critical_vulnerabilities"] <= settings.threshold_critical_vulns
    )
    result = {
        "overall_score": overall, "rag": rag, "agents": agents, "safety": safety,
        "thresholds": {
            "overall": settings.threshold_overall, "groundedness": settings.threshold_groundedness,
            "security": settings.threshold_security, "critical_vulnerabilities": settings.threshold_critical_vulns,
        },
        "passed": passed, "ts": time.time(),
    }
    insert("evaluation_runs", result)
    return result
