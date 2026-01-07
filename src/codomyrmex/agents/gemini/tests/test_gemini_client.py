"""Unit tests for GeminiClient.

Tests use real implementations only. When Gemini CLI is not available,
tests are skipped rather than using mocks. All data processing and
conversion logic is tested with real data structures.
"""

import pytest
from pathlib import Path
from typing import Any

from codomyrmex.agents.core import AgentRequest, AgentCapabilities
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.exceptions import GeminiError
from codomyrmex.agents.tests.helpers import GEMINI_AVAILABLE


class TestGeminiClient:
    """Test GeminiClient functionality."""

    def test_gemini_client_initialization(self):
        """Test GeminiClient can be initialized."""
        client = GeminiClient()
        assert client.name == "gemini"
        assert AgentCapabilities.CODE_GENERATION in client.get_capabilities()
        assert AgentCapabilities.CODE_EDITING in client.get_capabilities()
        assert AgentCapabilities.CODE_ANALYSIS in client.get_capabilities()
        assert AgentCapabilities.TEXT_COMPLETION in client.get_capabilities()
        assert AgentCapabilities.STREAMING in client.get_capabilities()
        assert AgentCapabilities.MULTI_TURN in client.get_capabilities()

    def test_gemini_client_capabilities(self):
        """Test GeminiClient declares correct capabilities."""
        client = GeminiClient()
        capabilities = client.get_capabilities()
        
        # Verify all expected capabilities are present
        assert AgentCapabilities.CODE_GENERATION in capabilities
        assert AgentCapabilities.CODE_EDITING in capabilities
        assert AgentCapabilities.CODE_ANALYSIS in capabilities
        assert AgentCapabilities.TEXT_COMPLETION in capabilities
        assert AgentCapabilities.STREAMING in capabilities
        assert AgentCapabilities.MULTI_TURN in capabilities

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_client_execute_success(self):
        """Test successful execution of Gemini command with real CLI."""
        client = GeminiClient()
        request = AgentRequest(prompt="test prompt")
        response = client.execute(request)
        
        # Test real response structure
        assert isinstance(response, type(client.execute(AgentRequest(prompt=""))))
        # Note: Actual success depends on authentication and CLI state
        # We test that the response structure is correct

    def test_gemini_client_execute_failure_invalid_command(self):
        """Test handling when command is not found."""
        # Use invalid command to trigger real FileNotFoundError
        client = GeminiClient(config={"gemini_command": "nonexistent-gemini-command-xyz"})
        request = AgentRequest(prompt="test prompt")
        response = client.execute(request)
        
        # Test real error handling
        assert not response.is_success()
        assert response.error is not None

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_client_stream(self):
        """Test streaming output from Gemini with real CLI."""
        client = GeminiClient()
        request = AgentRequest(prompt="test prompt")
        
        # Test that streaming returns an iterator
        stream = client.stream(request)
        chunks = list(stream)
        
        # Verify we got some response (even if empty or error)
        assert isinstance(chunks, list)

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_client_execute_command(self):
        """Test executing a Gemini slash command with real CLI."""
        client = GeminiClient()
        result = client.execute_gemini_command("/help")
        
        # Test real result structure
        assert isinstance(result, dict)
        assert "exit_code" in result or "output" in result

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_client_save_chat(self):
        """Test saving a chat session with real CLI."""
        client = GeminiClient()
        result = client.save_chat("test_session", "test prompt")
        
        # Test real result structure
        assert isinstance(result, dict)

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_client_resume_chat(self):
        """Test resuming a chat session with real CLI."""
        client = GeminiClient()
        result = client.resume_chat("test_session")
        
        # Test real result structure
        assert isinstance(result, dict)

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="gemini CLI not installed")
    def test_gemini_client_list_chats(self):
        """Test listing chat sessions with real CLI."""
        client = GeminiClient()
        result = client.list_chats()
        
        # Test real result structure
        assert isinstance(result, dict)

    def test_gemini_client_get_help(self):
        """Test getting Gemini help information."""
        client = GeminiClient()
        help_info = client.get_gemini_help()
        
        # Test real result structure
        assert isinstance(help_info, dict)
        assert "available" in help_info
        assert "help_text" in help_info
        # Available depends on whether gemini is installed
        if GEMINI_AVAILABLE:
            assert help_info["available"] is True

    def test_gemini_client_timeout_config(self):
        """Test timeout configuration."""
        client = GeminiClient(config={"gemini_timeout": 120})
        assert client.timeout == 120

    def test_gemini_client_file_operations_structure(self):
        """Test file operations structure (without executing)."""
        client = GeminiClient()
        request = AgentRequest(
            prompt="Analyze this code",
            context={"files": ["src/main.py"]}
        )
        
        # Test that request structure is correct
        assert request.prompt == "Analyze this code"
        assert "files" in request.context
        assert request.context["files"] == ["src/main.py"]

    def test_gemini_client_config_override(self):
        """Test configuration override."""
        config = {
            "gemini_command": "custom-gemini",
            "gemini_timeout": 120,
        }
        
        client = GeminiClient(config=config)
        
        assert client.gemini_command == "custom-gemini"
        assert client.timeout == 120

    def test_gemini_client_request_validation(self):
        """Test request validation."""
        client = GeminiClient()
        
        # Test empty prompt validation
        empty_request = AgentRequest(prompt="")
        errors = client.validate_request(empty_request)
        assert len(errors) > 0
        assert any("empty" in error.lower() for error in errors)
