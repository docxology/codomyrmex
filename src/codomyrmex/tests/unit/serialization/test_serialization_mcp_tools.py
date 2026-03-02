"""Tests for serialization MCP tools.

Zero-mock policy: tests use the real serialize/deserialize functions.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.serialization.mcp_tools import (
        deserialize_data,
        serialization_list_formats,
        serialize_data,
    )

    assert callable(serialize_data)
    assert callable(deserialize_data)
    assert callable(serialization_list_formats)


def test_list_formats_returns_list() -> None:
    """serialization_list_formats returns a non-empty list of strings."""
    from codomyrmex.serialization.mcp_tools import serialization_list_formats

    formats = serialization_list_formats()
    assert isinstance(formats, list)
    assert len(formats) > 0
    assert all(isinstance(f, str) for f in formats)


def test_list_formats_includes_json() -> None:
    """serialization_list_formats always includes 'json'."""
    from codomyrmex.serialization.mcp_tools import serialization_list_formats

    assert "json" in serialization_list_formats()


def test_serialize_data_json_returns_string() -> None:
    """serialize_data returns a JSON string for a dict."""
    from codomyrmex.serialization.mcp_tools import serialize_data

    result = serialize_data({"key": "value", "num": 42}, format="json")
    assert isinstance(result, str)
    assert "key" in result


def test_serialize_deserialize_roundtrip() -> None:
    """serialize_data then deserialize_data recovers the original object."""
    from codomyrmex.serialization.mcp_tools import deserialize_data, serialize_data

    original = {"hello": "world", "number": 123}
    serialized = serialize_data(original, format="json")
    recovered = deserialize_data(serialized, format="json")
    assert recovered == original


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.serialization.mcp_tools import (
        deserialize_data,
        serialization_list_formats,
        serialize_data,
    )

    for fn in (serialize_data, deserialize_data, serialization_list_formats):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
