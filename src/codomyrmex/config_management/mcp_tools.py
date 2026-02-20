"""MCP tools for the config_management module."""

from typing import Any, Dict, List, Optional

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="config_management")
def get_config(
    key: str,
    namespace: str = "default",
) -> dict:
    """Retrieve a configuration value by key.

    Args:
        key: Configuration key to look up
        namespace: Configuration namespace (e.g. 'default', 'llm', 'mcp')

    Returns:
        Dictionary with the configuration value and metadata.
    """
    from codomyrmex.config_management import get_config as _get_config

    try:
        value = _get_config(key, namespace=namespace)
        return {
            "status": "success",
            "key": key,
            "namespace": namespace,
            "value": value,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="config_management")
def set_config(
    key: str,
    value: Any,
    namespace: str = "default",
) -> dict:
    """Set a configuration value.

    Args:
        key: Configuration key to set
        value: Value to store
        namespace: Configuration namespace

    Returns:
        Status dictionary confirming the update.
    """
    from codomyrmex.config_management import set_config as _set_config

    try:
        _set_config(key, value, namespace=namespace)
        return {
            "status": "success",
            "key": key,
            "namespace": namespace,
            "updated": True,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="config_management")
def validate_config(namespace: str = "default") -> dict:
    """Validate configuration consistency and completeness.

    Args:
        namespace: Configuration namespace to validate

    Returns:
        Validation report with any found issues.
    """
    from codomyrmex.config_management import validate_config as _validate

    try:
        result = _validate(namespace=namespace)
        return {
            "status": "success",
            "namespace": namespace,
            "valid": result.get("valid", True) if isinstance(result, dict) else True,
            "issues": result.get("issues", []) if isinstance(result, dict) else [],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
