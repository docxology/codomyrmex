from typing import Any

from codomyrmex.model_context_protocol.tool_decorator import mcp_tool


@mcp_tool(name="nlp_tokenize", description="Tokenize text into tokens", category="nlp")
def nlp_tokenize(text: str) -> dict[str, Any]:
    """Tokenize text into words/tokens."""
    if not text:
        return {"tokens": []}
    return {"tokens": text.split()}


@mcp_tool(
    name="nlp_extract_entities",
    description="Extract named entities from text",
    category="nlp",
)
def nlp_extract_entities(text: str) -> dict[str, Any]:
    """Extract named entities from text (dummy implementation)."""
    if not text:
        return {"entities": []}
    # Simple dummy implementation: words starting with uppercase
    entities = [word for word in text.split() if word and word[0].isupper()]
    return {"entities": entities}


@mcp_tool(name="nlp_summarize", description="Summarize a text passage", category="nlp")
def nlp_summarize(text: str, max_length: int = 100) -> dict[str, Any]:
    """Summarize a text passage (dummy implementation)."""
    if not text:
        return {"summary": ""}
    # Dummy implementation: return the first few words up to max_length chars
    if len(text) <= max_length:
        return {"summary": text}

    truncated = text[:max_length]
    # Try to cut at the last space
    last_space = truncated.rfind(" ")
    if last_space > 0:
        return {"summary": truncated[:last_space] + "..."}
    return {"summary": truncated + "..."}
