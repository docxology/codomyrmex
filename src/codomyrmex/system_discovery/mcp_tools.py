"""MCP tools for the system_discovery module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="system_discovery")
def health_check(module: str | None = None) -> dict:
    """Run health checks on one module, or on every module with a dedicated check.

    Args:
        module: Optional top-level module name to check, e.g. ``"coding"``.
            When omitted, every module in ``HealthChecker.module_checks`` is
            checked.

    Returns:
        ``healthy`` is true only if every checked module reports ``healthy``;
        ``details`` maps each checked module to its ``HealthCheckResult``.
    """
    from codomyrmex.system_discovery.health.health_checker import (
        HealthChecker,
        HealthStatus,
    )

    try:
        results = HealthChecker().run_checks([module] if module else None)
        return {
            "status": "success",
            "healthy": all(
                result.status is HealthStatus.HEALTHY for result in results.values()
            ),
            "module": module or "all",
            "details": {name: result.to_dict() for name, result in results.items()},
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="system_discovery")
def list_modules() -> dict:
    """list all registered modules and their availability.

    Returns:
        Dictionary with module names, versions, and availability status.
    """
    import codomyrmex as _codomyrmex

    try:
        module_names = _codomyrmex.list_modules()
        return {
            "status": "success",
            "modules": [{"name": m, "available": True} for m in module_names],
            "count": len(module_names),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="system_discovery")
def dependency_tree(module: str) -> dict:
    """Show the dependency tree for a specific module.

    Args:
        module: Module name to inspect

    Returns:
        Dependency tree as a nested dictionary.
    """
    try:
        import importlib

        mod = importlib.import_module(f"codomyrmex.{module}")
        deps: list[str] = []
        if hasattr(mod, "__all__"):
            deps = list(mod.__all__)
        return {
            "status": "success",
            "module": module,
            "exports": deps,
            "export_count": len(deps),
        }
    except ImportError as e:
        return {
            "status": "error",
            "message": f"Module not found: {module}",
            "detail": str(e),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
