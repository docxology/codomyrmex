"""
Unit tests for llm providers: models, base, factory, openrouter, anthropic, openai, exceptions, mcp_tools.

Zero-mock policy: no unittest.mock, MagicMock, patch or monkeypatch.
Tests exercise real code paths via actual instantiation and concrete inputs.
Provider API calls (network) are skipped via module-level env-var guards.
"""

from __future__ import annotations

import os

import pytest

from codomyrmex.llm.exceptions import (
    ContentFilterError,
    ContextWindowError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMTimeoutError,
    ModelNotFoundError,
    PromptTooLongError,
    PromptValidationError,
    ResponseParsingError,
    StreamingError,
    TokenLimitError,
)
from codomyrmex.llm.providers.models import (
    CompletionResponse,
    Message,
    ProviderConfig,
    ProviderType,
)

# Skip guard for live API tests
_has_openrouter_key = bool(os.getenv("OPENROUTER_API_KEY"))
_has_anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))
_has_openai_key = bool(os.getenv("OPENAI_API_KEY"))


# ===========================================================================
# 1. Message dataclass
# ===========================================================================


@pytest.mark.unit
class TestMessageDataclass:
    """Tests for the Message dataclass."""

    def test_to_dict_minimal_fields(self):
        """to_dict with only role+content omits None optional fields."""
        msg = Message(role="user", content="Hello")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "Hello"
        assert "name" not in d
        assert "tool_calls" not in d
        assert "tool_call_id" not in d

    def test_to_dict_with_name(self):
        """to_dict includes name field when set."""
        msg = Message(role="assistant", content="Hi", name="bot")
        d = msg.to_dict()
        assert d["name"] == "bot"

    def test_to_dict_with_tool_calls(self):
        """to_dict includes tool_calls when set."""
        tc = [{"id": "call_1", "function": {"name": "search"}}]
        msg = Message(role="assistant", content="", tool_calls=tc)
        d = msg.to_dict()
        assert d["tool_calls"] == tc

    def test_to_dict_with_tool_call_id(self):
        """to_dict includes tool_call_id when set."""
        msg = Message(role="tool", content="result", tool_call_id="call_abc")
        d = msg.to_dict()
        assert d["tool_call_id"] == "call_abc"

    def test_all_optional_fields_set(self):
        """to_dict includes all optional fields when all are set."""
        tc = [{"id": "x"}]
        msg = Message(
            role="assistant",
            content="done",
            name="agent",
            tool_calls=tc,
            tool_call_id="cid",
        )
        d = msg.to_dict()
        assert d["name"] == "agent"
        assert d["tool_calls"] == tc
        assert d["tool_call_id"] == "cid"

    def test_system_role_message(self):
        """System role message serializes correctly."""
        msg = Message(role="system", content="You are a helpful assistant.")
        d = msg.to_dict()
        assert d["role"] == "system"
        assert d["content"] == "You are a helpful assistant."


# ===========================================================================
# 2. CompletionResponse dataclass
# ===========================================================================


@pytest.mark.unit
class TestCompletionResponse:
    """Tests for the CompletionResponse dataclass."""

    def test_total_tokens_with_usage(self):
        """total_tokens returns the value from usage dict."""
        resp = CompletionResponse(
            content="hi",
            model="gpt-4o",
            provider=ProviderType.OPENAI,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        )
        assert resp.total_tokens == 15

    def test_total_tokens_without_usage(self):
        """total_tokens returns 0 when usage is None."""
        resp = CompletionResponse(
            content="hi",
            model="gpt-4o",
            provider=ProviderType.OPENAI,
        )
        assert resp.total_tokens == 0

    def test_total_tokens_missing_key(self):
        """total_tokens returns 0 when total_tokens key is absent."""
        resp = CompletionResponse(
            content="hi",
            model="gpt-4o",
            provider=ProviderType.OPENAI,
            usage={"prompt_tokens": 10, "completion_tokens": 5},
        )
        assert resp.total_tokens == 0

    def test_finish_reason_defaults_none(self):
        """finish_reason defaults to None."""
        resp = CompletionResponse(
            content="text",
            model="claude-3",
            provider=ProviderType.ANTHROPIC,
        )
        assert resp.finish_reason is None

    def test_tool_calls_defaults_none(self):
        """tool_calls defaults to None."""
        resp = CompletionResponse(
            content="",
            model="m",
            provider=ProviderType.GOOGLE,
        )
        assert resp.tool_calls is None


