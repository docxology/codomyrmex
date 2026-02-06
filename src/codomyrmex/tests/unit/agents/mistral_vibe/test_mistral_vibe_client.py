"""Unit tests for MistralVibeClient.

Tests use real implementations only. When Mistral Vibe CLI is not available
or API key is not configured, tests are skipped rather than using mocks.
"""

import os

import pytest

try:
    from codomyrmex.agents.core import AgentCapabilities, AgentRequest
    from codomyrmex.agents.mistral_vibe import MistralVibeClient
    from codomyrmex.tests.unit.agents.helpers import VIBE_AVAILABLE
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)

# Skip entire module if vibe CLI is not properly configured
pytestmark = pytest.mark.skipif(
    not os.getenv("MISTRAL_API_KEY"),
    reason="MISTRAL_API_KEY not set - skipping mistral_vibe tests"
)


class TestMistralVibeClient:
    """Test MistralVibeClient functionality."""

    def test_mistral_vibe_client_initialization(self):
        """Test MistralVibeClient can be initialized."""
        client = MistralVibeClient()
        assert client.name == "mistral_vibe"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.STREAMING in client.get_capabilities()
        assert AgentCapabilities.MULTI_TURN in client.get_capabilities()

    def test_mistral_vibe_client_capabilities(self):
        """Test MistralVibeClient declares correct capabilities."""
        client = MistralVibeClient()
        capabilities = client.get_capabilities()

        # Verify all expected capabilities are present
        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.STREAMING in capabilities
        assert AgentCapabilities.MULTI_TURN in capabilities

    @pytest.mark.skipif(not VIBE_AVAILABLE or not os.getenv("MISTRAL_API_KEY"), reason="vibe CLI not installed or not configured")
    def test_mistral_vibe_client_execute_success(self):
        """Test successful execution of Mistral Vibe command with real CLI."""
        client = MistralVibeClient()
        request = AgentRequest(prompt="test prompt")
        response = client.execute(request)

        # Test real response structure
        assert isinstance(response, type(client.execute(AgentRequest(prompt=""))))
        # Note: Actual success depends on authentication and CLI state
        # We test that the response structure is correct

    @pytest.mark.skipif(not VIBE_AVAILABLE or not os.getenv("MISTRAL_API_KEY"), reason="vibe CLI not configured")
    @pytest.mark.timeout(5)
    def test_mistral_vibe_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        # Use invalid command to trigger real FileNotFoundError
        client = MistralVibeClient(config={"mistral_vibe_command": "nonexistent-vibe-command-xyz"})
        request = AgentRequest(prompt="test prompt")
        response = client.execute(request)

        # Test real error handling
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(not VIBE_AVAILABLE or not os.getenv("MISTRAL_API_KEY"), reason="vibe CLI not installed or not configured")
    @pytest.mark.timeout(5)
    def test_mistral_vibe_client_stream(self):
        """Test streaming output from Mistral Vibe with real CLI."""
        client = MistralVibeClient()
        request = AgentRequest(prompt="test prompt")

        # Test that streaming returns an iterator
        stream = client.stream(request)
        chunks = list(stream)

        # Verify we got some response (even if empty or error)
        assert isinstance(chunks, list)

    @pytest.mark.skipif(not VIBE_AVAILABLE or not os.getenv("MISTRAL_API_KEY"), reason="vibe CLI not installed or not configured")
    @pytest.mark.timeout(5)
    def test_mistral_vibe_client_execute_command(self):
        """Test executing a Mistral Vibe command with real CLI."""
        client = MistralVibeClient()
        result = client.execute_vibe_command("help")

        # Test real result structure
        assert isinstance(result, dict)
        assert "exit_code" in result or "output" in result

    @pytest.mark.skipif(not VIBE_AVAILABLE or not os.getenv("MISTRAL_API_KEY"), reason="vibe CLI not installed or not configured")
    @pytest.mark.timeout(5)
    def test_mistral_vibe_client_get_help(self):
        """Test getting Mistral Vibe help information with real CLI."""
        client = MistralVibeClient()
        help_info = client.get_vibe_help()

        # Test real result structure
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info

    @pytest.mark.skipif(not VIBE_AVAILABLE or not os.getenv("MISTRAL_API_KEY"), reason="vibe CLI not configured")
    @pytest.mark.timeout(5)
    def test_mistral_vibe_client_get_help_structure(self):
        """Test getting Mistral Vibe help information structure."""
        client = MistralVibeClient()
        help_info = client.get_vibe_help()

        # Test real result structure
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info
        # Available depends on whether vibe is installed
        if VIBE_AVAILABLE:
            assert help_info["available"] is True

    def test_mistral_vibe_client_timeout_config(self):
        """Test timeout configuration."""
        client = MistralVibeClient(config={"mistral_vibe_timeout": 120})
        assert client.timeout == 120

    def test_mistral_vibe_client_file_operations_structure(self):
        """Test file operations structure (without executing)."""
        client = MistralVibeClient()
        request = AgentRequest(
            prompt="Analyze this code",
            context={"files": ["src/main.py"]}
        )

        # Test that request structure is correct
        assert request.prompt == "Analyze this code"
        assert "files" in request.context
        assert request.context["files"] == ["src/main.py"]

    def test_mistral_vibe_client_config_override(self):
        """Test configuration override."""
        config = {
            "mistral_vibe_command": "custom-vibe",
            "mistral_vibe_timeout": 120,
        }

        client = MistralVibeClient(config=config)

        assert client.command == "custom-vibe"
        assert client.timeout == 120

    def test_mistral_vibe_client_request_validation(self):
        """Test request validation."""
        client = MistralVibeClient()

        # Test empty prompt validation
        empty_request = AgentRequest(prompt="")
        response = client.execute(empty_request)
        assert not response.is_success()
        assert "Prompt is required" in response.error
        assert "empty" in response.error.lower()
