"""
CI/CD evaluation gate. Runs the full evaluation and exits non-zero if
configured thresholds are not met, so GitHub Actions blocks deployment.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.evaluation.evaluator import run_full_evaluation  # noqa: E402


def main() -> int:
    result = run_full_evaluation()
    print(json.dumps(result, indent=2, default=str))
    print(f"Overall score: {result['overall_score']}")
    if not result["passed"]:
        print("Evaluation thresholds not met - deployment will be blocked.")
        return 1
    print("Evaluation thresholds passed - deployment may proceed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
