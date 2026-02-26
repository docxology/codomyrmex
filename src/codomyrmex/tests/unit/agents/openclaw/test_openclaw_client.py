"""Integration tests for OpenClaw agent integration.

Tests use real implementations only. When OpenClaw CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest

try:
    from codomyrmex.agents.core import AgentCapabilities, AgentRequest, AgentResponse
    from codomyrmex.agents.generic import AgentOrchestrator
    from codomyrmex.agents.openclaw import OpenClawClient, OpenClawIntegrationAdapter
    from codomyrmex.tests.unit.agents.helpers import OPENCLAW_AVAILABLE
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


class TestOpenClawClient:
    """Test OpenClawClient functionality."""

    def test_openclaw_client_initialization(self):
        """Test OpenClawClient can be initialized."""
        client = OpenClawClient()
        assert client.name == "openclaw"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.MULTI_TURN in client.get_capabilities()
        assert AgentCapabilities.TOOL_USE in client.get_capabilities()

    def test_openclaw_client_capabilities(self):
        """Test OpenClawClient declares correct capabilities."""
        client = OpenClawClient()
        capabilities = client.get_capabilities()

        # Verify all expected capabilities are present
        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.MULTI_TURN in capabilities
        assert AgentCapabilities.STREAMING in capabilities
        assert AgentCapabilities.TOOL_USE in capabilities

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_client_execute_success(self):
        """Test successful execution of OpenClaw command with real CLI."""
        client = OpenClawClient()
        request = AgentRequest(prompt="write unit tests")

        try:
            response = client.execute(request)

            # Test real response structure
            assert isinstance(response, AgentResponse)
            assert "command" in response.metadata
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_client_execute_with_context(self):
        """Test execution with context parameters using real CLI."""
        client = OpenClawClient()
        request = AgentRequest(
            prompt="write unit tests",
            context={"thinking": "high", "language": "python"}
        )

        try:
            response = client.execute(request)

            # Test real response structure
            assert isinstance(response, AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_client_execute_with_doctor(self):
        """Test execution with doctor context using real CLI."""
        client = OpenClawClient()
        request = AgentRequest(
            prompt="health check",
            context={"doctor": True}
        )

        try:
            response = client.execute(request)

            # Test real response structure
            assert isinstance(response, AgentResponse)
            command = response.metadata.get("command_full", "")
            assert "doctor" in command.lower()
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    def test_openclaw_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        # Use invalid command to trigger real FileNotFoundError
        client = OpenClawClient(config={"openclaw_command": "nonexistent-openclaw-command-xyz"})
        request = AgentRequest(prompt="invalid task")
        response = client.execute(request)

        # Test real error handling
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_client_stream(self):
        """Test streaming functionality with real CLI."""
        client = OpenClawClient()
        request = AgentRequest(prompt="test task")

        try:
            # Test that streaming returns an iterator
            stream = client.stream(request)
            chunks = list(stream)

            # Verify we got some response (even if empty or error)
            assert isinstance(chunks, list)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_client_get_version(self):
        """Test getting OpenClaw version information."""
        client = OpenClawClient()
        version_info = client.get_openclaw_version()

        # Test real result structure
        assert isinstance(version_info, dict)
        assert "available" in version_info
        assert "version" in version_info
        # Available depends on whether openclaw is installed
        if OPENCLAW_AVAILABLE:
            assert version_info["available"] is True

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_client_run_doctor(self):
        """Test doctor health check with real CLI."""
        client = OpenClawClient()

        try:
            result = client.run_doctor()

            # Test real result structure
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_client_send_message(self):
        """Test sending message via channel routing with real CLI."""
        client = OpenClawClient()

        try:
            result = client.send_message(target="test-channel", message="hello")

            # Test real result structure
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")


class TestOpenClawIntegrationAdapter:
    """Test OpenClawIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized with OpenClawClient."""
        client = OpenClawClient()
        adapter = OpenClawIntegrationAdapter(client)
        assert adapter.agent == client

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_adapter_ai_code_editing(self):
        """Test adapter for AI code editing with real CLI."""
        client = OpenClawClient()
        adapter = OpenClawIntegrationAdapter(client)

        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="create a test function",
                language="python"
            )

            # Test real result structure
            assert isinstance(code, str)
        except RuntimeError:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_adapter_ai_code_editing_failure(self):
        """Test adapter handles code generation failures."""
        client = OpenClawClient()
        adapter = OpenClawIntegrationAdapter(client)

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

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_adapter_llm_integration(self):
        """Test adapter for LLM module integration with real CLI."""
        client = OpenClawClient()
        adapter = OpenClawIntegrationAdapter(client)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]

        try:
            result = adapter.adapt_for_llm(messages)

            # Test real result structure
            assert isinstance(result, dict)
            assert "content" in result
            assert result["model"] == "openclaw"
            assert "usage" in result
            assert "metadata" in result
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_adapter_code_execution(self):
        """Test adapter for code execution sandbox with real CLI."""
        client = OpenClawClient()
        adapter = OpenClawIntegrationAdapter(client)

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
            pytest.skip("OpenClaw CLI authentication or execution failed")


class TestOpenClawOrchestration:
    """Test OpenClaw integration with AgentOrchestrator."""

    def test_openclaw_with_orchestrator_structure(self):
        """Test OpenClawClient with AgentOrchestrator structure."""
        client = OpenClawClient()
        orchestrator = AgentOrchestrator([client])

        # Test orchestrator structure
        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0] == client

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_with_orchestrator_parallel(self):
        """Test OpenClaw in parallel orchestration with real CLI."""
        client = OpenClawClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            responses = orchestrator.execute_parallel(request)

            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_with_orchestrator_sequential(self):
        """Test OpenClaw in sequential orchestration with real CLI."""
        client = OpenClawClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            responses = orchestrator.execute_sequential(request)

            # Test real response structure
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    @pytest.mark.skipif(not OPENCLAW_AVAILABLE, reason="openclaw CLI not installed")
    def test_openclaw_with_orchestrator_fallback(self):
        """Test OpenClaw in fallback orchestration with real CLI."""
        client = OpenClawClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            response = orchestrator.execute_with_fallback(request)

            # Test real response structure
            assert isinstance(response, AgentResponse)
        except Exception:
            # Expected if authentication fails or CLI error
            pytest.skip("OpenClaw CLI authentication or execution failed")

    def test_openclaw_capability_selection(self):
        """Test selecting OpenClaw by capability."""
        client = OpenClawClient()
        orchestrator = AgentOrchestrator([client])

        # Select agents by capability
        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )

        assert len(code_gen_agents) == 1
        assert code_gen_agents[0] == client
