"""Tests for GeminiClient.

Zero-Mock compliant — tests use the real Gemini API when GEMINI_API_KEY is
set, otherwise they are skipped.
"""

import os
from collections.abc import Generator

import pytest

_HAS_GEMINI_KEY = bool(os.environ.get("GEMINI_API_KEY"))

try:
    from codomyrmex.agents.core import AgentCapabilities, AgentRequest
    from codomyrmex.agents.gemini.gemini_client import GeminiClient
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Tests that require no API key (structural / init tests)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGeminiClientInit:
    """Tests for GeminiClient initialisation paths."""

    @pytest.mark.skipif(not _HAS_GEMINI_KEY, reason="GEMINI_API_KEY not set")
    def test_init_with_real_key(self):
        """GeminiClient initializes successfully with a real API key."""
        client = GeminiClient()
        assert client.name == "gemini"
        assert AgentCapabilities.TEXT_COMPLETION in client.capabilities
        assert client.client is not None

    def test_init_without_key_warns(self):
        """GeminiClient warns (but doesn't crash) when no API key is available."""
        # The client logs a warning instead of raising
        client = GeminiClient(config={"gemini_api_key": ""})
        # api_key should be falsy
        assert not client.api_key

    @pytest.mark.skipif(not _HAS_GEMINI_KEY, reason="GEMINI_API_KEY not set")
    def test_default_model(self):
        """GeminiClient uses the default model from config or env."""
        client = GeminiClient()
        assert client.default_model is not None
        assert isinstance(client.default_model, str)


# ---------------------------------------------------------------------------
# Tests that require a live Gemini API key
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _HAS_GEMINI_KEY, reason="GEMINI_API_KEY not set")
@pytest.mark.unit
class TestGeminiClientAPI:
    """Live-API tests for GeminiClient — skipped without GEMINI_API_KEY."""

    @pytest.fixture
    def client(self):
        """Create a real GeminiClient with the environment API key."""
        return GeminiClient()

    def test_generate_content(self, client):
        """Test generate_content returns a successful response."""
        request = AgentRequest(prompt="Say hello in one word.")
        response = client.execute(request)

        assert response.is_success()
        assert len(response.content) > 0

    def test_list_models(self, client):
        """Test list_models returns at least one model."""
        models = client.list_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_count_tokens(self, client):
        """Test count_tokens returns token count dict."""
        result = client.count_tokens("Hello world")
        assert result is not None

    def test_stream(self, client):
        """Test streaming yields content chunks."""
        request = AgentRequest(prompt="Count from 1 to 3.")
        chunks = list(client.stream(request))
        assert len(chunks) >= 1
        assert any(len(c) > 0 for c in chunks)
