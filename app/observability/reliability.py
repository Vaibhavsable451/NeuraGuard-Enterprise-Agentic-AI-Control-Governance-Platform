"""Reliability primitives: retry, timeout, backoff, circuit breaker, rate limit."""
import time
import functools
import threading
from collections import defaultdict


def retry(max_attempts: int = 3, backoff_base: float = 0.2):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    last_exc = e
                    time.sleep(backoff_base * (2 ** attempt))
            raise last_exc
        return wrapper
    return decorator


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.reset_seconds = reset_seconds
        self.failures = 0
        self.opened_at: float | None = None

    def is_open(self) -> bool:
        if self.opened_at is None:
            return False
        if time.time() - self.opened_at > self.reset_seconds:
            self.opened_at = None
            self.failures = 0
            return False
        return True

    def record_success(self):
        self.failures = 0
        self.opened_at = None

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.time()


class RateLimiter:
    """Simple in-memory token-bucket-ish limiter per key."""
    def __init__(self, max_per_minute: int = 60):
        self.max_per_minute = max_per_minute
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            hits = [t for t in self._hits[key] if now - t < 60]
            if len(hits) >= self.max_per_minute:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True


global_rate_limiter = RateLimiter(max_per_minute=120)
