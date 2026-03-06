"""
Validation utilities for system integrity and integration.
"""

from .pai import validate_pai_integration

# Shared schemas for cross-module interop — imported by 74+ modules
try:
    from .schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

__all__ = [
    "Result",
    "ResultStatus",
    "validate_pai_integration",
]
