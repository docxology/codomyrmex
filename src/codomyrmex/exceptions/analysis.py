"""Analysis Exceptions.

Errors related to static analysis, pattern matching, and security auditing.
"""

from __future__ import annotations

from typing import Any

from .base import CodomyrmexError


class StaticAnalysisError(CodomyrmexError):
    """Raised when static analysis operations fail.

    Attributes:
        message (str): The error message.
        analyzer_name (str | None): Name of the analyzer that failed.
        file_path (str | None): Path to the file being analyzed.
    """

    def __init__(
        self,
        message: str,
        analyzer_name: str | None = None,
        file_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if analyzer_name:
            self.context["analyzer_name"] = analyzer_name
        if file_path:
            self.context["file_path"] = file_path


class PatternMatchingError(CodomyrmexError):
    """Raised when pattern matching operations fail.

    Attributes:
        message (str): The error message.
        pattern (str | None): The pattern that failed to match.
        subject_preview (str | None): A preview of the subject being matched.
    """

    def __init__(
        self,
        message: str,
        pattern: str | None = None,
        subject_preview: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if pattern:
            self.context["pattern"] = pattern
        if subject_preview:
            self.context["subject_preview"] = subject_preview


class SecurityAuditError(CodomyrmexError):
    """Raised when security audit operations fail.

    Attributes:
        message (str): The error message.
        vulnerability_type (str | None): The type of vulnerability found.
        severity (str | None): The severity of the vulnerability.
    """

    def __init__(
        self,
        message: str,
        vulnerability_type: str | None = None,
        severity: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if vulnerability_type:
            self.context["vulnerability_type"] = vulnerability_type
        if severity:
            self.context["severity"] = severity
