"""MCP tool definitions for the validation module.

Exposes schema validation, configuration checking, and validation
summary as MCP tools discoverable by Claude Code and other
MCP-compatible agents.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


def _get_validation_manager():
    """Lazy import ValidationManager to avoid circular imports."""
    from codomyrmex.validation.validation_manager import ValidationManager
    return ValidationManager()


@mcp_tool(
    category="validation",
    description="Validate data against a JSON Schema.",
)
def validate_schema(
    data: dict[str, Any],
    schema: dict[str, Any],
    validator_type: str = "json_schema",
) -> dict[str, Any]:
    """Validate data against a schema using the specified validator type.

    Args:
        data: Data to validate.
        schema: JSON Schema or Pydantic model reference.
        validator_type: Validation strategy — 'json_schema', 'pydantic', or 'custom'.

    Returns:
        Dictionary with validation result, errors, and warnings.
    """
    mgr = _get_validation_manager()
    result = mgr.validate(data, schema, validator_type=validator_type)

    return {
        "is_valid": result.is_valid,
        "errors": [
            {
                "message": str(e),
                "field": getattr(e, "field", None),
                "code": getattr(e, "code", None),
            }
            for e in result.errors
        ],
        "warnings": [
            {
                "message": w.message,
                "field": w.field,
            }
            for w in result.warnings
        ],
    }


@mcp_tool(
    category="validation",
    description="Validate a configuration dictionary against common patterns.",
)
def validate_config(
    config: dict[str, Any],
    required_keys: list[str] | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    """Validate a configuration dictionary for required keys and types.

    Args:
        config: Configuration dictionary to validate.
        required_keys: Keys that must be present in the config.
        strict: If True, reject unknown keys.

    Returns:
        Dictionary with validation status, missing keys, and extra keys.
    """
    required_keys = required_keys or []
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    # Check required keys
    missing = [k for k in required_keys if k not in config]
    for key in missing:
        errors.append({"field": key, "message": f"Required key '{key}' is missing"})

    # Check for extra keys in strict mode
    if strict and required_keys:
        extra = [k for k in config if k not in required_keys]
        for key in extra:
            warnings.append({"field": key, "message": f"Unknown key '{key}' in strict mode"})

    # Check for None values in required keys
    for key in required_keys:
        if key in config and config[key] is None:
            warnings.append({"field": key, "message": f"Key '{key}' is present but None"})

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "missing_keys": missing,
        "key_count": len(config),
    }


@mcp_tool(
    category="validation",
    description="Get a summary of validation operations performed in this session.",
)
def validation_summary() -> dict[str, Any]:
    """Return summary statistics from the validation manager.

    Returns:
        Dictionary with run count, pass rate, error rate, and validators used.
    """
    mgr = _get_validation_manager()
    return mgr.summary()