# ===========================================================================
# 3. ProviderType enum
# ===========================================================================


@pytest.mark.unit
class TestProviderTypeEnum:
    """Tests for the ProviderType enum."""

    def test_openai_value(self):
        """OPENAI enum value is 'openai'."""
        assert ProviderType.OPENAI.value == "openai"

    def test_anthropic_value(self):
        """ANTHROPIC enum value is 'anthropic'."""
        assert ProviderType.ANTHROPIC.value == "anthropic"

    def test_openrouter_value(self):
        """OPENROUTER enum value is 'openrouter'."""
        assert ProviderType.OPENROUTER.value == "openrouter"

    def test_google_value(self):
        """GOOGLE enum value is 'google'."""
        assert ProviderType.GOOGLE.value == "google"

    def test_ollama_value(self):
        """OLLAMA enum value is 'ollama'."""
        assert ProviderType.OLLAMA.value == "ollama"

    def test_all_expected_types_exist(self):
        """All expected provider types are defined."""
        names = {t.name for t in ProviderType}
        for expected in ("OPENAI", "ANTHROPIC", "OPENROUTER", "GOOGLE", "OLLAMA"):
            assert expected in names


# ===========================================================================
# 4. ProviderConfig dataclass
# ===========================================================================


@pytest.mark.unit
class TestProviderConfig:
    """Tests for the ProviderConfig dataclass."""

    def test_defaults(self):
        """Default timeout=60 and max_retries=3."""
        cfg = ProviderConfig()
        assert cfg.timeout == 60.0
        assert cfg.max_retries == 3
        assert cfg.api_key is None
        assert cfg.base_url is None
        assert cfg.organization is None
        assert cfg.default_model is None

    def test_extra_headers_default_empty_dict(self):
        """extra_headers defaults to an empty dict."""
        cfg = ProviderConfig()
        assert cfg.extra_headers == {}

    def test_custom_values(self):
        """Custom values are stored correctly."""
        cfg = ProviderConfig(
            api_key="sk-test",
            base_url="https://example.com",
            timeout=30.0,
            max_retries=1,
            default_model="gpt-4",
        )
        assert cfg.api_key == "sk-test"
        assert cfg.base_url == "https://example.com"
        assert cfg.timeout == 30.0
        assert cfg.max_retries == 1
        assert cfg.default_model == "gpt-4"

    def test_extra_headers_are_independent_per_instance(self):
        """Each ProviderConfig gets its own extra_headers dict (no shared state)."""
        cfg1 = ProviderConfig()
        cfg2 = ProviderConfig()
        cfg1.extra_headers["X-Test"] = "value"
        assert "X-Test" not in cfg2.extra_headers


# ===========================================================================
# 5. LLMProvider base class (via concrete subclass)
# ===========================================================================


@pytest.mark.unit
class TestLLMProviderBase:
    """Tests for the LLMProvider ABC contract."""

    def _make_provider(self, default_model: str = "model-x"):
        """Create a minimal concrete provider for testing base class methods."""
        from collections.abc import Iterator

        from codomyrmex.llm.providers.base import LLMProvider

        class ConcreteProvider(LLMProvider):
            provider_type = ProviderType.OPENAI

            def complete(
                self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs
            ):
                return CompletionResponse(
                    content="test",
                    model=self.get_model(model),
                    provider=self.provider_type,
                )

            def complete_stream(
                self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs
            ) -> Iterator[str]:
                yield "test"

            async def complete_async(
                self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs
            ):
                return CompletionResponse(
                    content="test",
                    model=self.get_model(model),
                    provider=self.provider_type,
                )

            def list_models(self):
                return ["model-x"]

            def _default_model(self):
                return default_model

        return ConcreteProvider(ProviderConfig())

    def test_context_manager_returns_self(self):
        """__enter__ returns the provider instance."""
        provider = self._make_provider()
        with provider as p:
            assert p is provider

    def test_context_manager_cleanup_clears_client(self):
        """__exit__ calls cleanup() which sets _client to None."""
        provider = self._make_provider()
        provider._client = object()  # set non-None sentinel
        with provider:
            pass
        assert provider._client is None

    def test_get_model_returns_provided_model(self):
        """get_model(model) returns the specified model string."""
        provider = self._make_provider()
        assert provider.get_model("gpt-4") == "gpt-4"

    def test_get_model_returns_config_default(self):
        """get_model(None) returns config.default_model when set."""
        cfg = ProviderConfig(default_model="claude-3")
        from collections.abc import Iterator

        from codomyrmex.llm.providers.base import LLMProvider

        class MinimalProvider(LLMProvider):
            provider_type = ProviderType.ANTHROPIC

            def complete(
                self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs
            ):
                return None

            def complete_stream(
                self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs
            ) -> Iterator[str]:
                yield ""

            async def complete_async(
                self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs
            ):
                return None

            def list_models(self):
                return []

            def _default_model(self):
                return "fallback"

        provider = MinimalProvider(cfg)
        assert provider.get_model(None) == "claude-3"

    def test_get_model_falls_back_to_default_model_method(self):
        """get_model(None) with no config default falls back to _default_model()."""
        provider = self._make_provider(default_model="model-x")
        assert provider.get_model(None) == "model-x"


