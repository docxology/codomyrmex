"""
MCP Tool Argument Validation

Validates tool arguments against their JSON Schema ``inputSchema`` before
dispatch, preventing invalid data from reaching handlers.
"""

from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ValidationResult:
    """Outcome of validating tool arguments against a schema."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    coerced_args: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Core validation function
# ---------------------------------------------------------------------------

def validate_tool_arguments(
    tool_name: str,
    arguments: dict[str, Any] | None,
    schema: dict[str, Any],
    *,
    coerce: bool = True,
) -> ValidationResult:
    """Validate *arguments* against the tool's ``inputSchema``.

    Parameters
    ----------
    tool_name:
        Used only for logging / error messages.
    arguments:
        The raw arguments dict supplied by the caller.
    schema:
        The full tool schema dict.  The ``inputSchema`` key is extracted
        automatically; if *schema* itself looks like a JSON Schema object
        (has ``"type"`` or ``"properties"``) it is used directly.
    coerce:
        When ``True``, attempt lightweight type coercion for common
        mismatches (``str → int``, ``str → bool``, ``str → float``).

    Returns
    -------
    ValidationResult
        ``valid=True`` with (optionally coerced) ``coerced_args`` on success,
        or ``valid=False`` with human-readable ``errors`` on failure.
    """
    # Normalise None → empty dict
    if arguments is None:
        arguments = {}

    # Extract the actual JSON Schema object
    input_schema = _extract_input_schema(schema)
    if input_schema is None:
        # No schema to validate against — pass through
        return ValidationResult(valid=True, coerced_args=dict(arguments))

    working_args = dict(arguments)

    if coerce:
        working_args = _coerce_types(working_args, input_schema)

    errors = _validate_against_schema(working_args, input_schema, tool_name)

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, coerced_args=working_args)


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

def _extract_input_schema(schema: dict[str, Any]) -> dict[str, Any] | None:
    """Pull the ``inputSchema`` out of a tool schema dict.

    Handles both ``{"inputSchema": {...}}`` and a bare JSON Schema object.
    """
    if "inputSchema" in schema:
        return schema["inputSchema"]
    if "type" in schema or "properties" in schema:
        return schema
    return None


# ---------------------------------------------------------------------------
# Lightweight type coercion
# ---------------------------------------------------------------------------

_BOOL_TRUTHY = frozenset({"true", "1", "yes", "on"})
_BOOL_FALSY = frozenset({"false", "0", "no", "off"})


def _coerce_types(
    args: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Best-effort coercion of string values to declared schema types."""
    properties = schema.get("properties", {})
    coerced = dict(args)

    for key, value in coerced.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        if expected_type is None or not isinstance(value, str):
            continue

        try:
            if expected_type == "integer":
                coerced[key] = int(value)
            elif expected_type == "number":
                coerced[key] = float(value)
            elif expected_type == "boolean":
                low = value.lower()
                if low in _BOOL_TRUTHY:
                    coerced[key] = True
                elif low in _BOOL_FALSY:
                    coerced[key] = False
        except (ValueError, TypeError) as e:
            logger.debug("Coercion of key '%s' to %s failed: %s", key, expected_type, e)
            pass  # Let validation catch it

    return coerced


# ---------------------------------------------------------------------------
# Schema validation (pure-Python, no external deps for core path)
# ---------------------------------------------------------------------------

def _validate_against_schema(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate *args* against a JSON Schema object.

    Uses ``jsonschema`` if available (preferred), otherwise falls back to
    a lightweight built-in checker for ``required``, ``type``, ``enum``,
    ``minimum``/``maximum``, and ``pattern``.
    """
    try:
        return _validate_with_jsonschema(args, schema, tool_name)
    except ImportError:
        logger.debug("jsonschema not available; using built-in validator")
        return _validate_builtin(args, schema, tool_name)


def _validate_with_jsonschema(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Validate using the ``jsonschema`` library."""
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for err in sorted(validator.iter_errors(args), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def _validate_builtin(
    args: dict[str, Any],
    schema: dict[str, Any],
    tool_name: str,
) -> list[str]:
    """Lightweight fallback validation without ``jsonschema``."""
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Required field check
    for req in required:
        if req not in args:
            errors.append(f"{req}: required field is missing")

    # Type checks
    _TYPE_MAP: dict[str, tuple[type, ...]] = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
        "boolean": (bool,),
        "array": (list,),
        "object": (dict,),
    }

    for key, value in args.items():
        if key not in properties:
            # additionalProperties — skip unknown fields by default
            continue

        prop_schema = properties[key]
        expected = prop_schema.get("type")

        if expected and expected in _TYPE_MAP:
            if not isinstance(value, _TYPE_MAP[expected]):
                errors.append(
                    f"{key}: expected type '{expected}', "
                    f"got '{type(value).__name__}'"
                )
                continue

        # Enum
        enum_values = prop_schema.get("enum")
        if enum_values is not None and value not in enum_values:
            errors.append(
                f"{key}: value {value!r} not in allowed values {enum_values}"
            )

        # Min / max (numeric)
        if isinstance(value, (int, float)):
            mn = prop_schema.get("minimum")
            mx = prop_schema.get("maximum")
            if mn is not None and value < mn:
                errors.append(f"{key}: {value} < minimum {mn}")
            if mx is not None and value > mx:
                errors.append(f"{key}: {value} > maximum {mx}")

        # Pattern (string)
        if isinstance(value, str):
            import re

            pattern = prop_schema.get("pattern")
            if pattern and not re.search(pattern, value):
                errors.append(
                    f"{key}: value {value!r} does not match pattern {pattern!r}"
                )

    return errors


def _generate_schema_from_func(func: Callable[..., Any]) -> dict[str, Any]:
    """Generate a JSON Schema for a function's arguments."""
    sig = inspect.signature(func)
    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        param_schema: dict[str, Any] = {}

        # Type inference
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is str:
                param_schema["type"] = "string"
            elif param.annotation is int:
                param_schema["type"] = "integer"
            elif param.annotation is float:
                param_schema["type"] = "number"
            elif param.annotation is bool:
                param_schema["type"] = "boolean"
            elif param.annotation is list:
                param_schema["type"] = "array"
            elif param.annotation is dict:
                param_schema["type"] = "object"
            else:
                # Fallback or complex types
                param_schema["type"] = "string" # simplified
        else:
            param_schema["type"] = "string" # default

        properties[name] = param_schema

        if param.default == inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }
__all__ = [
    "ValidationResult",
    "validate_tool_arguments",
    "_generate_schema_from_func",
]
