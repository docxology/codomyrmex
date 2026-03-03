"""MCP tool definitions for the reporting module.

Exposes reporting generation as MCP tools.
"""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.reporting.reporting import create_reporting


@mcp_tool(
    category="reporting",
    description="Process data and generate a report.",
)
def reporting_process(data: str) -> dict[str, Any]:
    """Process the given data into a report.

    Args:
        data: The input data to report on, serialized as string.

    Returns:
        A dictionary containing the report result.
    """
    reporter = create_reporting()
    return reporter.process(data)
