"""YAML-driven policy engine."""
import os
import yaml

POLICY_PATH = os.getenv("POLICY_PATH", "policies/policies.yaml")

_DEFAULT_POLICIES = {
    "policies": [
        {"name": "block_credential_leak", "trigger": "sensitive_data.detected", "action": "BLOCK"},
        {"name": "block_prompt_injection", "trigger": "prompt_injection.detected", "action": "BLOCK"},
        {"name": "block_jailbreak", "trigger": "jailbreak.detected", "action": "BLOCK"},
        {"name": "block_tool_abuse", "trigger": "tool_abuse.detected", "action": "BLOCK"},
        {"name": "block_exfiltration", "trigger": "exfiltration.detected", "action": "BLOCK"},
        {"name": "review_pii", "trigger": "pii.detected", "action": "REVIEW_REQUIRED"},
    ]
}


def load_policies() -> dict:
    if os.path.exists(POLICY_PATH):
        with open(POLICY_PATH) as f:
            return yaml.safe_load(f) or _DEFAULT_POLICIES
    return _DEFAULT_POLICIES


def _get(detections: dict, dotted: str):
    node = detections
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def evaluate_policies(detections: dict) -> list[dict]:
    """Returns list of {name, action, reason} for every policy that fired."""
    policies = load_policies().get("policies", [])
    fired = []
    for p in policies:
        value = _get(detections, p["trigger"])
        if value:
            policy_name = p["name"]
            trigger_name = p["trigger"]
            fired.append({"name": policy_name, "action": p["action"], "reason": f"Policy '{policy_name}' triggered by {trigger_name}"})
    return fired
