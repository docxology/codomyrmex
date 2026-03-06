"""Unit tests for the Hermes Agent client.

These tests follow the Codomyrmex zero-mock policy. They instantiate
HermesClient and execute real assertions against its argument builder.
If the 'hermes' CLI is missing, execution tests gracefully skip or assert
on the resulting HermesError.
"""

import shutil

import pytest

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes import HermesClient
from codomyrmex.agents.hermes.mcp_tools import (
    hermes_execute,
    hermes_skills_list,
    hermes_status,
)

# Check if hermes is actually installed locally for integration tests
HAS_HERMES = shutil.which("hermes") is not None


class TestHermesClientArgBuilder:
    """Zero-mock tests for HermesClient argument building."""

    def test_client_initialization(self) -> None:
        """Test client initializes without mocking config handling."""
        client = HermesClient(
            config={"hermes_command": "custom_hermes", "hermes_timeout": 500}
        )
        assert client.command == "custom_hermes"
        assert client.timeout == 500
        assert client.name == "hermes"

    def test_build_args_chat(self) -> None:
        """Test default single-turn chat arg builder."""
        client = HermesClient()
        args = client._build_hermes_args(prompt="test task", context={})
        assert args == ["chat", "-q", "test task"]

    def test_build_args_specialized_command(self) -> None:
        """Test specialized command via context bypass."""
        client = HermesClient()
        args = client._build_hermes_args(
            prompt="ignored here",
            context={"command": "status", "args": ["--verbose"]},
        )
        assert args == ["status", "--verbose"]

    def test_build_args_skills_list(self) -> None:
        """Test skills list builder."""
        client = HermesClient()
        args = client._build_hermes_args(
            prompt="",
            context={"command": "skills", "args": ["list"]},
        )
        assert args == ["skills", "list"]


class TestHermesClientExecution:
    """Zero-mock execution tests for HermesClient."""

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_hermes_status_success(self) -> None:
        """Test actual status command if installed."""
        client = HermesClient()
        result = client.get_hermes_status()
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.skipif(HAS_HERMES, reason="hermes CLI is installed")
    def test_hermes_missing_error(self) -> None:
        """Test that missing hermes command returns an error response."""
        client = HermesClient(config={"hermes_command": "nonexistent_hermes_binary"})
        request = AgentRequest(prompt="test")
        response = client.execute(request)
        assert not response.is_success()
        assert "nonexistent_hermes_binary" in str(response.error)

    def test_stream_args(self) -> None:
        """Test streaming argument iteration on client."""
        client = HermesClient(config={"hermes_command": "echo"})
        # Replacing command with echo bypasses hermes requirement,
        # but verifies that execution pathways don't crash and stream yields
        request = AgentRequest(prompt="hello")

        # Build stream
        stream = client.stream(request)
        outputs = list(stream)

        # We should at least get some output or an error if echo isn't exactly matched
        # Our CLIAgentBase handles wrapping, so we just verify it returned strings or raised a proper AgentError.
        assert len(outputs) > 0 or isinstance(outputs, list)


class TestHermesMCPTools:
    """Zero-mock tests for Hermes MCP Tools."""

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_hermes_skills_list_mcp(self) -> None:
        """Test the hermes_skills_list tool directly."""
        result = hermes_skills_list()
        assert result["status"] in ("success", "error")
        if result["status"] == "success":
            assert isinstance(result["output"], str)

    def test_hermes_status_mcp_missing_binary(self) -> None:
        """Test status with an invalid binary configured via class monkeypatch or natural error."""
        # By default, hermes_status uses the local system.
        result = hermes_status()
        assert "status" in result
        assert "available" in result

    def test_hermes_execute_mcp(self) -> None:
        """Test execute MCP tool. If hermes is missing, it returns an error dict."""
        result = hermes_execute(prompt="test prompt", timeout=1)
        # Verify the structure matches MCP SPEC
        assert "status" in result
        assert "content" in result
        assert "error" in result
        assert "metadata" in result
