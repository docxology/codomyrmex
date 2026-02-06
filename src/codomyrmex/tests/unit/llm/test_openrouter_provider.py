"""
Tests for OpenRouterProvider.

Unit tests for the OpenRouter LLM provider implementation.
"""

from unittest.mock import MagicMock

import pytest

from codomyrmex.llm.providers import (
    Message,
    OpenRouterProvider,
    ProviderConfig,
    ProviderType,
    get_provider,
)


class TestOpenRouterProviderInit:
    """Test OpenRouterProvider initialization."""

    def test_provider_initialization_sets_base_url(self):
        """Test that provider sets OpenRouter base URL by default."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        assert provider.config.base_url == "https://openrouter.ai/api/v1"

    def test_provider_initialization_preserves_custom_base_url(self):
        """Test that custom base URL is preserved if provided."""
        config = ProviderConfig(
            api_key="test-key",
            base_url="https://custom.api.com/v1"
        )
        provider = OpenRouterProvider(config)

        assert provider.config.base_url == "https://custom.api.com/v1"

    def test_provider_sets_required_headers(self):
        """Test that required OpenRouter headers are set."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        assert "HTTP-Referer" in provider.config.extra_headers
        assert "X-Title" in provider.config.extra_headers
        assert provider.config.extra_headers["X-Title"] == "Codomyrmex"

    def test_provider_type_is_openrouter(self):
        """Test that provider_type is set correctly."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        assert provider.provider_type == ProviderType.OPENROUTER


class TestOpenRouterProviderModels:
    """Test OpenRouterProvider model listing."""

    def test_list_models_returns_free_models(self):
        """Test that list_models returns free models."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        models = provider.list_models()

        assert len(models) > 0
        assert any(":free" in m for m in models)

    def test_free_models_includes_expected_providers(self):
        """Test that free models include models from known providers."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        models = provider.list_models()

        # Check for models from different providers (updated for 2026 free models)
        providers_found = set()
        for model in models:
            if "nvidia/" in model:
                providers_found.add("nvidia")
            elif "liquid/" in model:
                providers_found.add("liquid")
            elif "arcee-ai/" in model:
                providers_found.add("arcee")
            elif "openrouter/" in model:
                providers_found.add("openrouter")

        # Should have at least 2 different providers
        assert len(providers_found) >= 2, f"Expected models from multiple providers, got: {providers_found}"

    def test_default_model_is_free(self):
        """Test that default model is a free model."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        default = provider._default_model()

        # Default is "openrouter/free" which auto-selects best free model
        assert "free" in default


class TestOpenRouterProviderFactory:
    """Test OpenRouterProvider via get_provider factory."""

    def test_get_provider_returns_openrouter(self):
        """Test that get_provider returns OpenRouterProvider for OPENROUTER type."""
        provider = get_provider(
            ProviderType.OPENROUTER,
            api_key="test-key"
        )

        assert isinstance(provider, OpenRouterProvider)

    def test_get_provider_with_config(self):
        """Test that get_provider accepts ProviderConfig."""
        config = ProviderConfig(
            api_key="test-key",
            timeout=120.0,
            max_retries=5
        )
        provider = get_provider(ProviderType.OPENROUTER, config=config)

        assert provider.config.timeout == 120.0
        assert provider.config.max_retries == 5


class TestOpenRouterProviderContextManager:
    """Test OpenRouterProvider context manager support."""

    def test_context_manager_enter_returns_provider(self):
        """Test that __enter__ returns the provider instance."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        with provider as p:
            assert p is provider

    def test_context_manager_cleanup_on_exit(self):
        """Test that cleanup is called on context manager exit."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        with provider:
            # Client should exist
            pass

        # After exit, client should be None (cleanup called)
        assert provider._client is None


class TestOpenRouterProviderComplete:
    """Test OpenRouterProvider completion methods."""

    def test_complete_calls_openai_client(self):
        """Test that complete() uses the OpenAI client correctly."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from OpenRouter!"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "google/gemma-2-9b-it:free"
        mock_response.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
        mock_client.chat.completions.create.return_value = mock_response

        # Create provider and inject mock client
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)
        provider._client = mock_client

        messages = [Message(role="user", content="Say hello")]
        response = provider.complete(messages)

        # Verify response
        assert response.content == "Hello from OpenRouter!"
        assert response.provider == ProviderType.OPENROUTER
        assert response.usage["total_tokens"] == 15

        # Verify the client was called correctly
        mock_client.chat.completions.create.assert_called_once()

    def test_complete_raises_when_client_not_initialized(self):
        """Test that complete() raises RuntimeError when client is None."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)
        provider._client = None

        messages = [Message(role="user", content="Hello")]

        with pytest.raises(RuntimeError, match="not initialized"):
            provider.complete(messages)


class TestOpenRouterProviderModel:
    """Test OpenRouterProvider model selection."""

    def test_get_model_uses_provided_model(self):
        """Test that get_model returns provided model."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        model = provider.get_model("meta-llama/llama-3.2-3b-instruct:free")

        assert model == "meta-llama/llama-3.2-3b-instruct:free"

    def test_get_model_uses_default_model(self):
        """Test that get_model returns default model when None provided."""
        config = ProviderConfig(api_key="test-key")
        provider = OpenRouterProvider(config)

        model = provider.get_model(None)

        assert model == "openrouter/free"

    def test_get_model_uses_config_default_model(self):
        """Test that get_model uses config default_model if set."""
        config = ProviderConfig(
            api_key="test-key",
            default_model="mistralai/mistral-7b-instruct:free"
        )
        provider = OpenRouterProvider(config)

        model = provider.get_model(None)

        assert model == "mistralai/mistral-7b-instruct:free"
