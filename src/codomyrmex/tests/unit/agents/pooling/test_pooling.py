"""
Tests for Agent Pooling Module
"""

import pytest
import time
from codomyrmex.agents.pooling import (
    AgentPool,
    FallbackChain,
    CircuitBreaker,
    LoadBalanceStrategy,
    AgentStatus,
    PoolConfig,
)


class MockAgent:
    """Mock agent for testing."""
    
    def __init__(self, name: str, fail_count: int = 0, latency_ms: float = 10):
        self.name = name
        self.fail_count = fail_count
        self.latency_ms = latency_ms
        self._calls = 0
    
    def execute(self, prompt: str) -> str:
        self._calls += 1
        time.sleep(self.latency_ms / 1000)
        
        if self._calls <= self.fail_count:
            raise RuntimeError(f"{self.name} failed")
        
        return f"{self.name}: Response to '{prompt}'"
    
    @property
    def call_count(self) -> int:
        return self._calls


class TestCircuitBreaker:
    """Tests for circuit breaker."""
    
    def test_closed_by_default(self):
        """Circuit should be closed initially."""
        cb = CircuitBreaker()
        assert cb.is_open is False
    
    def test_opens_after_failures(self):
        """Circuit should open after threshold failures."""
        cb = CircuitBreaker(failure_threshold=3)
        
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open is False
        
        cb.record_failure()
        assert cb.is_open is True
    
    def test_success_resets(self):
        """Success should reset failure count."""
        cb = CircuitBreaker(failure_threshold=3)
        
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        cb.record_failure()
        cb.record_failure()
        
        # Should not be open because success reset the count
        assert cb.is_open is False
    
    def test_reset(self):
        """Manual reset should close circuit."""
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.is_open is True
        
        cb.reset()
        assert cb.is_open is False


