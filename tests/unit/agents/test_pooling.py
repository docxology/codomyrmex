"""Tests for agent pooling: AgentPool, CircuitBreaker, load balancing strategies."""

import pytest

from codomyrmex.agents.pooling import (
    AgentHealth,
    AgentPool,
    AgentStatus,
    CircuitBreaker,
    LoadBalanceStrategy,
    PoolConfig,
)


# ---------------------------------------------------------------------------
# Helpers (real objects, zero mocks)
# ---------------------------------------------------------------------------

class FakeAgent:
    """Lightweight agent stand-in for pool tests (NOT a mock — just a minimal real object)."""

    def __init__(self, name: str, fail: bool = False):
        self.name = name
        self.fail = fail

    def run(self, prompt: str) -> str:
        if self.fail:
            raise RuntimeError(f"{self.name} failed")
        return f"{self.name}:{prompt}"


# ── CircuitBreaker ────────────────────────────────────────────────────────


class TestCircuitBreaker:
    def test_starts_closed(self):
        cb = CircuitBreaker(failure_threshold=3)
        assert not cb.is_open

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout_s=60)
        for _ in range(3):
            cb.record_failure()
        assert cb.is_open

    def test_success_resets_counter(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        # Should still be closed
        assert not cb.is_open

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open
        cb.reset()
        assert not cb.is_open


# ── AgentHealth ───────────────────────────────────────────────────────────


class TestAgentHealth:
    def test_initial_state(self):
        h = AgentHealth()
        assert h.status == AgentStatus.HEALTHY
        assert h.avg_latency_ms == 0.0
        assert h.error_rate == 0.0
        assert h.is_available

    def test_error_rate(self):
        h = AgentHealth(success_count=7, failure_count=3)
        assert abs(h.error_rate - 0.3) < 0.01

    def test_avg_latency(self):
        h = AgentHealth(success_count=4, failure_count=0, total_latency_ms=400.0)
        assert h.avg_latency_ms == 100.0


# ── AgentPool ─────────────────────────────────────────────────────────────


class TestAgentPool:
    def test_add_remove(self):
        pool = AgentPool[FakeAgent]()
        pool.add_agent("a1", FakeAgent("alpha"))
        pool.add_agent("a2", FakeAgent("beta"))
        assert len(pool.get_available_agents()) == 2
        pool.remove_agent("a1")
        assert len(pool.get_available_agents()) == 1

    def test_round_robin(self):
        pool = AgentPool[FakeAgent](strategy=LoadBalanceStrategy.ROUND_ROBIN)
        pool.add_agent("a", FakeAgent("A"))
        pool.add_agent("b", FakeAgent("B"))
        results = []
        for _ in range(4):
            r = pool.execute(lambda agent: agent.run("x"))
            results.append(r)
        # Should alternate between A and B
        assert "A:x" in results and "B:x" in results

    def test_execute_with_failover(self):
        pool = AgentPool[FakeAgent](
            strategy=LoadBalanceStrategy.ROUND_ROBIN,
            config=PoolConfig(max_retries=3),
        )
        pool.add_agent("bad", FakeAgent("bad", fail=True))
        pool.add_agent("good", FakeAgent("good", fail=False))
        result = pool.execute(lambda agent: agent.run("test"))
        assert result == "good:test"

    def test_pool_stats(self):
        pool = AgentPool[FakeAgent]()
        pool.add_agent("one", FakeAgent("one"))
        pool.execute(lambda a: a.run("hi"))
        stats = pool.get_stats()
        assert "one" in stats

    def test_reset_agent(self):
        pool = AgentPool[FakeAgent]()
        pool.add_agent("r", FakeAgent("r"))
        pool.execute(lambda a: a.run("x"))
        pool.reset_agent("r")
        stats = pool.get_stats()
        assert stats["r"]["success_count"] == 0

    def test_reset_all(self):
        pool = AgentPool[FakeAgent]()
        pool.add_agent("a", FakeAgent("a"))
        pool.add_agent("b", FakeAgent("b"))
        pool.execute(lambda a: a.run("x"))
        pool.reset_all()
        for s in pool.get_stats().values():
            assert s["success_count"] == 0
