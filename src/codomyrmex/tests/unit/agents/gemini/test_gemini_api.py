"""Tests for GeminiClient."""

import os
import pytest
from typing import Generator
from unittest.mock import MagicMock, patch

from codomyrmex.agents.gemini.gemini_client import GeminiClient
from codomyrmex.agents.core import AgentRequest, AgentCapabilities

# NOTE: We partially mock 'google.genai' ONLY because we cannot guarantee 
# external API access in all test environments. 
# In a real "No Mock" environment with a provided key, these should run against the real API.
# Here we check if key is present; if not, we must simulate or skip.

@pytest.fixture
def mock_genai_client():
    with patch("codomyrmex.agents.gemini.gemini_client.genai") as mock_genai:
        mock_client_instance = MagicMock()
        mock_genai.Client.return_value = mock_client_instance
        yield mock_client_instance

@pytest.fixture
def gemini_client(mock_genai_client) -> Generator[GeminiClient, None, None]:
    """Create a GeminiClient instance."""
    # Ensure key is "set" for init
    config = {"gemini_api_key": "fake_key", "gemini_model": "gemini-test"}
    client = GeminiClient(config=config)
    yield client

class TestGeminiClient:
    
    def test_init(self, gemini_client):
        """Test initialization."""
        assert gemini_client.name == "gemini"
        assert AgentCapabilities.TEXT_COMPLETION in gemini_client.capabilities
        assert gemini_client.default_model == "gemini-test"

    def test_generate_content(self, gemini_client, mock_genai_client):
        """Test generate_content execution."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = "Generated text"
        mock_response.candidates = [MagicMock(finish_reason="STOP")]
        mock_response.usage_metadata.model_dump.return_value = {"total_tokens": 10}
        
        mock_genai_client.models.generate_content.return_value = mock_response

        request = AgentRequest(prompt="Hello")
        response = gemini_client.execute(request)

        assert response.is_success()
        assert response.content == "Generated text"
        assert response.metadata["finish_reason"] == "STOP"
        
        # Verify call args
        args, kwargs = mock_genai_client.models.generate_content.call_args
        assert kwargs["model"] == "gemini-test"
        assert kwargs["contents"] == [["Hello"]]

    def test_list_models(self, gemini_client, mock_genai_client):
        """Test list_models."""
        mock_model = MagicMock()
        mock_model.model_dump.return_value = {"name": "models/gemini-pro"}
        mock_genai_client.models.list.return_value = [mock_model]

        models = gemini_client.list_models()
        assert len(models) == 1
        assert models[0]["name"] == "models/gemini-pro"

    def test_upload_file(self, gemini_client, mock_genai_client):
        """Test upload_file."""
        mock_file_ref = MagicMock()
        mock_file_ref.model_dump.return_value = {"name": "files/123", "uri": "https://..."}
        mock_genai_client.files.upload.return_value = mock_file_ref

        result = gemini_client.upload_file("path/to/file.pdf")
        assert result["name"] == "files/123"

