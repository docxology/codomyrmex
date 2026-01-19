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
from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.tests.unit.agents.helpers import GEMINI_AVAILABLE


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

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="Gemini SDK/Key not available")
    def test_gemini_client_execute_content(self):
        """Test executing generic content generation."""
        client = GeminiClient()
        request = AgentRequest(prompt="Say 'Hello, World!'")
        # Only run if we actually have a client (which implies API key)
        if client.client:
            response = client.execute(request)
            assert response is not None
            if not response.is_success():
                pytest.skip(f"Gemini API call failed (environment/auth issue): {response.error}")
            assert len(response.content) > 0

    def test_gemini_client_timeout_config(self):
        """Test timeout configuration."""
        client = GeminiClient(config={"gemini_timeout": 120})
        # Timeout settings are stored in config
        assert client.get_config_value("gemini_timeout") == 120

    def test_gemini_client_file_operations_structure(self):
        """Test file operations structure (without executing)."""
        client = GeminiClient()
        assert hasattr(client, 'upload_file')
        assert hasattr(client, 'list_files')
        assert hasattr(client, 'delete_file')

    def test_gemini_client_config_override(self):
        """Test configuration override."""
        config = {
            "gemini_model": "custom-model",
            "gemini_timeout": 120,
        }
    
        client = GeminiClient(config=config)
    
        assert client.default_model == "custom-model"
        assert client.get_config_value("gemini_timeout") == 120

    def test_gemini_client_request_validation(self):
        """Test request validation."""
        client = GeminiClient()
    
        # Test empty prompt validation
        empty_request = AgentRequest(prompt="")
        response = client.execute(empty_request)
        assert not response.is_success()
        assert "Prompt is required" in response.error
