"""MCP tools for the demos module."""

from codomyrmex.demos.registry import DemoResult, get_registry
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="demos")
def demos_list_demos(module: str | None = None, category: str | None = None) -> list[dict]:
    """
    List all registered demonstrations.

    Args:
        module: Optional module name to filter demos by.
        category: Optional category name to filter demos by.

    Returns:
        A list of dictionaries containing demonstration metadata.
    """
    registry = get_registry()
    demos = registry.list_demos(module=module, category=category)
    return [
        {
            "name": d.name,
            "description": d.description,
            "module": d.module,
            "category": d.category,
        }
        for d in demos
    ]


@mcp_tool(category="demos")
def demos_run_demo(name: str) -> dict:
    """
    Run a specified demonstration by name.

    Args:
        name: The name of the demo to run.

    Returns:
        A dictionary containing the results of the demonstration execution.
    """
    registry = get_registry()
    result: DemoResult = registry.run_demo(name)
    return {
        "name": result.name,
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time,
    }
