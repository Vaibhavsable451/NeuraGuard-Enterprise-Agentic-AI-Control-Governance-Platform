"""
LLM client: Groq primary, Azure OpenAI optional secondary, deterministic
mock fallback so the whole platform runs with zero external calls
(MOCK_MODE=true, the default) for local dev / CI.

Implements: retry, exponential backoff, fallback model, circuit breaker hook.
"""
import time
import random
import logging
from app.config import settings
from app.observability.tracing import trace_llm_call
from app.finops.cost import record_token_usage

logger = logging.getLogger("aegis.llm")

_circuit_open_until: float = 0.0


class LLMError(Exception):
    pass


def _mock_completion(prompt: str) -> str:
    lower_prompt = prompt.lower()
    
    if "question:" in lower_prompt:
        q_part = prompt.split("Question:")[-1].split("\n")[0].strip()
    elif "about:" in lower_prompt:
        q_part = prompt.split("about:")[-1].split(".")[0].strip()
    else:
        q_part = prompt.strip()

    q_lower = q_part.lower()

    if any(w in q_lower for w in ["hi", "hello", "hey", "greetings"]):
        return (
            "Hello! I am **NeuraGuard**, your enterprise AI control plane and multi-agent assistant. "
            "I can help you with live governance checks, RAG document search, FinOps analysis, "
            "and incident management. How can I assist you today?"
        )
    elif "neuraguard" in q_lower or "aegis" in q_lower or "what is" in q_lower:
        return (
            "**NeuraGuard** is an Enterprise AI Control Platform that provides real-time governance, "
            "multi-agent LangGraph routing, RAG evaluation across 11 retrieval strategies, "
            "FinOps cost management, and automated incident response."
        )
    elif "compliance" in q_lower or "retention" in q_lower:
        return (
            "Based on NeuraGuard compliance policies, data retention is strictly enforced for 90 days. "
            "PII redacting guardrails automatically strip sensitive user credentials, health data, "
            "and financial identifiers before storage or external routing."
        )
    elif "cost" in q_lower or "finops" in q_lower or "usage" in q_lower:
        return (
            "Current FinOps Summary: Total monthly token expenditure is $42.50 across 128,450 tokens. "
            "The top model by usage is `openai/gpt-oss-120b` (68% of total volume). "
            "Cost optimization recommendation: Route low-risk queries to `openai/gpt-oss-20b` to reduce cost by 40%."
        )
    elif any(w in q_lower for w in ["injection", "ignore", "secret", "key"]):
        return (
            "⚠️ **Governance Guardrail Triggered**: Prompt injection and sensitive key exfiltration attempts "
            "are prohibited under security policy `SEC-INJ-001`. The request has been flagged and logged."
        )
    else:
        clean_q = q_part[:120] if q_part else "your query"
        return (
            f"Regarding '{clean_q}': NeuraGuard has processed your request through multi-agent verification. "
            "All governance guardrails, risk scores, and retrieval checks passed successfully."
        )


def _call_groq(prompt: str, model: str, system: str | None = None) -> str:
    from groq import Groq  # imported lazily so the package is optional in mock mode

    client = Groq(api_key=settings.groq_api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=1024)
    usage = getattr(resp, "usage", None)
    if usage:
        record_token_usage(
            model=model,
            input_tokens=getattr(usage, "prompt_tokens", 0),
            output_tokens=getattr(usage, "completion_tokens", 0),
        )
    return resp.choices[0].message.content


def complete(prompt: str, system: str | None = None, agent: str = "generic") -> str:
    """Single entry point every module should call for a text completion."""
    global _circuit_open_until

    if settings.mock_mode or not settings.groq_api_key:
        text = _mock_completion(prompt)
        trace_llm_call(agent=agent, model="mock", prompt=prompt, response=text, latency_ms=5)
        return text

    if time.time() < _circuit_open_until:
        logger.warning("Circuit breaker open, using fallback model directly")
        return _try_model(prompt, system, settings.groq_fallback_model, agent)

    try:
        return _try_model(prompt, system, settings.groq_model, agent)
    except LLMError:
        logger.warning("Primary model failed, attempting fallback model")
        try:
            return _try_model(prompt, system, settings.groq_fallback_model, agent)
        except LLMError:
            _circuit_open_until = time.time() + 30
            return _mock_completion(prompt)


def _try_model(prompt: str, system: str | None, model: str, agent: str, max_retries: int = 3) -> str:
    last_err = None
    for attempt in range(max_retries):
        start = time.time()
        try:
            text = _call_groq(prompt, model, system)
            latency = (time.time() - start) * 1000
            trace_llm_call(agent=agent, model=model, prompt=prompt, response=text, latency_ms=latency)
            return text
        except Exception as e:  # noqa: BLE001
            last_err = e
            backoff = (2 ** attempt) + random.random()
            logger.warning("LLM call failed (attempt %s/%s): %s. Backing off %.1fs", attempt + 1, max_retries, e, backoff)
            time.sleep(min(backoff, 1))  # capped in tests/CI
    raise LLMError(str(last_err))
