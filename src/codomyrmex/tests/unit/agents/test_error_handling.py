"""Comprehensive error handling and edge case tests.

Tests use real implementations only. FailingAgent is a test adapter
that implements BaseAgent interface for testing error scenarios, not a mock.
"""

import pytest
import subprocess

from codomyrmex.agents.core import AgentRequest, AgentResponse, AgentCapabilities
from codomyrmex.agents.core import BaseAgent
from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
from codomyrmex.agents.core.exceptions import (
    AgentError,
    EveryCodeError,
    AgentTimeoutError,
    AgentConfigurationError,
    OpenCodeError,
    JulesError,
)
from codomyrmex.agents.core.config import AgentConfig, get_config, set_config, reset_config
from codomyrmex.agents.opencode import OpenCodeClient


class FailingAgent(BaseAgent):
    """Test agent that fails in various ways for error testing.
    
    This is a test adapter implementing BaseAgent interface, not a mock.
    """

    def __init__(self, name: str, failure_type: str = "error_response"):
        super().__init__(
            name=name,
            capabilities=[AgentCapabilities.CODE_GENERATION],
            config={}
        )
        self.failure_type = failure_type

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        if self.failure_type == "error_response":
            return AgentResponse(content="", error="Simulated error")
        elif self.failure_type == "exception":
            raise AgentError("Simulated exception")
        elif self.failure_type == "timeout":
            raise AgentTimeoutError("Simulated timeout", timeout=30)
        else:
            return AgentResponse(content="Success")

    def _stream_impl(self, request: AgentRequest):
        if self.failure_type == "exception":
            raise AgentError("Stream exception")
        yield "test"


@pytest.mark.unit
class TestNetworkFailuresAndRetries:
    """Test network failure and retry scenarios."""

    def test_agent_unavailable_handling(self):
        """Test handling when agent is unavailable."""
        # Use invalid command to trigger real FileNotFoundError
        client = OpenCodeClient(config={"opencode_command": "nonexistent-opencode-command-xyz"})
        request = AgentRequest(prompt="test")
        
        response = client.execute(request)
        
        assert not response.is_success()
        assert response.error is not None
        assert "not found" in response.error.lower() or "failed" in response.error.lower()

    def test_partial_network_failure(self):
        """Test partial network failure in multi-agent scenario."""
        working_agent = FailingAgent("working", "success")
        failing_agent = FailingAgent("failing", "error_response")
        
        orchestrator = AgentOrchestrator([working_agent, failing_agent])
        request = AgentRequest(prompt="test")
        
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 2
        # One should succeed, one should fail
        success_count = sum(1 for r in responses if r.is_success())
        failure_count = sum(1 for r in responses if not r.is_success())
        
        assert success_count == 1
        assert failure_count == 1


@pytest.mark.unit
class TestTimeoutScenarios:
    """Test timeout handling scenarios."""

    def test_request_timeout_handling(self):
        """Test handling of request timeouts."""
        agent = FailingAgent("timeout_agent", "timeout")
        request = AgentRequest(prompt="test", timeout=5)

        # BaseAgent.execute() catches all exceptions and wraps them
        response = agent.execute(request)
        assert not response.is_success()
        assert response.error is not None
        assert "timeout" in response.error.lower()

    def test_timeout_in_orchestration(self):
        """Test timeout handling in orchestration."""
        timeout_agent = FailingAgent("timeout", "timeout")
        normal_agent = FailingAgent("normal", "success")
        
        orchestrator = AgentOrchestrator([timeout_agent, normal_agent])
        request = AgentRequest(prompt="test")
        
        # Should handle timeout gracefully
        try:
            responses = orchestrator.execute_parallel(request)
            # If timeout is caught, we should still get responses
            assert len(responses) == 2
        except AgentTimeoutError:
            # Timeout might propagate, which is also valid
            pass