# ===========================================================================
# 6. Provider factory
# ===========================================================================


@pytest.mark.unit
class TestProviderFactory:
    """Tests for the get_provider factory function."""

    def test_raises_for_unsupported_ollama(self):
        """get_provider raises ValueError for OLLAMA (not in factory map)."""
        from codomyrmex.llm.providers.factory import get_provider

        with pytest.raises(ValueError, match="Unsupported provider"):
            get_provider(ProviderType.OLLAMA)

    def test_raises_for_unsupported_azure_openai(self):
        """get_provider raises ValueError for AZURE_OPENAI."""
        from codomyrmex.llm.providers.factory import get_provider

        with pytest.raises(ValueError, match="Unsupported provider"):
            get_provider(ProviderType.AZURE_OPENAI)

    def test_creates_config_from_kwargs(self):
        """get_provider creates ProviderConfig from kwargs when config=None."""
        from codomyrmex.llm.providers.factory import get_provider

        provider = get_provider(ProviderType.OPENROUTER, api_key="test-key")
        assert provider.config.api_key == "test-key"

    def test_openrouter_provider_returned(self):
        """get_provider returns OpenRouterProvider for OPENROUTER type."""
        from codomyrmex.llm.providers.factory import get_provider
        from codomyrmex.llm.providers.openrouter import OpenRouterProvider

        # api_key required by openai SDK even without a real key
        provider = get_provider(ProviderType.OPENROUTER, api_key="test-key")
        assert isinstance(provider, OpenRouterProvider)

    def test_anthropic_provider_returned(self):
        """get_provider returns AnthropicProvider for ANTHROPIC type."""
        from codomyrmex.llm.providers.anthropic import AnthropicProvider
        from codomyrmex.llm.providers.factory import get_provider

        provider = get_provider(ProviderType.ANTHROPIC, api_key="test-key")
        assert isinstance(provider, AnthropicProvider)

    def test_existing_config_passed_through(self):
        """get_provider uses provided config object without modification."""
        from codomyrmex.llm.providers.factory import get_provider

        cfg = ProviderConfig(api_key="existing", timeout=45.0)
        provider = get_provider(ProviderType.OPENROUTER, config=cfg)
        assert provider.config.api_key == "existing"
        assert provider.config.timeout == 45.0


# ===========================================================================
# 7. OpenRouterProvider
# ===========================================================================


