from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic
from typing import Callable, Deque, Literal

from fastapi import Request

from app.core.config import settings
from app.core.exceptions.base import RateLimitError
from app.core.request_context import RequestContext

Tier = Literal["strict", "moderate"]

_buckets: dict[str, Deque[float]] = defaultdict(deque)


def clear_rate_limit_store() -> None:
    _buckets.clear()


def _client_ip(request: Request) -> str:
    ip = RequestContext.get_client_ip()
    if ip:
        return ip
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _consume(key: str, max_hits: int, window_seconds: float) -> int | None:
    now = monotonic()
    bucket = _buckets[key]
    cutoff = now - window_seconds
    while bucket and bucket[0] <= cutoff:
        bucket.popleft()

    if len(bucket) >= max_hits:
        oldest = bucket[0]
        retry_after = max(1, int(oldest + window_seconds - now) + 1)
        return retry_after

    bucket.append(now)
    return None


def RateLimit(scope: str, *, tier: Tier = "strict") -> Callable[[Request], None]:
    def dependency(request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return

        max_hits = (
            settings.RATE_LIMIT_STRICT_MAX if tier == "strict" else settings.RATE_LIMIT_MODERATE_MAX
        )
        window = float(settings.RATE_LIMIT_WINDOW_SECONDS)
        key = f"{scope}:{_client_ip(request)}"
        retry_after = _consume(key, max_hits, window)
        if retry_after is not None:
            raise RateLimitError(retry_after=retry_after)

    return dependency
