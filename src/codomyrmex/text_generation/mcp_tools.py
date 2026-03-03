"""
MCP tools for the text_generation module.
"""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="text_generation")
def generate_text(prompt: str, max_length: int = 100) -> str:
    """Generate text from a prompt.

    Args:
        prompt: The prompt to generate text from.
        max_length: The maximum length of the generated text.

    Returns:
        The generated text.
    """
    return f"Generated text for: {prompt[:max_length]}"
