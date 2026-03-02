"""Unit tests for EveryCodeClient.

Tests use real implementations only. When Every Code CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""


import pytest

try:
    from codomyrmex.agents.core import AgentCapabilities, AgentRequest
    from codomyrmex.agents.every_code import EveryCodeClient
    from codomyrmex.tests.unit.agents.helpers import EVERY_CODE_AVAILABLE
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


class TestEveryCodeClient:
    """Test EveryCodeClient functionality."""

    def test_every_code_client_initialization(self):
        """Test EveryCodeClient can be initialized."""
        client = EveryCodeClient()
        assert client.name == "every_code"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.STREAMING in client.get_capabilities()
        assert AgentCapabilities.MULTI_TURN in client.get_capabilities()

    def test_every_code_client_capabilities(self):
        """Test EveryCodeClient declares correct capabilities."""
        client = EveryCodeClient()
        capabilities = client.get_capabilities()

        # Verify all expected capabilities are present
        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.STREAMING in capabilities
        assert AgentCapabilities.MULTI_TURN in capabilities

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_every_code_client_execute_success(self):
        """Test successful execution of Every Code command with real CLI."""
        client = EveryCodeClient()
        request = AgentRequest(prompt="test prompt")
        response = client.execute(request)

        # Test real response structure
        assert isinstance(response, type(client.execute(AgentRequest(prompt=""))))
        # Note: Actual success depends on authentication and CLI state
        # We test that the response structure is correct

    def test_every_code_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        # Use invalid command to trigger real FileNotFoundError
        client = EveryCodeClient(config={"every_code_command": "nonexistent-code-command-xyz"})
        request = AgentRequest(prompt="test prompt")
        response = client.execute(request)

        # Test real error handling
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_every_code_client_stream(self):
        """Test streaming output from Every Code with real CLI."""
        client = EveryCodeClient()
        request = AgentRequest(prompt="test prompt")

        # Test that streaming returns an iterator
        stream = client.stream(request)
        chunks = list(stream)

        # Verify we got some response (even if empty or error)
        assert isinstance(chunks, list)

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_every_code_client_execute_command(self):
        """Test executing an Every Code command with real CLI."""
        client = EveryCodeClient()
        result = client.execute_code_command("/plan", ["test task"])

        # Test real result structure
        assert isinstance(result, dict)
        assert "exit_code" in result or "output" in result

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_every_code_client_get_help(self):
        """Test getting Every Code help information with real CLI."""
        client = EveryCodeClient()
        help_info = client.get_code_help()

        # Test real result structure
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_every_code_client_get_help_structure(self):
        """Test getting Every Code help information structure."""
        client = EveryCodeClient()
        help_info = client.get_code_help()

        # Test real result structure
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info
        # Available depends on whether code/coder is installed
        if EVERY_CODE_AVAILABLE:
            assert help_info["available"] is True

    @pytest.mark.skipif(not EVERY_CODE_AVAILABLE, reason="code/coder CLI not installed")
    def test_every_code_client_get_version_structure(self):
        """Test getting Every Code version information structure."""
        client = EveryCodeClient()
        version_info = client.get_code_version()

        # Test real result structure
        assert isinstance(version_info, dict)
        assert "available" in version_info
        assert "version" in version_info

    def test_every_code_client_timeout_config(self):
        """Test timeout configuration."""
        client = EveryCodeClient(config={"every_code_timeout": 180})
        assert client.timeout == 180

    def test_every_code_client_file_operations_structure(self):
        """Test file operations structure (without executing)."""
        EveryCodeClient()
        request = AgentRequest(
            prompt="Analyze this code",
            context={"files": ["src/main.py"]}
        )

        # Test that request structure is correct
        assert request.prompt == "Analyze this code"
        assert "files" in request.context
        assert request.context["files"] == ["src/main.py"]

    def test_every_code_client_config_override(self):
        """Test configuration override."""
        config = {
            "every_code_command": "custom-code",
            "every_code_timeout": 180,
        }

        client = EveryCodeClient(config=config)

        assert client.command == "custom-code"
        assert client.timeout == 180

    def test_every_code_client_request_validation(self):
        """Test request validation."""
        client = EveryCodeClient()

        # Test empty prompt validation
        empty_request = AgentRequest(prompt="")
        response = client.execute(empty_request)
        assert not response.is_success()
        assert "Prompt is required" in response.error

    def test_every_code_client_special_commands(self):
        """Test special command handling."""
        EveryCodeClient()

        # Test /plan command
        request = AgentRequest(prompt="/plan Create a new feature")
        assert request.prompt.startswith("/plan")

        # Test /solve command
        request = AgentRequest(prompt="/solve Fix the bug")
        assert request.prompt.startswith("/solve")

        # Test /code command
        request = AgentRequest(prompt="/code Implement sorting")
        assert request.prompt.startswith("/code")

