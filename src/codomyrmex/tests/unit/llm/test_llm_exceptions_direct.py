"""Tests for llm.exceptions module — direct construction and hierarchy."""

import pytest

from codomyrmex.exceptions import AIProviderError
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


class TestLLMErrorHierarchy:
    def test_llm_error_is_ai_provider_error(self):
        assert issubclass(LLMError, AIProviderError)

    def test_connection_is_llm_error(self):
        assert issubclass(LLMConnectionError, LLMError)

    def test_prompt_is_llm_error(self):
        assert issubclass(PromptError, LLMError)

    def test_prompt_too_long_is_prompt_error(self):
        assert issubclass(PromptTooLongError, PromptError)

    def test_response_is_llm_error(self):
        assert issubclass(ResponseError, LLMError)

    def test_response_parsing_is_response_error(self):
        assert issubclass(ResponseParsingError, ResponseError)

    def test_response_validation_is_response_error(self):
        assert issubclass(ResponseValidationError, ResponseError)


class TestLLMConnectionError:
    def test_with_provider_and_endpoint(self):
        e = LLMConnectionError("Failed", provider="openai", endpoint="https://api.openai.com")
        assert e.context["provider"] == "openai"
        assert e.context["endpoint"] == "https://api.openai.com"

    def test_without_optional_fields(self):
        e = LLMConnectionError("Can't connect")
        assert "provider" not in e.context
        assert "endpoint" not in e.context

    def test_is_exception(self):
        with pytest.raises(LLMConnectionError):
            raise LLMConnectionError("no connection")


class TestLLMAuthenticationError:
    def test_with_provider(self):
        e = LLMAuthenticationError("Bad key", provider="anthropic")
        assert e.context["provider"] == "anthropic"

    def test_without_provider(self):
        e = LLMAuthenticationError("Auth failed")
        assert "provider" not in e.context


class TestLLMRateLimitError:
    def test_with_all_fields(self):
        e = LLMRateLimitError("Rate limited", provider="openai", retry_after=30.0, limit_type="rpm")
        assert e.context["provider"] == "openai"
        assert e.context["retry_after"] == 30.0
        assert e.context["limit_type"] == "rpm"

    def test_retry_after_zero_stored(self):
        e = LLMRateLimitError("Limit hit", retry_after=0.0)
        assert e.context["retry_after"] == 0.0

    def test_without_optional_fields(self):
        e = LLMRateLimitError("Too many requests")
        assert "provider" not in e.context
        assert "retry_after" not in e.context


class TestLLMTimeoutError:
    def test_with_timeout_and_provider(self):
        e = LLMTimeoutError("Timed out", timeout_seconds=60.0, provider="anthropic")
        assert e.context["timeout_seconds"] == 60.0
        assert e.context["provider"] == "anthropic"

    def test_without_optional_fields(self):
        e = LLMTimeoutError("Timeout")
        assert "timeout_seconds" not in e.context


class TestPromptTooLongError:
    def test_with_all_fields(self):
        e = PromptTooLongError("Too long", token_count=5000, max_tokens=4096, model="gpt-4")
        assert e.context["token_count"] == 5000
        assert e.context["max_tokens"] == 4096
        assert e.context["model"] == "gpt-4"

    def test_without_optional_fields(self):
        e = PromptTooLongError("Prompt too long")
        assert "token_count" not in e.context


class TestPromptValidationError:
    def test_with_validation_errors(self):
        errors = ["missing required field", "invalid format"]
        e = PromptValidationError("Invalid prompt", validation_errors=errors)
        assert e.context["validation_errors"] == errors

    def test_without_validation_errors(self):
        e = PromptValidationError("Validation failed")
        assert "validation_errors" not in e.context


class TestResponseParsingError:
    def test_with_expected_format(self):
        e = ResponseParsingError("Parse failed", expected_format="JSON")
        assert e.context["expected_format"] == "JSON"

    def test_raw_response_stored(self):
        e = ResponseParsingError("Failed", raw_response="invalid response body")
        assert "raw_response" in e.context

    def test_raw_response_truncated_at_500(self):
        long_response = "x" * 1000
        e = ResponseParsingError("Failed", raw_response=long_response)
        assert len(e.context["raw_response"]) <= 510

    def test_without_raw_response(self):
        e = ResponseParsingError("Parse error")
        assert "raw_response" not in e.context


class TestContentFilterError:
    def test_with_filter_type_and_category(self):
        e = ContentFilterError("Blocked", filter_type="hate_speech", category="violence")
        assert e.context["filter_type"] == "hate_speech"
        assert e.context["category"] == "violence"

    def test_without_optional_fields(self):
        e = ContentFilterError("Content filtered")
        assert "filter_type" not in e.context


class TestModelNotFoundError:
    def test_with_all_fields(self):
        e = ModelNotFoundError(
            "Not found",
            model="gpt-5",
            provider="openai",
            available_models=["gpt-4", "gpt-3.5"],
        )
        assert e.context["model"] == "gpt-5"
        assert e.context["provider"] == "openai"
        assert "gpt-4" in e.context["available_models"]

    def test_without_available_models(self):
        e = ModelNotFoundError("Not found", model="missing")
        assert "available_models" not in e.context


class TestTokenLimitError:
    def test_with_token_counts(self):
        e = TokenLimitError("Limit exceeded", requested_tokens=5000, available_tokens=4096)
        assert e.context["requested_tokens"] == 5000
        assert e.context["available_tokens"] == 4096

    def test_zero_tokens_stored(self):
        e = TokenLimitError("Limit", requested_tokens=0, available_tokens=0)
        assert e.context["requested_tokens"] == 0
        assert e.context["available_tokens"] == 0

    def test_without_counts(self):
        e = TokenLimitError("Token limit error")
        assert "requested_tokens" not in e.context


class TestStreamingError:
    def test_with_chunks_received(self):
        e = StreamingError("Stream broken", chunks_received=42)
        assert e.context["chunks_received"] == 42

    def test_zero_chunks_stored(self):
        e = StreamingError("Stream failed", chunks_received=0)
        assert e.context["chunks_received"] == 0

    def test_without_chunks(self):
        e = StreamingError("Streaming failed")
        assert "chunks_received" not in e.context


class TestContextWindowError:
    def test_with_all_fields(self):
        e = ContextWindowError("Too big", context_length=200000, max_context=128000, model="claude")
        assert e.context["context_length"] == 200000
        assert e.context["max_context"] == 128000
        assert e.context["model"] == "claude"

    def test_without_optional_fields(self):
        e = ContextWindowError("Context exceeded")
        assert "context_length" not in e.context
        assert "max_context" not in e.context
