"""MCP tool definitions for the dependency_injection module.

Exposes IoC container operations as MCP tools for agent consumption.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_container():
    """Lazy import of Container."""
    from codomyrmex.dependency_injection.container import Container

    return Container()


def _get_scope_enum():
    """Lazy import of Scope enum."""
    from codomyrmex.dependency_injection.scopes import Scope

    return Scope


@mcp_tool(
    category="dependency_injection",
    description="list available service scopes and create a new empty IoC container.",
)
def dependency_injection_list_scopes() -> dict[str, Any]:
    """list available dependency injection scopes.

    Returns:
        dict with keys: status, scopes
    """
    try:
        Scope = _get_scope_enum()
        return {
            "status": "success",
            "scopes": [s.value for s in Scope],
            "descriptions": {
                "singleton": "One instance shared across all consumers",
                "transient": "New instance created on every resolution",
                "scoped": "One instance per scope context",
            },
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="dependency_injection",
    description="Create a container, register services, and verify resolution works.",
)
def dependency_injection_verify_container() -> dict[str, Any]:
    """Verify the IoC container works by registering and resolving a test service.

    Returns:
        dict with keys: status, registration_count, resolution_ok, container_repr
    """
    try:
        container = _get_container()

        # Register a simple test class
        class _TestService:
            value = "test"

        container.register(_TestService, _TestService, scope="singleton")
        resolved = container.resolve(_TestService)

        return {
            "status": "success",
            "registration_count": len(container),
            "resolution_ok": resolved.value == "test",
            "container_repr": repr(container),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="dependency_injection",
    description="Inspect an injectable class for its dependency metadata and scope.",
)
def dependency_injection_inspect_class(class_name: str) -> dict[str, Any]:
    """Inspect whether a class has injectable metadata.

    Args:
        class_name: Fully qualified class name (e.g., 'codomyrmex.dependency_injection.Container').

    Returns:
        dict with keys: status, is_injectable, scope, auto_register, inject_params
    """
    try:
        from codomyrmex.dependency_injection.decorators import (
            get_inject_metadata,
            get_injectable_metadata,
            is_injectable,
        )

        # Resolve the class by name
        parts = class_name.rsplit(".", 1)
        if len(parts) != 2:
            return {
                "status": "error",
                "message": "class_name must be fully qualified (e.g., 'module.ClassName')",
            }
        module_path, cls_name = parts
        import importlib

        mod = importlib.import_module(module_path)
        cls = getattr(mod, cls_name)

        injectable = is_injectable(cls)
        meta = get_injectable_metadata(cls)
        inject_meta = get_inject_metadata(cls)

        result: dict[str, Any] = {
            "status": "success",
            "class": class_name,
            "is_injectable": injectable,
        }
        if meta:
            result["scope"] = meta.scope
            result["auto_register"] = meta.auto_register
        if inject_meta:
            result["inject_params"] = {k: str(v) for k, v in inject_meta.items()}

        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
