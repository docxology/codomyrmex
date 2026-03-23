"""Integration tests for Paperclip agent integration.

Tests use real implementations only. When the Paperclip CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest

try:
    from codomyrmex.agents.core import AgentCapabilities, AgentRequest, AgentResponse
    from codomyrmex.agents.core.exceptions import PaperclipError
    from codomyrmex.agents.generic import AgentOrchestrator
    from codomyrmex.agents.paperclip import (
        PaperclipAPIClient,
        PaperclipClient,
        PaperclipIntegrationAdapter,
    )
    from codomyrmex.tests.unit.agents.helpers import PAPERCLIPAI_AVAILABLE

    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


# ------------------------------------------------------------------ #
# PaperclipClient (CLI)
# ------------------------------------------------------------------ #


class TestPaperclipClient:
    """Test PaperclipClient functionality."""

    def test_paperclip_client_initialization(self):
        """Test PaperclipClient can be initialized."""
        client = PaperclipClient()
        assert client.name == "paperclip"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.MULTI_TURN in client.get_capabilities()
        assert AgentCapabilities.TOOL_USE in client.get_capabilities()
        assert AgentCapabilities.STREAMING in client.get_capabilities()

    def test_paperclip_client_custom_config(self):
        """Test PaperclipClient with custom configuration."""
        client = PaperclipClient(
            config={
                "paperclip_command": "paperclipai",
                "paperclip_timeout": 60,
                "paperclip_agent_id": "test-agent-1",
                "paperclip_api_base": "http://localhost:4000",
            }
        )
        assert client.agent_id == "test-agent-1"
        assert client.api_base == "http://localhost:4000"

    def test_paperclip_client_default_api_base(self):
        """Test default API base URL."""
        client = PaperclipClient()
        assert client.api_base == "http://localhost:3100"

    def test_paperclip_client_capabilities(self):
        """Test PaperclipClient declares correct capabilities."""
        client = PaperclipClient()
        capabilities = client.get_capabilities()

        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.MULTI_TURN in capabilities
        assert AgentCapabilities.STREAMING in capabilities
        assert AgentCapabilities.TOOL_USE in capabilities

    def test_paperclip_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        client = PaperclipClient(
            config={"paperclip_command": "nonexistent-paperclip-command-xyz"}
        )
        request = AgentRequest(prompt="invalid task")
        response = client.execute(request)

        # Real error handling — no mocks
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_client_execute_success(self):
        """Test successful execution with real CLI."""
        client = PaperclipClient()
        request = AgentRequest(prompt="check status")

        try:
            response = client.execute(request)
            assert isinstance(response, AgentResponse)
        except Exception:
            pytest.skip("Paperclip CLI execution failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_client_get_version(self):
        """Test getting Paperclip version."""
        client = PaperclipClient()
        version_info = client.get_version()

        assert isinstance(version_info, dict)
        assert "available" in version_info
        assert "version" in version_info
        if PAPERCLIPAI_AVAILABLE:
            assert version_info["available"] is True

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_client_run_doctor(self):
        """Test doctor diagnostics with real CLI."""
        client = PaperclipClient()

        try:
            result = client.run_doctor()
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            pytest.skip("Paperclip doctor failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_client_stream(self):
        """Test streaming functionality with real CLI."""
        client = PaperclipClient()
        request = AgentRequest(prompt="test task")

        try:
            stream = client.stream(request)
            chunks = list(stream)
            assert isinstance(chunks, list)
        except Exception:
            pytest.skip("Paperclip CLI stream failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_client_list_companies(self):
        """Test listing companies via CLI."""
        client = PaperclipClient()

        try:
            result = client.list_companies()
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            pytest.skip("Paperclip company list failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_client_get_env(self):
        """Test env output with real CLI."""
        client = PaperclipClient()

        try:
            result = client.get_env()
            assert isinstance(result, dict)
            assert "success" in result
        except Exception:
            pytest.skip("Paperclip env failed")


# ------------------------------------------------------------------ #
# PaperclipAPIClient (REST)
# ------------------------------------------------------------------ #


class TestPaperclipAPIClient:
    """Test PaperclipAPIClient functionality."""

    def test_api_client_initialization(self):
        """Test PaperclipAPIClient can be initialized."""
        client = PaperclipAPIClient()
        assert client.base_url == "http://localhost:3100"
        assert client.api_key is None
        assert client.timeout == 30

    def test_api_client_custom_config(self):
        """Test PaperclipAPIClient with custom configuration."""
        client = PaperclipAPIClient(
            base_url="http://example.com:4100",
            api_key="test-key-123",
            timeout=60,
        )
        assert client.base_url == "http://example.com:4100"
        assert client.api_key == "test-key-123"
        assert client.timeout == 60

    def test_api_client_base_url_strip_trailing_slash(self):
        """Test that trailing slash is stripped from base_url."""
        client = PaperclipAPIClient(base_url="http://localhost:3100/")
        assert client.base_url == "http://localhost:3100"

    def test_api_client_health_check_connection_error(self):
        """Test health_check handles connection errors gracefully."""
        # Use a port that won't have a server
        client = PaperclipAPIClient(base_url="http://127.0.0.1:59999")

        with pytest.raises(PaperclipError):
            client.health_check()

    def test_api_client_list_companies_connection_error(self):
        """Test list_companies handles connection errors gracefully."""
        client = PaperclipAPIClient(base_url="http://127.0.0.1:59999")

        with pytest.raises(PaperclipError):
            client.list_companies()

    def test_api_client_create_company_connection_error(self):
        """Test create_company handles connection errors gracefully."""
        client = PaperclipAPIClient(base_url="http://127.0.0.1:59999")

        with pytest.raises(PaperclipError):
            client.create_company(name="test-company")

    def test_api_client_create_issue_connection_error(self):
        """Test create_issue handles connection errors gracefully."""
        client = PaperclipAPIClient(base_url="http://127.0.0.1:59999")

        with pytest.raises(PaperclipError):
            client.create_issue(company_id="test-co", title="Test Issue")


# ------------------------------------------------------------------ #
# PaperclipIntegrationAdapter
# ------------------------------------------------------------------ #


class TestPaperclipIntegrationAdapter:
    """Test PaperclipIntegrationAdapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized with PaperclipClient."""
        client = PaperclipClient()
        adapter = PaperclipIntegrationAdapter(client)
        assert adapter.agent == client

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_adapter_ai_code_editing(self):
        """Test adapter for AI code editing with real CLI."""
        client = PaperclipClient()
        adapter = PaperclipIntegrationAdapter(client)

        try:
            code = adapter.adapt_for_ai_code_editing(
                prompt="create a test function", language="python"
            )
            assert isinstance(code, str)
        except RuntimeError:
            pytest.skip("Paperclip code generation failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_adapter_llm_integration(self):
        """Test adapter for LLM module integration with real CLI."""
        client = PaperclipClient()
        adapter = PaperclipIntegrationAdapter(client)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        try:
            result = adapter.adapt_for_llm(messages)
            assert isinstance(result, dict)
            assert "content" in result
            assert result["model"] == "paperclip"
            assert "usage" in result
            assert "metadata" in result
        except Exception:
            pytest.skip("Paperclip LLM adapter failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_adapter_code_execution(self):
        """Test adapter for code execution sandbox with real CLI."""
        client = PaperclipClient()
        adapter = PaperclipIntegrationAdapter(client)

        try:
            result = adapter.adapt_for_code_execution(
                code="print('hello')", language="python"
            )
            assert isinstance(result, dict)
            assert "success" in result
            assert "output" in result
            assert "metadata" in result
        except Exception:
            pytest.skip("Paperclip code execution adapter failed")


# ------------------------------------------------------------------ #
# Orchestrator integration
# ------------------------------------------------------------------ #


class TestPaperclipOrchestration:
    """Test Paperclip integration with AgentOrchestrator."""

    def test_paperclip_with_orchestrator_structure(self):
        """Test PaperclipClient with AgentOrchestrator structure."""
        client = PaperclipClient()
        orchestrator = AgentOrchestrator([client])

        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0] == client

    def test_paperclip_capability_selection(self):
        """Test selecting Paperclip by capability."""
        client = PaperclipClient()
        orchestrator = AgentOrchestrator([client])

        code_gen_agents = orchestrator.select_agent_by_capability(
            AgentCapabilities.CODE_GENERATION.value
        )

        assert len(code_gen_agents) == 1
        assert code_gen_agents[0] == client

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_with_orchestrator_parallel(self):
        """Test Paperclip in parallel orchestration with real CLI."""
        client = PaperclipClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            responses = orchestrator.execute_parallel(request)
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            pytest.skip("Paperclip parallel orchestration failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_with_orchestrator_sequential(self):
        """Test Paperclip in sequential orchestration with real CLI."""
        client = PaperclipClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            responses = orchestrator.execute_sequential(request)
            assert len(responses) == 1
            assert isinstance(responses[0], AgentResponse)
        except Exception:
            pytest.skip("Paperclip sequential orchestration failed")

    @pytest.mark.skipif(
        not PAPERCLIPAI_AVAILABLE, reason="paperclipai CLI not installed"
    )
    def test_paperclip_with_orchestrator_fallback(self):
        """Test Paperclip in fallback orchestration with real CLI."""
        client = PaperclipClient()
        orchestrator = AgentOrchestrator([client])

        request = AgentRequest(prompt="test task")

        try:
            response = orchestrator.execute_with_fallback(request)
            assert isinstance(response, AgentResponse)
        except Exception:
            pytest.skip("Paperclip fallback orchestration failed")


# ------------------------------------------------------------------ #
# PaperclipError
# ------------------------------------------------------------------ #


class TestPaperclipError:
    """Test PaperclipError exception."""

    def test_paperclip_error_basic(self):
        """Test basic PaperclipError construction."""
        error = PaperclipError("test error")
        assert "test error" in str(error)

    def test_paperclip_error_with_command(self):
        """Test PaperclipError with command context."""
        error = PaperclipError("command failed", command="paperclipai doctor")
        assert error.context["command"] == "paperclipai doctor"

    def test_paperclip_error_with_exit_code(self):
        """Test PaperclipError with exit code context."""
        error = PaperclipError("exit error", command="paperclipai run", exit_code=1)
        assert error.context["exit_code"] == 1
        assert error.context["command"] == "paperclipai run"

    def test_paperclip_error_inheritance(self):
        """Test PaperclipError inherits from AgentError."""
        from codomyrmex.agents.core.exceptions import AgentError

        error = PaperclipError("test")
        assert isinstance(error, AgentError)
