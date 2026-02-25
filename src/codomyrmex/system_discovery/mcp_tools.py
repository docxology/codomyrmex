"""MCP tools for the system_discovery module."""


from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="system_discovery")
def health_check(module: str | None = None) -> dict:
    """Run a health check on the system or a specific module.

    Args:
        module: Optional module name to check (checks all if omitted)

    Returns:
        Health status report with module statuses.
    """
    from codomyrmex.system_discovery import HealthChecker

    try:
        checker = HealthChecker()
        if module:
            result = checker.check_module(module)
        else:
            result = checker.check_all()
        return {
            "status": "success",
            "healthy": result.healthy if hasattr(result, "healthy") else True,
            "module": module or "all",
            "details": result.to_dict() if hasattr(result, "to_dict") else str(result),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="system_discovery")
def list_modules() -> dict:
    """List all registered modules and their availability.

    Returns:
        Dictionary with module names, versions, and availability status.
    """
    from codomyrmex.system_discovery import CapabilityScanner

    try:
        scanner = CapabilityScanner()
        modules = scanner.scan() if hasattr(scanner, "scan") else []
        return {
            "status": "success",
            "modules": [
                {
                    "name": m.name if hasattr(m, "name") else str(m),
                    "available": m.available if hasattr(m, "available") else True,
                }
                for m in modules
            ] if modules else [],
            "count": len(modules) if modules else 0,
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
        return {"status": "error", "message": f"Module not found: {module}", "detail": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