class TestAgentPool:
    """Tests for agent pool."""
    
    def test_add_agent(self):
        """Adding agents should work."""
        pool = AgentPool[MockAgent]()
        pool.add_agent("agent1", MockAgent("Agent 1"))
        
        available = pool.get_available_agents()
        assert len(available) == 1
        assert available[0].agent_id == "agent1"
    
    def test_remove_agent(self):
        """Removing agents should work."""
        pool = AgentPool[MockAgent]()
        pool.add_agent("agent1", MockAgent("Agent 1"))
        
        assert pool.remove_agent("agent1") is True
        assert pool.remove_agent("nonexistent") is False
        assert len(pool.get_available_agents()) == 0
    
    def test_execute_success(self):
        """Successful execution should work."""
        pool = AgentPool[MockAgent]()
        pool.add_agent("agent1", MockAgent("Agent 1"))
        
        result = pool.execute(lambda agent: agent.execute("test"))
        assert "Agent 1" in result
    
    def test_execute_with_failover(self):
        """Failover should use next agent."""
        pool = AgentPool[MockAgent](
            strategy=LoadBalanceStrategy.PRIORITY,
            config=PoolConfig(max_retries=3),
        )
        
        # First agent always fails, second succeeds
        pool.add_agent("failing", MockAgent("Failing", fail_count=100), priority=0)
        pool.add_agent("working", MockAgent("Working", fail_count=0), priority=1)
        
        result = pool.execute(lambda agent: agent.execute("test"))
        assert "Working" in result
    
    def test_round_robin(self):
        """Round robin should distribute requests."""
        pool = AgentPool[MockAgent](strategy=LoadBalanceStrategy.ROUND_ROBIN)
        
        agent1 = MockAgent("Agent 1")
        agent2 = MockAgent("Agent 2")
        pool.add_agent("agent1", agent1)
        pool.add_agent("agent2", agent2)
        
        pool.execute(lambda agent: agent.execute("test"))
        pool.execute(lambda agent: agent.execute("test"))
        pool.execute(lambda agent: agent.execute("test"))
        pool.execute(lambda agent: agent.execute("test"))
        
        # Should be roughly balanced (may not be exactly even due to selection order)
        assert agent1.call_count >= 1
        assert agent2.call_count >= 1
    
    def test_weighted_distribution(self):
        """Weighted strategy should favor higher weights."""
        pool = AgentPool[MockAgent](strategy=LoadBalanceStrategy.WEIGHTED)
        
        heavy = MockAgent("Heavy")
        light = MockAgent("Light")
        pool.add_agent("heavy", heavy, weight=10.0)
        pool.add_agent("light", light, weight=1.0)
        
        for _ in range(20):
            pool.execute(lambda agent: agent.execute("test"))
        
        # Heavy should get more calls (not deterministic but very likely)
        assert heavy.call_count > light.call_count
    
    def test_circuit_breaker_integration(self):
        """Circuit breaker should track failures."""
        config = PoolConfig(circuit_failure_threshold=2, max_retries=1)
        pool = AgentPool[MockAgent](config=config)
        
        failing = MockAgent("Failing", fail_count=100)
        working = MockAgent("Working")
        pool.add_agent("failing", failing)
        pool.add_agent("working", working)
        
        # Execute multiple times - should track failures
        for _ in range(5):
            try:
                pool.execute(lambda agent: agent.execute("test"))
            except:
                pass
        
        # Verify failures are tracked
        stats = pool.get_stats()
        assert stats["failing"]["failure_count"] >= 1
    
    def test_health_tracking(self):
        """Health metrics should be tracked."""
        pool = AgentPool[MockAgent]()
        pool.add_agent("agent1", MockAgent("Agent 1"))
        
        pool.execute(lambda agent: agent.execute("test"))
        pool.execute(lambda agent: agent.execute("test"))
        
        stats = pool.get_stats()
        assert stats["agent1"]["success_count"] == 2
        assert stats["agent1"]["status"] == "healthy"
    
    def test_reset_agent(self):
        """Resetting agent should clear metrics."""
        pool = AgentPool[MockAgent]()
        pool.add_agent("agent1", MockAgent("Agent 1"))
        pool.execute(lambda agent: agent.execute("test"))
        
        pool.reset_agent("agent1")
        
        stats = pool.get_stats()
        assert stats["agent1"]["success_count"] == 0


class TestFallbackChain:
    """Tests for fallback chain."""
    
    def test_primary_succeeds(self):
        """Primary agent should be used when it works."""
        chain = FallbackChain[MockAgent]()
        chain.add("primary", MockAgent("Primary"))
        chain.add("secondary", MockAgent("Secondary"))
        
        result = chain.execute(lambda agent: agent.execute("test"))
        assert "Primary" in result
    
    def test_fallback_on_failure(self):
        """Should fall back when primary fails."""
        chain = FallbackChain[MockAgent]()
        chain.add("primary", MockAgent("Primary", fail_count=1))
        chain.add("secondary", MockAgent("Secondary"))
        
        result = chain.execute(lambda agent: agent.execute("test"))
        assert "Secondary" in result
    
    def test_fallback_callback(self):
        """Fallback callback should be called."""
        chain = FallbackChain[MockAgent]()
        chain.add("primary", MockAgent("Primary", fail_count=1))
        chain.add("secondary", MockAgent("Secondary"))
        
        fallback_calls = []
        
        def on_fallback(name, error):
            fallback_calls.append((name, str(error)))
        
        chain.execute(lambda agent: agent.execute("test"), on_fallback=on_fallback)
        
        assert len(fallback_calls) == 1
        assert fallback_calls[0][0] == "primary"
    
    def test_all_fail(self):
        """Should raise when all agents fail."""
        chain = FallbackChain[MockAgent]()
        chain.add("agent1", MockAgent("Agent1", fail_count=100))
        chain.add("agent2", MockAgent("Agent2", fail_count=100))
        
        with pytest.raises(RuntimeError):
            chain.execute(lambda agent: agent.execute("test"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
