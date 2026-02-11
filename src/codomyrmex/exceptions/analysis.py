from __future__ import annotations
"""
Analysis Exceptions

Errors related to static analysis, pattern matching, and security auditing.
"""

from .base import CodomyrmexError


class StaticAnalysisError(CodomyrmexError):
    """Raised when static analysis operations fail."""
    pass


class PatternMatchingError(CodomyrmexError):
    """Raised when pattern matching operations fail."""
    pass


class SecurityAuditError(CodomyrmexError):
    """Raised when security audit operations fail."""
    pass
