"""Code Execution Submodule.

Provides secure code execution capabilities in sandboxed Docker environments.
Supports multiple programming languages with configurable timeouts and session
management for persistent execution contexts.

Public API:
    execute_code: Main function to execute code snippets.
    SUPPORTED_LANGUAGES: Dictionary of supported language configurations.
    validate_language: Check if a language is supported.
    validate_session_id: Validate and sanitize session identifiers.

Example:
    >>> from codomyrmex.coding.execution import execute_code, validate_language
    >>> if validate_language("python"):
    ...     result = execute_code("python", "print('Hello!')")
    ...     print(result["stdout"])  # "Hello!"
"""

from .executor import execute_code
from .language_support import SUPPORTED_LANGUAGES, validate_language
from .session_manager import validate_session_id

__all__ = [
    "execute_code",
    "SUPPORTED_LANGUAGES",
    "validate_language",
    "validate_session_id",
]

