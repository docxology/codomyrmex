"""LLM Exception Classes.

This module defines exceptions specific to LLM (Large Language Model) operations
including API calls, prompt processing, and response handling.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from codomyrmex.exceptions import CodomyrmexError, AIProviderError


class LLMError(AIProviderError):
    """Base exception for LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """Raised when connection to LLM service fails."""

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        endpoint: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if provider:
            self.context["provider"] = provider
        if endpoint:
            self.context["endpoint"] = endpoint


class LLMAuthenticationError(LLMError):
    """Raised when LLM authentication fails."""

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if provider:
            self.context["provider"] = provider


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        retry_after: float | None = None,
        limit_type: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if provider:
            self.context["provider"] = provider
        if retry_after is not None:
            self.context["retry_after"] = retry_after
        if limit_type:
            self.context["limit_type"] = limit_type


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""

    def __init__(
        self,
        message: str,
        timeout_seconds: float | None = None,
        provider: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds
        if provider:
            self.context["provider"] = provider


class PromptError(LLMError):
    """Raised when prompt processing fails."""
    pass


class PromptTooLongError(PromptError):
    """Raised when prompt exceeds maximum token limit."""

    def __init__(
        self,
        message: str,
        token_count: int | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if token_count is not None:
            self.context["token_count"] = token_count
        if max_tokens is not None:
            self.context["max_tokens"] = max_tokens
        if model:
            self.context["model"] = model


class PromptValidationError(PromptError):
    """Raised when prompt validation fails."""

    def __init__(
        self,
        message: str,
        validation_errors: list[str] | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if validation_errors:
            self.context["validation_errors"] = validation_errors


class ResponseError(LLMError):
    """Raised when LLM response processing fails."""
    pass


class ResponseParsingError(ResponseError):
    """Raised when LLM response cannot be parsed."""

    def __init__(
        self,
        message: str,
        expected_format: str | None = None,
        raw_response: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if expected_format:
            self.context["expected_format"] = expected_format
        # Truncate raw response to avoid huge context
        if raw_response:
            self.context["raw_response"] = raw_response[:500] + "..." if len(raw_response) > 500 else raw_response


class ResponseValidationError(ResponseError):
    """Raised when LLM response validation fails."""
    pass


class ContentFilterError(LLMError):
    """Raised when content is blocked by safety filters."""

    def __init__(
        self,
        message: str,
        filter_type: str | None = None,
        category: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if filter_type:
            self.context["filter_type"] = filter_type
        if category:
            self.context["category"] = category


class ModelNotFoundError(LLMError):
    """Raised when specified model is not available."""

    def __init__(
        self,
        message: str,
        model: str | None = None,
        provider: str | None = None,
        available_models: list[str] | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if model:
            self.context["model"] = model
        if provider:
            self.context["provider"] = provider
        if available_models:
            self.context["available_models"] = available_models


class TokenLimitError(LLMError):
    """Raised when token limit operations fail."""

    def __init__(
        self,
        message: str,
        requested_tokens: int | None = None,
        available_tokens: int | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if requested_tokens is not None:
            self.context["requested_tokens"] = requested_tokens
        if available_tokens is not None:
            self.context["available_tokens"] = available_tokens


class StreamingError(LLMError):
    """Raised when streaming response fails."""

    def __init__(
        self,
        message: str,
        chunks_received: int | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if chunks_received is not None:
            self.context["chunks_received"] = chunks_received


class ContextWindowError(LLMError):
    """Raised when context window is exceeded."""

    def __init__(
        self,
        message: str,
        context_length: int | None = None,
        max_context: int | None = None,
        model: str | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if context_length is not None:
            self.context["context_length"] = context_length
        if max_context is not None:
            self.context["max_context"] = max_context
        if model:
            self.context["model"] = model
