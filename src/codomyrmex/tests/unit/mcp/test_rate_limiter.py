"""Tests for rate limiter — v0.1.8 Stream 2.

Zero-mock: real token buckets with real time passage.
"""

import time

import pytest

from codomyrmex.model_context_protocol.reliability.rate_limiter import (
    RateLimiter,
    RateLimiterConfig,
    _TokenBucket,
)


# ── Token bucket internals ───────────────────────────────────────────


def test_bucket_starts_full():
    """Test functionality: bucket starts full."""
    b = _TokenBucket(rate=10, burst=10)
    assert b.tokens == pytest.approx(10, abs=0.1)


def test_bucket_consume_reduces_tokens():
    """Test functionality: bucket consume reduces tokens."""
    b = _TokenBucket(rate=10, burst=10)
    assert b.consume(1)
    assert b.tokens < 10


def test_bucket_rejects_when_empty():
    """Test functionality: bucket rejects when empty."""
    b = _TokenBucket(rate=1, burst=2)
    assert b.consume(2)
    assert not b.consume(1)


def test_bucket_refills_over_time():
    """Test functionality: bucket refills over time."""
    b = _TokenBucket(rate=100, burst=10)
    b.consume(10)
    assert b.tokens < 1
    time.sleep(0.05)
    assert b.tokens > 0  # refilled ~5 tokens


def test_bucket_caps_at_burst():
    """Test functionality: bucket caps at burst."""
    b = _TokenBucket(rate=1000, burst=5)
    time.sleep(0.01)  # would add 10 tokens at rate 1000
    assert b.tokens <= 5


# ── RateLimiter ──────────────────────────────────────────────────────


def test_limiter_allows_under_rate():
    """Test functionality: limiter allows under rate."""
    rl = RateLimiter(RateLimiterConfig(rate=100, burst=100))
    for _ in range(50):
        assert rl.allow("test-tool")


def test_limiter_rejects_over_burst():
    """Test functionality: limiter rejects over burst."""
    rl = RateLimiter(RateLimiterConfig(rate=1, burst=3))
    assert rl.allow("t1")
    assert rl.allow("t2")
    assert rl.allow("t3")
    assert not rl.allow("t4")


def test_per_tool_rate_limit():
    """Test functionality: per tool rate limit."""
    rl = RateLimiter(RateLimiterConfig(
        rate=1000,
        burst=1000,
        per_tool_rate={"slow_tool": 1},
        per_tool_burst={"slow_tool": 2},
    ))
    assert rl.allow("slow_tool")
    assert rl.allow("slow_tool")
    assert not rl.allow("slow_tool")  # per-tool exhausted
    assert rl.allow("fast_tool")      # global still ok


def test_per_tool_does_not_affect_other_tools():
    """Test functionality: per tool does not affect other tools."""
    rl = RateLimiter(RateLimiterConfig(
        rate=100,
        burst=100,
        per_tool_rate={"limited": 1},
        per_tool_burst={"limited": 1},
    ))
    assert rl.allow("limited")
    assert not rl.allow("limited")
    # Other tools should still work
    for _ in range(10):
        assert rl.allow("unlimited")


def test_limiter_recovers_over_time():
    """Test functionality: limiter recovers over time."""
    rl = RateLimiter(RateLimiterConfig(rate=100, burst=2))
    rl.allow("a")
    rl.allow("a")
    assert not rl.allow("a")
    time.sleep(0.05)  # refill ~5 tokens
    assert rl.allow("a")


# ── Metrics ──────────────────────────────────────────────────────────


def test_metrics_structure():
    """Test functionality: metrics structure."""
    rl = RateLimiter(RateLimiterConfig(
        rate=10, burst=20,
        per_tool_rate={"x": 5}, per_tool_burst={"x": 10},
    ))
    rl.allow("x")
    m = rl.metrics
    assert "global" in m
    assert m["global"]["rate"] == 10
    assert m["global"]["burst"] == 20
    assert "per_tool" in m
    assert "x" in m["per_tool"]


# ── Reset ────────────────────────────────────────────────────────────


def test_reset_restores_full_capacity():
    """Test functionality: reset restores full capacity."""
    rl = RateLimiter(RateLimiterConfig(rate=1, burst=2))
    rl.allow("a")
    rl.allow("a")
    assert not rl.allow("a")
    rl.reset()
    assert rl.allow("a")
    assert rl.allow("a")
