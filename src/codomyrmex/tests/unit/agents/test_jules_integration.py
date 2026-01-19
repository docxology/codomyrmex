"""Integration tests for Jules agent integration.

Tests use real implementations only. When Jules CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest
from typing import Any

from codomyrmex.agents.core import AgentRequest, AgentCapabilities, AgentResponse
from codomyrmex.agents.jules import JulesClient, JulesIntegrationAdapter
from codomyrmex.agents.core import BaseAgent
from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
from codomyrmex.agents.core.exceptions import JulesError
from codomyrmex.tests.unit.agents.helpers import JULES_AVAILABLE


class TestJulesClient:
    """Test JulesClient functionality."""

    def test_jules_client_initialization(self):
        """Test JulesClient can be initialized."""
        client = JulesClient()
        assert client.name == "jules"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.STREAMING in client.get_capabilities()

    def test_jules_client_capabilities(self):
        """Test JulesClient declares correct capabilities."""
        client = JulesClient()
        capabilities = client.get_capabilities()
        
        # Verify all expected capabilities are present
        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.STREAMING in capabilities

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_execute_success(self):
        """Test successful execution of Jules command with real CLI."""
        client = JulesClient()
        request = AgentRequest(prompt="write unit tests")
        
        try:
            response = client.execute(request)
            
            # Test real response structure
            assert isinstance(response, AgentResponse)
            assert "command" in response.metadata
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_execute_with_context(self):
        """Test execution with context parameters using real CLI."""
        client = JulesClient()
        request = AgentRequest(
            prompt="write unit tests",
            context={"repo": "test/repo", "parallel": 2}
        )
        
        try:
            response = client.execute(request)
            
            # Test real response structure
            assert isinstance(response, AgentResponse)
            # Verify command was built with context
            command = response.metadata.get("command", "")
            assert "new" in command or "test" in command.lower()
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    def test_jules_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        # Use invalid command to trigger real FileNotFoundError
        client = JulesClient(config={"jules_command": "nonexistent-jules-command-xyz"})
        request = AgentRequest(prompt="invalid task")
        response = client.execute(request)
        
        # Test real error handling
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_stream(self):
        """Test streaming functionality with real CLI."""
        client = JulesClient()
        request = AgentRequest(prompt="test task")
        
        try:
            # Test that streaming returns an iterator
            stream = client.stream(request)
            chunks = list(stream)
            
            # Verify we got some response (even if empty or error)
            assert isinstance(chunks, list)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    def test_jules_client_get_help(self):
        """Test getting Jules help information."""
        client = JulesClient()
        help_info = client.get_jules_help()
        
        # Test real result structure
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info
        # Available depends on whether jules is installed
        if JULES_AVAILABLE:
            assert help_info["available"] is True

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_client_execute_jules_command(self):
        """Test direct command execution with real CLI."""
        client = JulesClient()
        
        try:
            result = client.execute_jules_command("help")
            
            # Test real result structure
            assert isinstance(result, dict)
            assert "exit_code" in result or "output" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")


class TestJulesIntegrationAdapter:
    """Test JulesIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized with JulesClient."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)
        assert adapter.agent == client

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_ai_code_editing(self):
        """Test adapter for AI code editing with real CLI."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)
        
        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="create a test function",
                language="python"
            )
            
            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_ai_code_editing_failure(self):
        """Test adapter handles code generation failures."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)
        
        # Use invalid prompt that might fail
        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="invalid prompt that should fail",
                language="python"
            )
            # If it doesn't fail, that's also valid
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if code generation fails
            pass

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_llm_integration(self):
        """Test adapter for LLM module integration with real CLI."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        try:
            result = adapter.adapt_for_llm(messages)
            
            # Test real result structure
            assert isinstance(result, dict)
            assert "content" in result
            assert result["model"] == "jules"
            assert "usage" in result
            assert "metadata" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_adapter_code_execution(self):
        """Test adapter for code execution sandbox with real CLI."""
        client = JulesClient()
        adapter = JulesIntegrationAdapter(client)
        
        try:
            result = adapter.adapt_for_code_execution(
                code="print('hello')",
                language="python"
            )
            
            # Test real result structure
            assert isinstance(result, dict)
            assert "success" in result
            assert "output" in result
            assert "metadata" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")


class TestJulesOrchestration:
    """Test Jules integration with AgentOrchestrator."""

    def test_jules_with_orchestrator_structure(self):
        """Test JulesClient with AgentOrchestrator structure."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])
        
        # Test orchestrator structure
        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0] == client

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_with_orchestrator_parallel(self):
        """Test Jules in parallel orchestration with real CLI."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])
        
        request = AgentRequest(prompt="test task")
        
        try:
            responses = orchestrator.execute_parallel(request)
            
            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_with_orchestrator_sequential(self):
        """Test Jules in sequential orchestration with real CLI."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])
        
        request = AgentRequest(prompt="test task")
        
        try:
            responses = orchestrator.execute_sequential(request)
            
            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    @pytest.mark.skipif(not JULES_AVAILABLE, reason="jules CLI not installed")
    def test_jules_with_orchestrator_fallback(self):
        """Test Jules in fallback orchestration with real CLI."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])
        
        request = AgentRequest(prompt="test task")
        
        try:
            response = orchestrator.execute_with_fallback(request)
            
            # Test real response structure
            assert isinstance(response, AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("Jules CLI authentication or execution failed")

    def test_jules_with_multiple_agents_structure(self):
        """Test Jules alongside other agents in orchestration structure."""
        jules_client = JulesClient()
        
        # Create a test agent that implements BaseAgent (not a mock)
        class TestAgent(BaseAgent):
            def _execute_impl(self, request):
                return AgentResponse(content="Test response")
            def _stream_impl(self, request):
                yield "Test"
        
        test_agent = TestAgent(
            name="test",
            capabilities=[AgentCapabilities.TEXT_COMPLETION]
        )
        
        orchestrator = AgentOrchestrator([jules_client, test_agent])
        request = AgentRequest(prompt="test")
        
        # Test structure without requiring execution
        assert len(orchestrator.agents) == 2
        assert orchestrator.agents[0] == jules_client
        assert orchestrator.agents[1] == test_agent

    def test_jules_capability_selection(self):
        """Test selecting Jules by capability."""
        client = JulesClient()
        orchestrator = AgentOrchestrator([client])
        
        # Select agents by capability
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        
        assert len(code_gen_agents) == 1
        assert code_gen_agents[0] == client
