"""MCP tools for the serialization module.

Exposes serialize/deserialize/list_formats as auto-discovered MCP tools.
Zero external dependencies beyond the serialization module itself.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


@mcp_tool(
    category="serialization",
    description=(
        "Serialize a Python object to a string using the specified format "
        "(json, yaml, pickle). Returns a UTF-8 string for text formats."
    ),
)
def serialize_data(data: dict | list, format: str = "json") -> str:
    """Serialize data to a string representation."""
    import base64

    from codomyrmex.serialization import SerializationFormat, serialize

    fmt = SerializationFormat(format)
    result = serialize(data, fmt)
    try:
        return result.decode("utf-8")
    except (UnicodeDecodeError, AttributeError):
        # Binary format (e.g. pickle) — base64-encode for safe transport
        return base64.b64encode(result).decode("ascii")


@mcp_tool(
    category="serialization",
    description=(
        "Deserialize a string back to a Python object using the specified format "
        "(json, yaml, pickle)."
    ),
)
def deserialize_data(data: str, format: str = "json") -> dict | list:
    """Deserialize a string to a Python object."""
    from codomyrmex.serialization import SerializationFormat, deserialize

    fmt = SerializationFormat(format)
    raw: bytes = data.encode("utf-8")
    return deserialize(raw, fmt)


@mcp_tool(
    category="serialization",
    description="List all supported serialization format names (e.g. json, yaml, pickle).",
)
def serialization_list_formats() -> list[str]:
    """Return all supported serialization format identifiers."""
    from codomyrmex.serialization import SerializationFormat

    return [f.value for f in SerializationFormat]
