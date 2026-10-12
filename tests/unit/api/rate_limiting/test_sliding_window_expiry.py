"""Deterministic expiry tests with real limiter instances and request queues."""

from collections import deque
from concurrent.futures import ThreadPoolExecutor

import pytest

from codomyrmex.api.rate_limiting import (
    FixedWindowLimiter,
    SlidingWindowLimiter,
    TokenBucketLimiter,
)
from codomyrmex.api.rate_limiting.models import RateLimitExceeded


class ManualClock:
    """A real injectable clock with explicit time advancement, without sleeps."""

    def __init__(self, now: float = 100.0) -> None:
        self.now = now
        self.calls = 0

    def __call__(self) -> float:
        self.calls += 1
        return self.now


@pytest.mark.parametrize("timestamps", [[], [1.0, 2.0], [40.0, 41.0, 99.0]])
def test_expiry_retains_exact_boundary(timestamps: list[float]) -> None:
    """Expired requests leave; exact-cutoff and newer requests remain."""
    limiter = SlidingWindowLimiter(limit=10, window_seconds=60)
    queue = deque(timestamps)
    other = deque([1.0])
    limiter._requests["client"] = queue
    limiter._requests["other"] = other

    limiter._clean_old_requests("client", now=100.0)

    assert list(queue) == [timestamp for timestamp in timestamps if timestamp >= 40]
    assert limiter._requests["client"] is queue
    assert list(other) == [1.0]


def test_cleanup_missing_key_does_not_create_state() -> None:
    """Read-only cleanup must not allocate a missing client's queue."""
    limiter = SlidingWindowLimiter(limit=3, window_seconds=60, clock=ManualClock())
    limiter._clean_old_requests("missing", now=100.0)
    assert limiter._requests == {}


def test_public_check_and_acquire_after_full_expiry() -> None:
    """Public quota operations reclaim an exhausted, expired window."""
    limiter = SlidingWindowLimiter(limit=3, window_seconds=60, clock=ManualClock())
    limiter._requests["client"] = deque([0.0, 1.0, 2.0])
    result = limiter.check("client", cost=3)
    assert result.allowed
    assert result.remaining == 3
    result = limiter.acquire("client", cost=3)
    assert result.allowed
    assert result.remaining == 0
    assert not limiter.check("client").allowed


def test_retry_after_waits_for_enough_quota() -> None:
    """A weighted request must wait for all necessary expirations."""
    clock = ManualClock()
    limiter = SlidingWindowLimiter(limit=3, window_seconds=60, clock=clock)
    limiter.acquire("client", cost=1)
    clock.now += 10
    limiter.acquire("client", cost=2)
    clock.now += 10
    with pytest.raises(RateLimitExceeded) as failure:
        limiter.acquire("client", cost=2)
    assert failure.value.retry_after == 50
    clock.now += 50
    # Existing expiry contract retains requests precisely at the cutoff.
    assert not limiter.check("client", cost=2).allowed
    clock.now += 0.001
    assert limiter.acquire("client", cost=2).allowed


@pytest.mark.parametrize("kind", ["fixed", "sliding", "token"])
@pytest.mark.parametrize("cost", [-1, 0.5, True])
def test_invalid_cost_cannot_credit_quota(kind: str, cost: int) -> None:
    """Invalid quota amounts fail before state or quota is modified."""
    limiter = {
        "fixed": FixedWindowLimiter(limit=3, window_seconds=60),
        "sliding": SlidingWindowLimiter(limit=3, window_seconds=60),
        "token": TokenBucketLimiter(capacity=3, refill_rate=1),
    }[kind]
    for operation in (limiter.check, limiter.acquire, limiter.consume):
        with pytest.raises(ValueError, match="cost"):
            operation("client", cost=cost)
    assert limiter.check("client").remaining == 3


