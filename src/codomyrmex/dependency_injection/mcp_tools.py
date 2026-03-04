"""MCP tools for the dependency_injection module.

Exposes dependency injection introspection capabilities as
auto-discovered MCP tools. Zero external dependencies beyond the
dependency_injection module itself.
"""

from __future__ import annotations

import importlib
from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _resolve_name(fully_qualified_name: str) -> Any:
    """Helper to resolve a fully qualified name to an object."""
    if "." not in fully_qualified_name:
        raise ValueError(f"'{fully_qualified_name}' is not a fully qualified name.")

    parts = fully_qualified_name.split(".")

    # Try to import progressively longer module paths
    for i in range(len(parts) - 1, 0, -1):
        module_name = ".".join(parts[:i])
        try:
            obj = importlib.import_module(module_name)
            # Traverse remaining parts
            for attr in parts[i:]:
                obj = getattr(obj, attr)
            return obj
        except ImportError:
            continue
        except AttributeError as exc:
            raise AttributeError(
                f"Could not resolve attribute path '{'.'.join(parts[i:])}' in module '{module_name}'"
            ) from exc

    raise ImportError(f"Could not resolve module for '{fully_qualified_name}'")


@mcp_tool(
    category="dependency_injection",
    description=(
        "Get @injectable metadata for a class given its fully qualified name. "
        "Returns a dictionary with 'scope', 'auto_register', and 'tags' if decorated, "
        "or None if not decorated."
    ),
)
def di_get_injectable_metadata(class_name: str) -> dict | None:
    """Get injectable metadata for a class.

    Args:
        class_name: The fully qualified string name of the class (e.g.,
            "codomyrmex.dependency_injection.Container").

    Returns:
        A dictionary with the metadata, or None if the class is not decorated.
    """
    from codomyrmex.dependency_injection import get_injectable_metadata

    try:
        cls = _resolve_name(class_name)
    except Exception as exc:
        return {"error": str(exc)}

    if not isinstance(cls, type):
        return {"error": f"'{class_name}' is not a class."}

    metadata = get_injectable_metadata(cls)
    if metadata is None:
        return None

    return {
        "scope": metadata.scope,
        "auto_register": metadata.auto_register,
        "tags": list(metadata.tags),
    }


@mcp_tool(
    category="dependency_injection",
    description=(
        "Get @inject metadata and parameters for a function/method given its "
        "fully qualified name. Returns a dictionary with 'params', 'resolve_all', "
        "and 'injectable_params' if decorated, or None if not decorated."
    ),
)
def di_get_inject_metadata(function_name: str) -> dict | None:
    """Get inject metadata for a function or method.

    Args:
        function_name: The fully qualified string name of the function or method
            (e.g., "codomyrmex.dependency_injection.Container.__init__").

    Returns:
        A dictionary with the metadata, or None if the function is not decorated.
    """
    from codomyrmex.dependency_injection import (
        get_inject_metadata,
        get_injectable_params,
    )

    try:
        fn = _resolve_name(function_name)
    except Exception as exc:
        return {"error": str(exc)}

    if not callable(fn):
        return {"error": f"'{function_name}' is not callable."}

    metadata = get_inject_metadata(fn)
    if metadata is None:
        return None

    injectable_params = get_injectable_params(fn)

    # Convert types in injectable_params to strings for JSON serialization
    safe_params = {
        name: str(hint) if not hasattr(hint, "__name__") else hint.__name__
        for name, hint in injectable_params.items()
    }

    # Also convert types in metadata.params if necessary, although it usually contains dicts
    safe_metadata_params = {}
    for k, v in metadata.params.items():
        if isinstance(v, type):
            safe_metadata_params[k] = v.__name__
        else:
            safe_metadata_params[k] = str(v)

    return {
        "params": safe_metadata_params,
        "resolve_all": metadata.resolve_all,
        "injectable_params": safe_params,
    }