@pytest.mark.unit
class TestOpenRouterProvider:
    """Tests for OpenRouterProvider initialization and static logic."""

    def _make(self, **kwargs):
        from codomyrmex.llm.providers.openrouter import OpenRouterProvider

        # openai SDK requires api_key; use a placeholder to avoid OpenAIError
        kwargs.setdefault("api_key", "test-placeholder-key")
        cfg = ProviderConfig(**kwargs)
        return OpenRouterProvider(cfg)

    def test_base_url_set_when_not_specified(self):
        """base_url is set to BASE_URL when config.base_url is None."""
        from codomyrmex.llm.providers.openrouter import OpenRouterProvider

        p = self._make()
        assert p.config.base_url == OpenRouterProvider.BASE_URL

    def test_base_url_unchanged_when_specified(self):
        """base_url stays as provided when explicitly set."""
        custom = "https://custom.example.com"
        p = self._make(base_url=custom)
        assert p.config.base_url == custom

    def test_extra_headers_set_on_init(self):
        """HTTP-Referer and X-Title headers are added during init."""
        p = self._make()
        assert "HTTP-Referer" in p.config.extra_headers
        assert "X-Title" in p.config.extra_headers

    def test_list_models_returns_free_models(self):
        """list_models() returns the FREE_MODELS class attribute."""
        from codomyrmex.llm.providers.openrouter import OpenRouterProvider

        p = self._make()
        models = p.list_models()
        assert models is OpenRouterProvider.FREE_MODELS
        assert len(models) > 0

    def test_list_models_contains_free_suffix(self):
        """At least one model in FREE_MODELS ends with ':free'."""
        p = self._make()
        assert any(m.endswith(":free") for m in p.list_models())

    def test_default_model_is_openrouter_free(self):
        """_default_model() returns 'openrouter/free'."""
        p = self._make()
        assert p._default_model() == "openrouter/free"

    def test_provider_type_is_openrouter(self):
        """provider_type is ProviderType.OPENROUTER."""
        p = self._make()
        assert p.provider_type == ProviderType.OPENROUTER

    def test_complete_raises_when_client_none(self):
        """complete() raises RuntimeError when _client is None."""
        p = self._make()
        p._client = None
        msgs = [Message(role="user", content="hello")]
        with pytest.raises(RuntimeError, match="not initialized"):
            p.complete(msgs)

    def test_complete_stream_raises_when_client_none(self):
        """complete_stream() raises RuntimeError when _client is None."""
        p = self._make()
        p._client = None
        msgs = [Message(role="user", content="hello")]
        with pytest.raises(RuntimeError, match="not initialized"):
            list(p.complete_stream(msgs))


# ===========================================================================
# 8. AnthropicProvider
# ===========================================================================


@pytest.mark.unit
class TestAnthropicProvider:
    """Tests for AnthropicProvider static/structural logic."""

    def _make(self, **kwargs):
        from codomyrmex.llm.providers.anthropic import AnthropicProvider

        cfg = ProviderConfig(**kwargs)
        return AnthropicProvider(cfg)

    def test_list_models_returns_claude_names(self):
        """list_models() returns a list of Claude model names."""
        p = self._make()
        models = p.list_models()
        assert len(models) > 0
        assert all("claude" in m.lower() for m in models)

    def test_default_model_is_sonnet(self):
        """_default_model() returns claude-3-5-sonnet string."""
        p = self._make()
        assert "claude-3-5-sonnet" in p._default_model()

    def test_provider_type_is_anthropic(self):
        """provider_type is ProviderType.ANTHROPIC."""
        p = self._make()
        assert p.provider_type == ProviderType.ANTHROPIC

    def test_complete_raises_when_client_none(self):
        """complete() raises RuntimeError when _client is None."""
        p = self._make()
        p._client = None
        msgs = [Message(role="user", content="hi")]
        with pytest.raises(RuntimeError, match="Anthropic client not initialized"):
            p.complete(msgs)

    def test_complete_stream_raises_when_client_none(self):
        """complete_stream() raises RuntimeError when _client is None."""
        p = self._make()
        p._client = None
        msgs = [Message(role="user", content="hi")]
        with pytest.raises(RuntimeError, match="Anthropic client not initialized"):
            list(p.complete_stream(msgs))


# ===========================================================================
# 9. OpenAIProvider
# ===========================================================================


@pytest.mark.unit
class TestOpenAIProvider:
    """Tests for OpenAIProvider structural logic."""

    def _make(self, **kwargs):
        from codomyrmex.llm.providers.openai import OpenAIProvider

        kwargs.setdefault("api_key", "test-placeholder-key")
        cfg = ProviderConfig(**kwargs)
        return OpenAIProvider(cfg)

    def test_default_model_is_gpt4o(self):
        """_default_model() returns 'gpt-4o'."""
        p = self._make()
        assert p._default_model() == "gpt-4o"

    def test_provider_type_is_openai(self):
        """provider_type is ProviderType.OPENAI."""
        p = self._make()
        assert p.provider_type == ProviderType.OPENAI

    def test_complete_raises_when_client_none(self):
        """complete() raises RuntimeError when _client is None."""
        p = self._make()
        p._client = None
        msgs = [Message(role="user", content="hi")]
        with pytest.raises(RuntimeError, match="OpenAI client not initialized"):
            p.complete(msgs)

    def test_complete_stream_raises_when_client_none(self):
        """complete_stream() raises RuntimeError when _client is None."""
        p = self._make()
        p._client = None
        msgs = [Message(role="user", content="hi")]
        with pytest.raises(RuntimeError, match="not initialized"):
            list(p.complete_stream(msgs))

    def test_list_models_returns_empty_when_client_none(self):
        """list_models() returns [] when _client is None."""
        p = self._make()
        p._client = None
        assert p.list_models() == []


