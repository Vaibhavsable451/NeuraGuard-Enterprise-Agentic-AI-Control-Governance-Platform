"""Rule/pattern-based detectors: PII, prompt injection, jailbreak, tool abuse,
data exfiltration, sensitive data. Deterministic and network-free."""
import re

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

PROMPT_INJECTION_MARKERS = [
    "ignore previous instructions", "ignore all previous", "disregard the system prompt",
    "you are now", "new instructions:", "act as if", "pretend you have no restrictions",
    "reveal your system prompt", "print your instructions", "override safety",
]

JAILBREAK_MARKERS = [
    "dan mode", "do anything now", "no ethical guidelines", "developer mode enabled",
    "bypass your restrictions", "unfiltered response", "without any censorship",
    "pretend you are not an ai",
]

TOOL_ABUSE_MARKERS = [
    "delete all", "drop table", "rm -rf", "format c:", "exfiltrate", "send this to external",
    "disable logging", "disable monitoring", "grant admin access",
]

EXFILTRATION_MARKERS = [
    "send the data to", "upload this to an external", "email this to my personal",
    "post this to pastebin", "copy the database to",
]

SENSITIVE_KEYWORDS = ["password", "api key", "secret key", "private key", "confidential", "classified"]


def detect_pii(text: str) -> dict:
    found = {}
    for kind, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found[kind] = len(matches)
    return {"detected": bool(found), "types": found}


def _match_markers(text: str, markers: list[str]) -> list[str]:
    lower = text.lower()
    return [m for m in markers if m in lower]


def detect_prompt_injection(text: str) -> dict:
    hits = _match_markers(text, PROMPT_INJECTION_MARKERS)
    return {"detected": bool(hits), "matched": hits}


def detect_jailbreak(text: str) -> dict:
    hits = _match_markers(text, JAILBREAK_MARKERS)
    return {"detected": bool(hits), "matched": hits}


def detect_tool_abuse(text: str) -> dict:
    hits = _match_markers(text, TOOL_ABUSE_MARKERS)
    return {"detected": bool(hits), "matched": hits}


def detect_exfiltration(text: str) -> dict:
    hits = _match_markers(text, EXFILTRATION_MARKERS)
    return {"detected": bool(hits), "matched": hits}


def detect_sensitive_data(text: str) -> dict:
    hits = _match_markers(text, SENSITIVE_KEYWORDS)
    return {"detected": bool(hits), "matched": hits}


def run_all_detectors(text: str) -> dict:
    return {
        "pii": detect_pii(text),
        "prompt_injection": detect_prompt_injection(text),
        "jailbreak": detect_jailbreak(text),
        "tool_abuse": detect_tool_abuse(text),
        "exfiltration": detect_exfiltration(text),
        "sensitive_data": detect_sensitive_data(text),
    }
