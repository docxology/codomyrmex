"""MCP tools for the cli module.

Exposes CLI command listing and execution capabilities as MCP tools.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.tool_decorator import mcp_tool
except ImportError:
    # Fallback to decorators if tool_decorator doesn't exist yet, or maybe just define it
    try:
        from codomyrmex.model_context_protocol.decorators import mcp_tool
    except ImportError:

        def mcp_tool(**kwargs: Any):  # type: ignore[misc]
            def decorator(func: Any) -> Any:
                func._mcp_tool_meta = kwargs
                return func

            return decorator


@mcp_tool(category="cli")
def cli_list_commands() -> dict[str, Any]:
    """List all available CLI commands.

    Introspects the Cli class to enumerate every registered command,
    returning the command name and its docstring.

    Returns:
        Dictionary with the list of available commands.
    """
    try:
        from codomyrmex.cli.core import Cli

        commands: list[dict[str, str]] = []
        for attr_name in sorted(dir(Cli)):
            if attr_name.startswith("_"):
                continue
            attr = getattr(Cli, attr_name, None)
            if callable(attr):
                doc = (attr.__doc__ or "").strip().split("\n")[0]
                commands.append({"name": attr_name, "description": doc})

        return {
            "status": "success",
            "command_count": len(commands),
            "commands": commands,
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="cli")
def cli_run_command(
    command: str,
    args: str = "",
) -> dict[str, Any]:
    """Execute a CLI command by name.

    Instantiates the Cli class and invokes the named method with
    the provided arguments. Arguments are passed as keyword pairs
    parsed from a JSON string.

    Args:
        command: Name of the CLI command to execute (e.g. 'check', 'modules').
        args: JSON string of keyword arguments to pass to the command.

    Returns:
        Dictionary with execution result or error information.
    """
    import json as _json

    try:
        from codomyrmex.cli.core import Cli

        cli_instance = Cli()
        method = getattr(cli_instance, command, None)
        if method is None:
            return {
                "status": "error",
                "message": f"Unknown CLI command: {command}",
            }

        kwargs: dict[str, Any] = {}
        if args:
            parsed = _json.loads(args)
            if isinstance(parsed, dict):
                kwargs = parsed
            else:
                return {
                    "status": "error",
                    "message": "args must be a JSON object (dict), not "
                    + type(parsed).__name__,
                }

        result = method(**kwargs)
        return {
            "status": "success",
            "command": command,
            "result": result,
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
