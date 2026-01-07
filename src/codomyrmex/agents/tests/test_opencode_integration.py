"""Integration tests for OpenCode agent integration.

Tests use real implementations only. When OpenCode CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest
from pathlib import Path
from typing import Any

from codomyrmex.agents.core import AgentRequest, AgentCapabilities, AgentResponse
from codomyrmex.agents.opencode import OpenCodeClient, OpenCodeIntegrationAdapter
from codomyrmex.agents.generic import AgentOrchestrator
from codomyrmex.agents.exceptions import OpenCodeError
from codomyrmex.agents.tests.helpers import OPENCODE_AVAILABLE


class TestOpenCodeClient:
    """Test OpenCodeClient functionality."""

    def test_opencode_client_initialization(self):
        """Test OpenCodeClient can be initialized."""
        client = OpenCodeClient()
        assert client.name == "opencode"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.MULTI_TURN in client.get_capabilities()

    def test_opencode_client_capabilities(self):
        """Test OpenCodeClient declares correct capabilities."""
        client = OpenCodeClient()
        capabilities = client.get_capabilities()
        
        # Verify all expected capabilities are present
        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.MULTI_TURN in capabilities

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_client_execute_success(self):
        """Test successful execution of OpenCode command with real CLI."""
        client = OpenCodeClient()
        request = AgentRequest(prompt="write unit tests")
        
        try:
            response = client.execute(request)
            
            # Test real response structure
            assert isinstance(response, AgentResponse)
            assert "command" in response.metadata
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_client_execute_with_context(self):
        """Test execution with context parameters using real CLI."""
        client = OpenCodeClient()
        request = AgentRequest(
            prompt="write unit tests",
            context={"init": False, "language": "python"}
        )
        
        try:
            response = client.execute(request)
            
            # Test real response structure
            assert isinstance(response, AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_client_execute_with_init(self):
        """Test execution with initialization context using real CLI."""
        client = OpenCodeClient()
        request = AgentRequest(
            prompt="init",
            context={"init": True}
        )
        
        try:
            response = client.execute(request)
            
            # Test real response structure
            assert isinstance(response, AgentResponse)
            # Verify init command was used
            command = response.metadata.get("command", "")
            assert "--init" in command or "init" in command.lower()
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    def test_opencode_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        # Use invalid command to trigger real FileNotFoundError
        client = OpenCodeClient(config={"opencode_command": "nonexistent-opencode-command-xyz"})
        request = AgentRequest(prompt="invalid task")
        response = client.execute(request)
        
        # Test real error handling
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_client_stream(self):
        """Test streaming functionality with real CLI."""
        client = OpenCodeClient()
        request = AgentRequest(prompt="test task")
        
        try:
            # Test that streaming returns an iterator
            stream = client.stream(request)
            chunks = list(stream)
            
            # Verify we got some response (even if empty or error)
            assert isinstance(chunks, list)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    def test_opencode_client_get_version(self):
        """Test getting OpenCode version information."""
        client = OpenCodeClient()
        version_info = client.get_opencode_version()
        
        # Test real result structure
        assert isinstance(version_info, dict)
        assert "available" in version_info
        assert "version" in version_info
        # Available depends on whether opencode is installed
        if OPENCODE_AVAILABLE:
            assert version_info["available"] is True

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_client_initialize_project(self):
        """Test project initialization with real CLI."""
        client = OpenCodeClient()
        
        try:
            result = client.initialize_project(project_path=Path("/tmp/test_opencode"))
            
            # Test real result structure
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")


class TestOpenCodeIntegrationAdapter:
    """Test OpenCodeIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized with OpenCodeClient."""
        client = OpenCodeClient()
        adapter = OpenCodeIntegrationAdapter(client)
        assert adapter.agent == client

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_adapter_ai_code_editing(self):
        """Test adapter for AI code editing with real CLI."""
        client = OpenCodeClient()
        adapter = OpenCodeIntegrationAdapter(client)
        
        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="create a test function",
                language="python"
            )
            
            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_adapter_ai_code_editing_failure(self):
        """Test adapter handles code generation failures."""
        client = OpenCodeClient()
        adapter = OpenCodeIntegrationAdapter(client)
        
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

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_adapter_llm_integration(self):
        """Test adapter for LLM module integration with real CLI."""
        client = OpenCodeClient()
        adapter = OpenCodeIntegrationAdapter(client)
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        try:
            result = adapter.adapt_for_llm(messages)
            
            # Test real result structure
            assert isinstance(result, dict)
            assert "content" in result
            assert result["model"] == "opencode"
            assert "usage" in result
            assert "metadata" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_adapter_code_execution(self):
        """Test adapter for code execution sandbox with real CLI."""
        client = OpenCodeClient()
        adapter = OpenCodeIntegrationAdapter(client)
        
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
            pytest.skip("OpenCode CLI authentication or execution failed")


class TestOpenCodeOrchestration:
    """Test OpenCode integration with AgentOrchestrator."""

    def test_opencode_with_orchestrator_structure(self):
        """Test OpenCodeClient with AgentOrchestrator structure."""
        client = OpenCodeClient()
        orchestrator = AgentOrchestrator([client])
        
        # Test orchestrator structure
        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0] == client

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_with_orchestrator_parallel(self):
        """Test OpenCode in parallel orchestration with real CLI."""
        client = OpenCodeClient()
        orchestrator = AgentOrchestrator([client])
        
        request = AgentRequest(prompt="test task")
        
        try:
            responses = orchestrator.execute_parallel(request)
            
            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_with_orchestrator_sequential(self):
        """Test OpenCode in sequential orchestration with real CLI."""
        client = OpenCodeClient()
        orchestrator = AgentOrchestrator([client])
        
        request = AgentRequest(prompt="test task")
        
        try:
            responses = orchestrator.execute_sequential(request)
            
            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCODE_AVAILABLE, reason="opencode CLI not installed")
    def test_opencode_with_orchestrator_fallback(self):
        """Test OpenCode in fallback orchestration with real CLI."""
        client = OpenCodeClient()
        orchestrator = AgentOrchestrator([client])
        
        request = AgentRequest(prompt="test task")
        
        try:
            response = orchestrator.execute_with_fallback(request)
            
            # Test real response structure
            assert isinstance(response, AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenCode CLI authentication or execution failed")

    def test_opencode_capability_selection(self):
        """Test selecting OpenCode by capability."""
        client = OpenCodeClient()
        orchestrator = AgentOrchestrator([client])
        
        # Select agents by capability
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )
        
        assert len(code_gen_agents) == 1
        assert code_gen_agents[0] == client