# ===========================================================================
# 10. LLM Exceptions
# ===========================================================================


@pytest.mark.unit
class TestLLMExceptions:
    """Tests for llm exception hierarchy and context field storage."""

    def test_llm_connection_error_stores_provider(self):
        """LLMConnectionError stores provider in context dict."""
        exc = LLMConnectionError("conn failed", provider="openai")
        assert exc.context["provider"] == "openai"

    def test_llm_connection_error_stores_endpoint(self):
        """LLMConnectionError stores endpoint in context dict."""
        exc = LLMConnectionError("conn failed", endpoint="http://localhost:11434")
        assert exc.context["endpoint"] == "http://localhost:11434"

    def test_llm_connection_error_omits_none_provider(self):
        """LLMConnectionError does not store 'provider' key when provider=None."""
        exc = LLMConnectionError("conn failed")
        assert "provider" not in exc.context

    def test_llm_authentication_error_stores_provider(self):
        """LLMAuthenticationError stores provider in context."""
        exc = LLMAuthenticationError("auth failed", provider="anthropic")
        assert exc.context["provider"] == "anthropic"

    def test_llm_rate_limit_stores_retry_after(self):
        """LLMRateLimitError stores retry_after in context."""
        exc = LLMRateLimitError("rate limit", retry_after=30.0)
        assert exc.context["retry_after"] == 30.0

    def test_llm_rate_limit_stores_limit_type(self):
        """LLMRateLimitError stores limit_type in context."""
        exc = LLMRateLimitError("rate limit", limit_type="requests")
        assert exc.context["limit_type"] == "requests"

    def test_llm_timeout_stores_timeout_seconds(self):
        """LLMTimeoutError stores timeout_seconds in context."""
        exc = LLMTimeoutError("timed out", timeout_seconds=60.0)
        assert exc.context["timeout_seconds"] == 60.0

    def test_prompt_too_long_stores_token_counts(self):
        """PromptTooLongError stores token_count and max_tokens in context."""
        exc = PromptTooLongError(
            "too long", token_count=8192, max_tokens=4096, model="gpt-4"
        )
        assert exc.context["token_count"] == 8192
        assert exc.context["max_tokens"] == 4096
        assert exc.context["model"] == "gpt-4"

    def test_prompt_validation_stores_errors(self):
        """PromptValidationError stores validation_errors list in context."""
        errors = ["field missing", "invalid format"]
        exc = PromptValidationError("validation failed", validation_errors=errors)
        assert exc.context["validation_errors"] == errors

    def test_prompt_validation_no_errors_omits_key(self):
        """PromptValidationError with None validation_errors omits the key."""
        exc = PromptValidationError("validation failed")
        assert "validation_errors" not in exc.context

    def test_response_parsing_stores_expected_format(self):
        """ResponseParsingError stores expected_format in context."""
        exc = ResponseParsingError("parse fail", expected_format="json")
        assert exc.context["expected_format"] == "json"

    def test_response_parsing_truncates_long_raw_response(self):
        """ResponseParsingError truncates raw_response longer than 500 chars."""
        long_raw = "x" * 600
        exc = ResponseParsingError("parse fail", raw_response=long_raw)
        stored = exc.context["raw_response"]
        assert stored.endswith("...")
        assert len(stored) == 503  # 500 chars + "..."

    def test_response_parsing_keeps_short_raw_response(self):
        """ResponseParsingError keeps raw_response shorter than 500 chars intact."""
        short_raw = "small response"
        exc = ResponseParsingError("parse fail", raw_response=short_raw)
        assert exc.context["raw_response"] == short_raw

    def test_context_window_error_stores_all_fields(self):
        """ContextWindowError stores context_length, max_context, and model."""
        exc = ContextWindowError(
            "context too long",
            context_length=8192,
            max_context=4096,
            model="gpt-3.5",
        )
        assert exc.context["context_length"] == 8192
        assert exc.context["max_context"] == 4096
        assert exc.context["model"] == "gpt-3.5"

    def test_streaming_error_stores_chunks_received(self):
        """StreamingError stores chunks_received in context."""
        exc = StreamingError("stream broken", chunks_received=5)
        assert exc.context["chunks_received"] == 5

    def test_token_limit_error_stores_requested_and_available(self):
        """TokenLimitError stores requested_tokens and available_tokens."""
        exc = TokenLimitError(
            "limit exceeded", requested_tokens=2000, available_tokens=1000
        )
        assert exc.context["requested_tokens"] == 2000
        assert exc.context["available_tokens"] == 1000

    def test_content_filter_stores_filter_type_and_category(self):
        """ContentFilterError stores filter_type and category in context."""
        exc = ContentFilterError("blocked", filter_type="safety", category="violence")
        assert exc.context["filter_type"] == "safety"
        assert exc.context["category"] == "violence"

    def test_model_not_found_stores_model_and_available(self):
        """ModelNotFoundError stores model and available_models in context."""
        exc = ModelNotFoundError(
            "not found",
            model="gpt-5",
            provider="openai",
            available_models=["gpt-4o", "gpt-4"],
        )
        assert exc.context["model"] == "gpt-5"
        assert exc.context["provider"] == "openai"
        assert exc.context["available_models"] == ["gpt-4o", "gpt-4"]

    def test_inheritance_chain(self):
        """LLMConnectionError is a subclass of LLMError and AIProviderError."""
        from codomyrmex.exceptions import AIProviderError
        from codomyrmex.llm.exceptions import LLMError

        exc = LLMConnectionError("test")
        assert isinstance(exc, LLMError)
        assert isinstance(exc, AIProviderError)


