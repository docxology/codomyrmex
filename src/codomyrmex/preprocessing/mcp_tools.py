"""MCP tools for the preprocessing module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="preprocessing")
def preprocess_data(data: str) -> dict:
    """Preprocess the given data string.

    Args:
        data: The input string data to preprocess.

    Returns:
        ``{"status": "success", "preprocessed": <str>}``, or
        ``{"status": "error", "message": <str>}`` when ``data`` is not a string.
    """
    if not isinstance(data, str):
        return {
            "status": "error",
            "message": f"data must be a string, got {type(data).__name__}",
        }
    return {"status": "success", "preprocessed": data.strip().lower()}
