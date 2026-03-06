"""AI and Code Generation Exceptions.

Errors related to AI providers, code generation, and model context.
"""

from __future__ import annotations

from typing import Any

from .base import CodomyrmexError


class AIProviderError(CodomyrmexError):
    """Raised when AI provider operations fail.

    Attributes:
        message (str): The error message.
        provider_name (str | None): Name of the AI provider.
        model_name (str | None): Name of the model being used.
    """

    def __init__(
        self,
        message: str,
        provider_name: str | None = None,
        model_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if provider_name:
            self.context["provider_name"] = provider_name
        if model_name:
            self.context["model_name"] = model_name


class CodeGenerationError(CodomyrmexError):
    """Raised when code generation fails.

    Attributes:
        message (str): The error message.
        language (str | None): The target programming language.
        prompt_preview (str | None): A preview of the prompt used.
    """

    def __init__(
        self,
        message: str,
        language: str | None = None,
        prompt_preview: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if language:
            self.context["language"] = language
        if prompt_preview:
            self.context["prompt_preview"] = prompt_preview


class CodeEditingError(CodomyrmexError):
    """Raised when code editing operations fail.

    Attributes:
        message (str): The error message.
        file_path (str | None): Path to the file being edited.
        edit_type (str | None): The type of edit being performed.
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        edit_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = file_path
        if edit_type:
            self.context["edit_type"] = edit_type


class ModelContextError(CodomyrmexError):
    """Raised when model context protocol operations fail.

    Attributes:
        message (str): The error message.
        protocol_version (str | None): The version of the protocol.
        operation (str | None): The operation that failed.
    """

    def __init__(
        self,
        message: str,
        protocol_version: str | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if protocol_version:
            self.context["protocol_version"] = protocol_version
        if operation:
            self.context["operation"] = operation
