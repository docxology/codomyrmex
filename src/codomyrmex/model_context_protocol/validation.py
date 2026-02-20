# DEPRECATED(v0.2.0): Shim module. Import from model_context_protocol.quality.validation instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: model_context_protocol.quality.validation"""
from .quality.validation import *  # noqa: F401,F403
from .quality.validation import (
    ValidationResult,
    validate_tool_arguments,
    _coerce_types,
    _extract_input_schema,
    _generate_schema_from_func,
    _validate_builtin,
)
