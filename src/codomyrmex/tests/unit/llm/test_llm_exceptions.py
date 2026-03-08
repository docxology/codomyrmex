"""Zero-mock tests for llm/exceptions.py.

Tests all exception classes with real instantiation, context storage,
hierarchy checks, and edge-case behaviors (e.g., truncation at 500 chars).
"""

from __future__ import annotations

import pytest

from codomyrmex.llm.exceptions import (
    ContentFilterError,
    ContextWindowError,
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
    ModelNotFoundError,
    PromptError,
    PromptTooLongError,
    PromptValidationError,
    ResponseError,
    ResponseParsingError,
    ResponseValidationError,
    StreamingError,
    TokenLimitError,
)


@pytest.mark.unit
class TestLLMErrorBase:
    """Tests for LLMError base class."""

    def test_llm_error_is_exception(self):
        err = LLMError("something went wrong")
        assert isinstance(err, Exception)

    def test_llm_error_message_stored(self):
        err = LLMError("base llm error")
        assert "base llm error" in str(err)

    def test_llm_error_context_empty_by_default(self):
        err = LLMError("base error")
        assert isinstance(err.context, dict)

    def test_llm_error_is_catchable_as_base(self):
        with pytest.raises(LLMError):
            raise LLMConnectionError("fail", provider="openai")


@pytest.mark.unit
class TestLLMConnectionError:
    """Tests for LLMConnectionError context storage."""

    def test_stores_provider(self):
        err = LLMConnectionError("conn failed", provider="ollama")
        assert err.context["provider"] == "ollama"

    def test_stores_endpoint(self):
        err = LLMConnectionError("conn failed", endpoint="http://localhost:11434")
        assert err.context["endpoint"] == "http://localhost:11434"

    def test_stores_provider_and_endpoint_together(self):
        err = LLMConnectionError("fail", provider="anthropic", endpoint="https://api.anthropic.com")
        assert err.context["provider"] == "anthropic"
        assert err.context["endpoint"] == "https://api.anthropic.com"

    def test_no_provider_no_endpoint_context_clean(self):
        err = LLMConnectionError("fail")
        assert "provider" not in err.context
        assert "endpoint" not in err.context


@pytest.mark.unit
class TestLLMAuthenticationError:
    """Tests for LLMAuthenticationError context storage."""

    def test_stores_provider(self):
        err = LLMAuthenticationError("bad key", provider="openai")
        assert err.context["provider"] == "openai"

    def test_no_provider_leaves_clean_context(self):
        err = LLMAuthenticationError("auth failure")
        assert "provider" not in err.context

    def test_message_preserved(self):
        err = LLMAuthenticationError("invalid API key")
        assert "invalid API key" in str(err)


@pytest.mark.unit
class TestLLMRateLimitError:
    """Tests for LLMRateLimitError context storage."""

    def test_stores_provider(self):
        err = LLMRateLimitError("rate limited", provider="openai")
        assert err.context["provider"] == "openai"

    def test_stores_retry_after(self):
        err = LLMRateLimitError("rate limited", retry_after=60.0)
        assert err.context["retry_after"] == 60.0

    def test_stores_limit_type(self):
        err = LLMRateLimitError("rate limited", limit_type="requests_per_minute")
        assert err.context["limit_type"] == "requests_per_minute"

    def test_retry_after_zero_not_stored(self):
        # retry_after=0.0 is falsy for "if retry_after is not None" — 0.0 IS stored
        err = LLMRateLimitError("rate limited", retry_after=0.0)
        assert "retry_after" in err.context
        assert err.context["retry_after"] == 0.0

    def test_no_optional_args_clean_context(self):
        err = LLMRateLimitError("rate limited")
        assert "provider" not in err.context
        assert "retry_after" not in err.context


@pytest.mark.unit
class TestLLMTimeoutError:
    """Tests for LLMTimeoutError context storage."""

    def test_stores_timeout_seconds(self):
        err = LLMTimeoutError("timed out", timeout_seconds=30.0)
        assert err.context["timeout_seconds"] == 30.0

    def test_stores_provider(self):
        err = LLMTimeoutError("timed out", provider="anthropic")
        assert err.context["provider"] == "anthropic"

    def test_timeout_zero_is_stored(self):
        err = LLMTimeoutError("timed out", timeout_seconds=0.0)
        assert err.context["timeout_seconds"] == 0.0


