"""
Validation utilities for system integrity and integration.
"""

import contextlib
import importlib
from typing import TYPE_CHECKING, Any

from .pai import validate_pai_integration

# Shared schemas for cross-module interop — imported by 74+ modules
with contextlib.suppress(ImportError):
    from .schemas import Result, ResultStatus

if TYPE_CHECKING:
    from .validation_manager import ValidationManager
    from .validator import (
        ValidationError,
        ValidationResult,
        Validator,
        get_errors,
        is_valid,
        validate,
    )

# The validation engine is loaded on first use: this package is imported by
# most modules (for Result), and the engine pulls in jsonschema and pydantic.
_LAZY_EXPORTS = {
    "ValidationError": ".validator",
    "ValidationManager": ".validation_manager",
    "ValidationResult": ".validator",
    "Validator": ".validator",
    "get_errors": ".validator",
    "is_valid": ".validator",
    "validate": ".validator",
}


def __getattr__(name: str) -> Any:
    module = _LAZY_EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(module, __name__), name)
    globals()[name] = value
    return value


__all__ = [
    "Result",
    "ResultStatus",
    "ValidationError",
    "ValidationManager",
    "ValidationResult",
    "Validator",
    "get_errors",
    "is_valid",
    "validate",
    "validate_pai_integration",
]
