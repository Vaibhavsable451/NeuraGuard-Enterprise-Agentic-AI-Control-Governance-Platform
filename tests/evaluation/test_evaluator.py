from app.evaluation.evaluator import evaluate_rag, evaluate_safety


def test_evaluate_rag_returns_scores():
    result = evaluate_rag("naive")
    assert "score" in result


def test_evaluate_safety_returns_security_score():
    result = evaluate_safety()
    assert "security_score" in result
