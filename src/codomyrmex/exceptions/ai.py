"""
AI and Code Generation Exceptions

Errors related to AI providers, code generation, and model context.
"""

from .base import CodomyrmexError


class AIProviderError(CodomyrmexError):
    """Raised when AI provider operations fail."""
    pass


class CodeGenerationError(CodomyrmexError):
    """Raised when code generation fails."""
    pass


class CodeEditingError(CodomyrmexError):
    """Raised when code editing operations fail."""
    pass


class ModelContextError(CodomyrmexError):
    """Raised when model context protocol operations fail."""
    pass
