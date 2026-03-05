"""MCP tools for the serialization module.

Exposes serialize/deserialize/list_formats as auto-discovered MCP tools.
Zero external dependencies beyond the serialization module itself.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="serialization",
    description=(
        "Serialize a Python object to a string using the specified format "
        "(json, yaml, pickle). Returns a UTF-8 string for text formats."
    ),
)
def serialize_data(data: dict[str, Any] | list[Any], format: str = "json") -> str:
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
def deserialize_data(data: str, format: str = "json") -> dict[str, Any] | list[Any]:
    """Deserialize a string to a Python object."""
    from typing import cast

    from codomyrmex.serialization import SerializationFormat, deserialize

    fmt = SerializationFormat(format)

    # If it's a binary format like pickle, the data was base64 encoded
    try:
        raw: bytes = data.encode("utf-8")
        if fmt == SerializationFormat.PICKLE:
            import base64

            raw = base64.b64decode(raw)
        return cast("dict[str, Any] | list[Any]", deserialize(raw, fmt))
    except Exception as e:
        # Fallback to pure bytes if decoding fails but we have other binary formats
        try:
            import base64

            raw = base64.b64decode(data.encode("utf-8"))
            return cast("dict[str, Any] | list[Any]", deserialize(raw, fmt))
        except Exception:
            raise e from None


@mcp_tool(
    category="serialization",
    description="List all supported serialization format names (e.g. json, yaml, pickle).",
)
def serialization_list_formats() -> list[str]:
    """Return all supported serialization format identifiers."""
    from codomyrmex.serialization import SerializationFormat

    return [f.value for f in SerializationFormat]
