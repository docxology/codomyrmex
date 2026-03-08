"""
Validation utilities for system integrity and integration.
"""

import contextlib

from .pai import validate_pai_integration

# Shared schemas for cross-module interop — imported by 74+ modules
with contextlib.suppress(ImportError):
    from .schemas import Result, ResultStatus

__all__ = [
    "Result",
    "ResultStatus",
    "validate_pai_integration",
]
