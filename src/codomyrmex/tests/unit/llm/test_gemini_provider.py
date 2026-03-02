"""Tests for GeminiProvider.

Zero-Mock compliant — uses real Gemini API calls gated by GEMINI_API_KEY.
"""

import os

import pytest

from codomyrmex.llm.providers import (
    Message,
    ProviderConfig,
    ProviderType,
    get_provider,
)
from codomyrmex.llm.providers.gemini import GEMINI_MODELS, GeminiProvider

_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
_skip_no_key = pytest.mark.skipif(not _GEMINI_KEY, reason="GEMINI_API_KEY not set")


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestGeminiProviderInit:
    """Test GeminiProvider initialization."""

    def test_provider_type_is_google(self):
        """Test that provider_type is set correctly."""
        config = ProviderConfig(api_key="test-key")
        provider = GeminiProvider(config)

        assert provider.provider_type == ProviderType.GOOGLE

    @_skip_no_key
    def test_init_with_real_key_creates_client(self):
        """Test that provider creates a client with a real API key."""
        config = ProviderConfig(api_key=_GEMINI_KEY)
        provider = GeminiProvider(config)

        assert provider._client is not None

    def test_init_reads_env_var(self):
        """Test that provider reads GEMINI_API_KEY from env if not in config."""
        config = ProviderConfig()
        provider = GeminiProvider(config)

        expected_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        assert provider.config.api_key == expected_key


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TestGeminiProviderModels:
    """Test GeminiProvider model listing."""

    def test_list_models_returns_known_models(self):
        """Test that list_models returns the known Gemini models."""
        config = ProviderConfig(api_key="test-key")
        provider = GeminiProvider(config)

        models = provider.list_models()

        assert len(models) > 0
        assert "gemini-2.5-pro" in models

    def test_default_model_is_gemini_2_5_pro(self):
        """Test that default model is gemini-2.5-pro (Ultra tier)."""
        config = ProviderConfig(api_key="test-key")
        provider = GeminiProvider(config)

        assert provider._default_model() == "gemini-2.5-pro"

    def test_get_model_uses_provided_model(self):
        """Test that get_model returns the provided model name."""
        config = ProviderConfig(api_key="test-key")
        provider = GeminiProvider(config)

        model = provider.get_model("gemini-2.5-flash")

        assert model == "gemini-2.5-flash"

    def test_get_model_uses_config_default_model(self):
        """Test that get_model uses config default_model if set."""
        config = ProviderConfig(api_key="test-key", default_model="gemini-2.0-flash")
        provider = GeminiProvider(config)

        model = provider.get_model(None)

        assert model == "gemini-2.0-flash"

    def test_gemini_models_constant_is_populated(self):
        """Test that the GEMINI_MODELS list is populated."""
        assert len(GEMINI_MODELS) >= 4
        assert all(m.startswith("gemini-") for m in GEMINI_MODELS)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class TestGeminiProviderFactory:
    """Test GeminiProvider via get_provider factory."""

    def test_get_provider_returns_gemini_provider(self):
        """Test that get_provider returns GeminiProvider for GOOGLE type."""
        provider = get_provider(ProviderType.GOOGLE, api_key="test-key")

        assert isinstance(provider, GeminiProvider)

    def test_get_provider_with_config(self):
        """Test that get_provider accepts ProviderConfig."""
        config = ProviderConfig(api_key="test-key", timeout=120.0, max_retries=5)
        provider = get_provider(ProviderType.GOOGLE, config=config)

        assert provider.config.timeout == 120.0
        assert provider.config.max_retries == 5


# ---------------------------------------------------------------------------
# Context Manager
# ---------------------------------------------------------------------------


class TestGeminiProviderContextManager:
    """Test GeminiProvider context manager support."""

    def test_context_manager_enter_returns_provider(self):
        """Test that __enter__ returns the provider instance."""
        config = ProviderConfig(api_key="test-key")
        provider = GeminiProvider(config)

        with provider as p:
            assert p is provider

    def test_context_manager_cleanup_on_exit(self):
        """Test that cleanup is called on context manager exit."""
        config = ProviderConfig(api_key="test-key")
        provider = GeminiProvider(config)

        with provider:
            pass

        assert provider._client is None


# ---------------------------------------------------------------------------
# Live API tests (require GEMINI_API_KEY)
# ---------------------------------------------------------------------------


@_skip_no_key
class TestGeminiProviderComplete:
    """Test GeminiProvider completion with real Gemini API."""

    def test_complete_returns_response(self):
        """Test that complete() returns a valid response using real API."""
        config = ProviderConfig(api_key=_GEMINI_KEY)
        with GeminiProvider(config) as provider:
            messages = [Message(role="user", content="Say hello in one word")]
            response = provider.complete(messages, model="gemini-2.0-flash")

            assert len(response.content) > 0
            assert response.provider == ProviderType.GOOGLE
            assert response.model == "gemini-2.0-flash"

    def test_complete_with_system_instruction(self):
        """Test that system instructions are handled."""
        config = ProviderConfig(api_key=_GEMINI_KEY)
        with GeminiProvider(config) as provider:
            messages = [
                Message(role="system", content="You are a pirate. Reply in pirate speak."),
                Message(role="user", content="Hello"),
            ]
            response = provider.complete(messages, model="gemini-2.0-flash")

            assert len(response.content) > 0

    def test_complete_returns_usage(self):
        """Test that usage metadata is returned."""
        config = ProviderConfig(api_key=_GEMINI_KEY)
        with GeminiProvider(config) as provider:
            messages = [Message(role="user", content="Say hi")]
            response = provider.complete(messages, model="gemini-2.0-flash")

            assert response.usage is not None
            assert response.usage.get("total_tokens", 0) > 0

    def test_stream_yields_chunks(self):
        """Test that stream yields content chunks."""
        config = ProviderConfig(api_key=_GEMINI_KEY)
        with GeminiProvider(config) as provider:
            messages = [Message(role="user", content="Count from 1 to 3")]
            chunks = list(provider.complete_stream(messages, model="gemini-2.0-flash"))

            assert len(chunks) >= 1
            assert any(len(c) > 0 for c in chunks)


# ---------------------------------------------------------------------------
# Message conversion
# ---------------------------------------------------------------------------


class TestGeminiMessagesToContents:
    """Test _messages_to_contents helper."""

    def test_filters_system_messages(self):
        """System messages are filtered (handled via system_instruction)."""
        messages = [
            Message(role="system", content="Be helpful"),
            Message(role="user", content="Hello"),
        ]
        contents = GeminiProvider._messages_to_contents(messages)

        assert len(contents) == 1
        assert contents[0]["role"] == "user"

    def test_maps_assistant_to_model(self):
        """Assistant role is mapped to 'model' for Gemini API."""
        messages = [
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!"),
        ]
        contents = GeminiProvider._messages_to_contents(messages)

        assert contents[0]["role"] == "user"
        assert contents[1]["role"] == "model"

    def test_preserves_content(self):
        """Message content is preserved in parts."""
        messages = [Message(role="user", content="Test content")]
        contents = GeminiProvider._messages_to_contents(messages)

        assert contents[0]["parts"][0]["text"] == "Test content"
