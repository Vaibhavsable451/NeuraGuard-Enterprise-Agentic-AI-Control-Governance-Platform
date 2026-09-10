"""Regression tests: guard against known-fixed issues regressing."""
from app.governance.guardrails import check_groundedness


def test_groundedness_zero_without_context():
    result = check_groundedness("Some answer.", [])
    assert result["grounded"] is False


def test_groundedness_high_with_matching_context():
    result = check_groundedness("The sky is blue.", ["The sky is blue during a clear day."])
    assert result["score"] > 0