# ===========================================================================
# 11. MCP tools metadata
# ===========================================================================


@pytest.mark.unit
class TestMCPToolsMetadata:
    """Tests verifying MCP tool metadata is correctly registered."""

    def test_generate_text_has_mcp_meta(self):
        """generate_text has _mcp_tool_meta attribute."""
        from codomyrmex.llm.mcp_tools import generate_text

        assert hasattr(generate_text, "_mcp_tool_meta")

    def test_list_local_models_has_mcp_meta(self):
        """list_local_models has _mcp_tool_meta attribute."""
        from codomyrmex.llm.mcp_tools import list_local_models

        assert hasattr(list_local_models, "_mcp_tool_meta")

    def test_query_fabric_metadata_has_mcp_meta(self):
        """query_fabric_metadata has _mcp_tool_meta attribute."""
        from codomyrmex.llm.mcp_tools import query_fabric_metadata

        assert hasattr(query_fabric_metadata, "_mcp_tool_meta")

    def test_reason_has_mcp_meta(self):
        """reason has _mcp_tool_meta attribute."""
        from codomyrmex.llm.mcp_tools import reason

        assert hasattr(reason, "_mcp_tool_meta")

    def test_generate_text_meta_category_is_llm(self):
        """generate_text._mcp_tool_meta category is 'llm'."""
        from codomyrmex.llm.mcp_tools import generate_text

        assert generate_text._mcp_tool_meta["category"] == "llm"

    def test_generate_text_meta_schema_has_required_prompt(self):
        """generate_text schema marks 'prompt' as required."""
        from codomyrmex.llm.mcp_tools import generate_text

        schema = generate_text._mcp_tool_meta["schema"]
        assert "prompt" in schema.get("required", [])

    def test_generate_text_meta_schema_has_provider_param(self):
        """generate_text schema includes 'provider' parameter."""
        from codomyrmex.llm.mcp_tools import generate_text

        schema = generate_text._mcp_tool_meta["schema"]
        assert "provider" in schema["properties"]

    def test_generate_text_meta_schema_has_model_param(self):
        """generate_text schema includes 'model' parameter."""
        from codomyrmex.llm.mcp_tools import generate_text

        schema = generate_text._mcp_tool_meta["schema"]
        assert "model" in schema["properties"]

    def test_reason_meta_returns_unsupported_provider_error(self):
        """generate_text with unknown provider returns error status dict."""
        from codomyrmex.llm.mcp_tools import generate_text

        result = generate_text(prompt="test", provider="nonexistent_provider_xyz")
        assert result["status"] == "error"

    def test_reason_meta_schema_has_prompt_required(self):
        """reason schema marks 'prompt' as required."""
        from codomyrmex.llm.mcp_tools import reason

        schema = reason._mcp_tool_meta["schema"]
        assert "prompt" in schema.get("required", [])
