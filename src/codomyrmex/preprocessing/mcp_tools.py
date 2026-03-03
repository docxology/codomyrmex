"""MCP tools for the preprocessing module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="preprocessing")
def preprocess_data(data: str) -> dict:
    """Preprocess the given data string.

    Args:
        data: The input string data to preprocess.

    Returns:
        A dictionary containing the preprocessed data.
    """
    return {"status": "success", "preprocessed": data.strip().lower()}