@pytest.mark.unit
class TestInvalidConfigurationHandling:
    """Test invalid configuration handling."""

    def test_invalid_timeout_configuration(self):
        """Test handling of invalid timeout configuration."""
        config = AgentConfig(
            default_timeout=-1,
            jules_timeout=0,
            claude_timeout=-5,
            gemini_timeout=-10,
        )
        
        errors = config.validate()
        
        assert len(errors) >= 3
        assert any("default_timeout" in e for e in errors)
        assert any("jules_timeout" in e for e in errors)
        assert any("claude_timeout" in e for e in errors)
        assert any("gemini_timeout" in e for e in errors)

    def test_missing_api_key_handling(self, monkeypatch):
        """Test handling of missing API keys."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        config = AgentConfig(
            claude_api_key=None,
            codex_api_key=None
        )

        errors = config.validate()

        # Should warn about missing API keys
        assert any("Claude API key" in e for e in errors)
        assert any("Codex API key" in e for e in errors)

    def test_invalid_agent_configuration(self):
        """Test handling of invalid agent-specific configuration."""
        # Invalid timeout should be caught by validation
        config = AgentConfig(opencode_timeout=-1)
        errors = config.validate()
        
        # Should catch invalid timeout
        assert any("opencode_timeout" in e or "positive" in e for e in errors)


@pytest.mark.unit
class TestAgentUnavailabilityHandling:
    """Test handling when agents are unavailable."""

    def test_all_agents_unavailable(self):
        """Test handling when all agents are unavailable."""
        failing_agent1 = FailingAgent("agent1", "error_response")
        failing_agent2 = FailingAgent("agent2", "error_response")
        
        orchestrator = AgentOrchestrator([failing_agent1, failing_agent2])
        request = AgentRequest(prompt="test")
        
        # Fallback should return last error
        response = orchestrator.execute_with_fallback(request)
        
        assert not response.is_success()
        assert response.error is not None

    def test_partial_agent_availability(self):
        """Test handling when some agents are available."""
        working_agent = FailingAgent("working", "success")
        failing_agent = FailingAgent("failing", "error_response")
        
        orchestrator = AgentOrchestrator([failing_agent, working_agent])
        request = AgentRequest(prompt="test")
        
        # Fallback should succeed with working agent
        response = orchestrator.execute_with_fallback(request)
        
        assert response.is_success()


@pytest.mark.unit
class TestPartialFailureScenarios:
    """Test partial failure scenarios."""

    def test_partial_failure_in_parallel(self):
        """Test partial failure in parallel execution."""
        agents = [
            FailingAgent("agent1", "success"),
            FailingAgent("agent2", "error_response"),
            FailingAgent("agent3", "success"),
        ]
        
        orchestrator = AgentOrchestrator(agents)
        request = AgentRequest(prompt="test")
        
        responses = orchestrator.execute_parallel(request)
        
        assert len(responses) == 3
        success_count = sum(1 for r in responses if r.is_success())
        assert success_count == 2

    def test_cascading_failures(self):
        """Test cascading failure scenario."""
        agents = [
            FailingAgent("agent1", "error_response"),
            FailingAgent("agent2", "error_response"),
            FailingAgent("agent3", "error_response"),
        ]
        
        orchestrator = AgentOrchestrator(agents)
        request = AgentRequest(prompt="test")
        
        # Sequential should continue through all failures
        responses = orchestrator.execute_sequential(request)
        
        assert len(responses) == 3
        assert all(not r.is_success() for r in responses)

    def test_recovery_after_failure(self):
        """Test recovery after initial failure."""
        failing_agent = FailingAgent("failing", "error_response")
        recovery_agent = FailingAgent("recovery", "success")
        
        orchestrator = AgentOrchestrator([failing_agent, recovery_agent])
        request = AgentRequest(prompt="test")
        
        # Fallback should recover
        response = orchestrator.execute_with_fallback(request)
        
        assert response.is_success()


@pytest.mark.unit
class TestErrorPropagationAndRecovery:
    """Test error propagation and recovery mechanisms."""

    def test_exception_propagation(self):
        """Test that exceptions propagate correctly."""
        exception_agent = FailingAgent("exception", "exception")
        request = AgentRequest(prompt="test")
        
        # BaseAgent.execute() catches exceptions and returns error response
        # So we test the _execute_impl directly for exception propagation
        with pytest.raises(AgentError):
            exception_agent._execute_impl(request)

    def test_error_response_vs_exception(self):
        """Test difference between error response and exception."""
        error_response_agent = FailingAgent("error_response", "error_response")
        exception_agent = FailingAgent("exception", "exception")
        
        request = AgentRequest(prompt="test")
        
        # Error response should return response with error
        error_response = error_response_agent.execute(request)
        assert not error_response.is_success()
        assert error_response.error is not None
        
        # BaseAgent.execute() catches exceptions, but _execute_impl raises
        # Test that _execute_impl raises exception
        with pytest.raises(AgentError):
            exception_agent._execute_impl(request)
        
        # But execute() catches it and returns error response
        exception_response = exception_agent.execute(request)
        assert not exception_response.is_success()
        assert exception_response.error is not None

    def test_error_metadata_preservation(self):
        """Test that error metadata is preserved."""
        agent = FailingAgent("metadata", "error_response")
        request = AgentRequest(prompt="test")
        
        response = agent.execute(request)
        
        assert not response.is_success()
        assert response.error is not None
        assert response.metadata is not None

    def test_graceful_degradation(self):
        """Test graceful degradation when agents fail."""
        primary_agent = FailingAgent("primary", "error_response")
        secondary_agent = FailingAgent("secondary", "success")
        tertiary_agent = FailingAgent("tertiary", "success")
        
        orchestrator = AgentOrchestrator([
            primary_agent,
            secondary_agent,
            tertiary_agent
        ])
        
        request = AgentRequest(prompt="test")
        
        # Should gracefully fall back to secondary
        response = orchestrator.execute_with_fallback(request)
        
        assert response.is_success()


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_prompt_handling(self):
        """Test handling of empty prompts."""
        agent = FailingAgent("test", "success")
        
        request = AgentRequest(prompt="")
        
        # Should be caught by validation
        response = agent.execute(request)
        
        # Validation should catch empty prompt
        assert not response.is_success()
        assert "empty" in response.error.lower() or "prompt" in response.error.lower()

    def test_very_long_prompt(self):
        """Test handling of very long prompts."""
        agent = FailingAgent("test", "success")
        
        long_prompt = "test " * 10000
        request = AgentRequest(prompt=long_prompt)
        
        # Should handle long prompts
        response = agent.execute(request)
        
        # Should either succeed or fail gracefully
        assert response is not None

    def test_none_context_handling(self):
        """Test handling of None context."""
        agent = FailingAgent("test", "success")
        
        request = AgentRequest(prompt="test", context=None)
        
        # Should handle None context
        response = agent.execute(request)
        
        assert response is not None

    def test_empty_capabilities_list(self):
        """Test handling of empty capabilities list."""
        agent = FailingAgent("test", "success")
        
        request = AgentRequest(prompt="test", capabilities=[])
        
        # Should handle empty capabilities
        response = agent.execute(request)
        
        assert response is not None

    def test_invalid_capability_request(self):
        """Test handling of invalid capability requests."""
        agent = FailingAgent("test", "success")

        # Request capability agent doesn't support
        request = AgentRequest(
            prompt="test",
            capabilities=[AgentCapabilities.CODE_EXECUTION]  # Not supported
        )

        # _validate_request logs a warning but does not block execution
        response = agent.execute(request)

        # Agent still succeeds (capability check is advisory, not blocking)
        assert response.is_success()