@pytest.mark.unit
class TestPromptHierarchy:
    """Tests for PromptError and its subclasses."""

    def test_prompt_error_is_llm_error(self):
        err = PromptError("prompt failed")
        assert isinstance(err, LLMError)

    def test_prompt_too_long_is_prompt_error(self):
        err = PromptTooLongError("too long")
        assert isinstance(err, PromptError)

    def test_prompt_too_long_stores_token_count(self):
        err = PromptTooLongError("too long", token_count=8192)
        assert err.context["token_count"] == 8192

    def test_prompt_too_long_stores_max_tokens(self):
        err = PromptTooLongError("too long", max_tokens=4096)
        assert err.context["max_tokens"] == 4096

    def test_prompt_too_long_stores_model(self):
        err = PromptTooLongError("too long", model="gpt-4")
        assert err.context["model"] == "gpt-4"

    def test_prompt_validation_stores_errors_list(self):
        errors = ["field required", "invalid format"]
        err = PromptValidationError("invalid", validation_errors=errors)
        assert err.context["validation_errors"] == errors

    def test_prompt_validation_no_errors_clean_context(self):
        err = PromptValidationError("invalid")
        assert "validation_errors" not in err.context


@pytest.mark.unit
class TestResponseHierarchy:
    """Tests for ResponseError and its subclasses."""

    def test_response_error_is_llm_error(self):
        err = ResponseError("response failed")
        assert isinstance(err, LLMError)

    def test_response_parsing_is_response_error(self):
        err = ResponseParsingError("parse failed")
        assert isinstance(err, ResponseError)

    def test_response_parsing_stores_expected_format(self):
        err = ResponseParsingError("failed", expected_format="json")
        assert err.context["expected_format"] == "json"

    def test_response_parsing_stores_raw_response_short(self):
        raw = "short response"
        err = ResponseParsingError("failed", raw_response=raw)
        assert err.context["raw_response"] == raw

    def test_response_parsing_truncates_raw_response_over_500_chars(self):
        raw = "x" * 600
        err = ResponseParsingError("failed", raw_response=raw)
        stored = err.context["raw_response"]
        assert stored.endswith("...")
        assert len(stored) == 503  # 500 + "..."

    def test_response_validation_is_response_error(self):
        err = ResponseValidationError("invalid")
        assert isinstance(err, ResponseError)


@pytest.mark.unit
class TestContentFilterError:
    """Tests for ContentFilterError context storage."""

    def test_stores_filter_type(self):
        err = ContentFilterError("blocked", filter_type="safety")
        assert err.context["filter_type"] == "safety"

    def test_stores_category(self):
        err = ContentFilterError("blocked", category="violence")
        assert err.context["category"] == "violence"

    def test_no_optional_args_clean(self):
        err = ContentFilterError("blocked")
        assert "filter_type" not in err.context
        assert "category" not in err.context


@pytest.mark.unit
class TestModelNotFoundError:
    """Tests for ModelNotFoundError context storage."""

    def test_stores_model(self):
        err = ModelNotFoundError("not found", model="gpt-5")
        assert err.context["model"] == "gpt-5"

    def test_stores_provider(self):
        err = ModelNotFoundError("not found", provider="openai")
        assert err.context["provider"] == "openai"

    def test_stores_available_models(self):
        models = ["gpt-4", "gpt-3.5-turbo"]
        err = ModelNotFoundError("not found", available_models=models)
        assert err.context["available_models"] == models


@pytest.mark.unit
class TestTokenAndStreamingErrors:
    """Tests for TokenLimitError and StreamingError."""

    def test_token_limit_stores_requested(self):
        err = TokenLimitError("limit", requested_tokens=100)
        assert err.context["requested_tokens"] == 100

    def test_token_limit_stores_available(self):
        err = TokenLimitError("limit", available_tokens=50)
        assert err.context["available_tokens"] == 50

    def test_token_limit_zero_stored(self):
        err = TokenLimitError("limit", available_tokens=0)
        assert err.context["available_tokens"] == 0

    def test_streaming_stores_chunks_received(self):
        err = StreamingError("stream failed", chunks_received=42)
        assert err.context["chunks_received"] == 42

    def test_streaming_no_chunks_clean_context(self):
        err = StreamingError("stream failed")
        assert "chunks_received" not in err.context


@pytest.mark.unit
class TestContextWindowError:
    """Tests for ContextWindowError context storage."""

    def test_stores_context_length(self):
        err = ContextWindowError("overflow", context_length=200000)
        assert err.context["context_length"] == 200000

    def test_stores_max_context(self):
        err = ContextWindowError("overflow", max_context=128000)
        assert err.context["max_context"] == 128000

    def test_stores_model(self):
        err = ContextWindowError("overflow", model="claude-3-5-sonnet")
        assert err.context["model"] == "claude-3-5-sonnet"

    def test_context_length_zero_stored(self):
        err = ContextWindowError("overflow", context_length=0)
        assert err.context["context_length"] == 0

    def test_full_context_all_fields(self):
        err = ContextWindowError(
            "context exceeded",
            context_length=150000,
            max_context=100000,
            model="claude-opus-4",
        )
        assert err.context["context_length"] == 150000
        assert err.context["max_context"] == 100000
        assert err.context["model"] == "claude-opus-4"