@pytest.mark.parametrize("kind", ["fixed", "sliding", "token"])
def test_zero_cost_is_a_noop_and_oversized_request_is_denied(kind: str) -> None:
    """Zero keeps quota intact; even a new key cannot bypass the capacity."""
    limiter = {
        "fixed": FixedWindowLimiter(limit=3, window_seconds=60),
        "sliding": SlidingWindowLimiter(limit=3, window_seconds=60),
        "token": TokenBucketLimiter(capacity=3, refill_rate=1),
    }[kind]
    assert limiter.acquire("client", cost=0).remaining == 3
    assert not limiter.check("client", cost=4).allowed
    with pytest.raises(RateLimitExceeded):
        limiter.acquire("client", cost=4)
    assert limiter.check("client").remaining == 3


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
@pytest.mark.parametrize("limiter_class", [FixedWindowLimiter, SlidingWindowLimiter])
def test_invalid_window_configuration(limiter_class: type, limit: int) -> None:
    """Invalid window dimensions cannot reach arithmetic or state creation."""
    with pytest.raises(ValueError, match="limit"):
        limiter_class(limit=limit, window_seconds=60)
    with pytest.raises(ValueError, match="window_seconds"):
        limiter_class(limit=3, window_seconds=limit)


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf")])
def test_invalid_refill_configuration(rate: float) -> None:
    """Refill calculations reject zero, negative, and nonfinite denominators."""
    with pytest.raises(ValueError, match="refill_rate"):
        TokenBucketLimiter(capacity=3, refill_rate=rate)
    with pytest.raises(ValueError, match="refill_interval"):
        TokenBucketLimiter(capacity=3, refill_rate=1, refill_interval=rate)


def test_token_refill_uses_one_clock_read_per_acquisition() -> None:
    """A consumed bucket keeps the timestamp used to calculate its refill."""
    clock = ManualClock()
    limiter = TokenBucketLimiter(capacity=3, refill_rate=1, clock=clock)
    limiter.acquire("client", cost=3)
    assert clock.calls == 1
    clock.now += 2
    assert limiter.acquire("client", cost=2).remaining == 0
    assert clock.calls == 2
    assert not limiter.check("client").allowed
    clock.now += 1
    assert limiter.acquire("client").remaining == 0


@pytest.mark.parametrize("kind", ["sliding", "token"])
def test_clock_is_sampled_under_lock(kind: str) -> None:
    """The sampled time and resulting queue/bucket mutation are serialized."""

    def clock() -> float:
        assert limiter._lock.locked()
        return 100.0

    limiter = (
        SlidingWindowLimiter(limit=3, window_seconds=60, clock=clock)
        if kind == "sliding"
        else TokenBucketLimiter(capacity=3, refill_rate=1, clock=clock)
    )
    assert limiter.acquire("client").allowed
    assert limiter.check("client").remaining == 2


def test_concurrent_requests_cannot_exceed_sliding_quota() -> None:
    """Real concurrent requests share one quota without losing updates."""
    limiter = SlidingWindowLimiter(limit=20, window_seconds=60)
    with ThreadPoolExecutor(max_workers=8) as workers:
        results = list(workers.map(lambda _: limiter.consume("client"), range(32)))
    assert sum(result.allowed for result in results) == 20
    assert limiter.check("client").remaining == 0


@pytest.mark.parametrize("initial_tokens", [-1, 4, True, 0.5])
def test_initial_tokens_cannot_exceed_capacity(initial_tokens: int) -> None:
    """Invalid initial quota cannot bypass the bucket's capacity contract."""
    with pytest.raises(ValueError, match="initial_tokens"):
        TokenBucketLimiter(capacity=3, refill_rate=1, initial_tokens=initial_tokens)


def test_composite_preflight_preserves_earlier_quota_on_known_denial():
    from codomyrmex.api.rate_limiting import CompositeRateLimiter, FixedWindowLimiter

    first = FixedWindowLimiter(10, 3600)
    exhausted = FixedWindowLimiter(1, 3600)
    exhausted.acquire("key")
    composite = CompositeRateLimiter({"first": first, "exhausted": exhausted})
    with pytest.raises(RateLimitExceeded):
        composite.acquire("key")
    assert first.check("key").remaining == 10


def test_middleware_preserves_weighted_retry_delay():
    from codomyrmex.api.rate_limiting import RateLimiterMiddleware

    clock = ManualClock(10.0)
    limiter = SlidingWindowLimiter(1, 10, clock=clock)
    limiter.acquire("key")
    denied = RateLimiterMiddleware(limiter).check("key")
    assert not denied.allowed
    assert denied.retry_after == 10.0


@pytest.mark.parametrize("kind", ["sliding", "token"])
def test_composite_and_middleware_preserve_constituent_retry(kind):
    from codomyrmex.api.rate_limiting import CompositeRateLimiter, RateLimiterMiddleware

    clock = ManualClock(10.0)
    limiter = (
        SlidingWindowLimiter(1, 10, clock=clock)
        if kind == "sliding"
        else TokenBucketLimiter(1, 0.1, clock=clock)
    )
    limiter.acquire("key")
    assert limiter.check("key").retry_after == 10.0
    composite = CompositeRateLimiter({"only": limiter})
    with pytest.raises(RateLimitExceeded) as rejection:
        composite.acquire("key")
    assert rejection.value.retry_after == 10.0
    assert RateLimiterMiddleware(composite).check("key").retry_after == 10.0
