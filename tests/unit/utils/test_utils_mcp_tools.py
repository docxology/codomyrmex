"""Tests for utils MCP tools.

Zero-mock policy: tests use the real utils functions.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.utils.mcp_tools import (
        utils_flatten_dict,
        utils_hash_content,
        utils_json_loads,
    )

    assert callable(utils_hash_content)
    assert callable(utils_json_loads)
    assert callable(utils_flatten_dict)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.utils.mcp_tools import (
        utils_flatten_dict,
        utils_hash_content,
        utils_json_loads,
    )

    for fn in (utils_hash_content, utils_json_loads, utils_flatten_dict):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "utils"


def test_hash_content_sha256() -> None:
    """utils_hash_content returns a 64-char hex digest for sha256."""
    from codomyrmex.utils.mcp_tools import utils_hash_content

    result = utils_hash_content("hello world")
    assert isinstance(result, str)
    assert len(result) == 64  # sha256 hex length


def test_hash_content_md5() -> None:
    """utils_hash_content with md5 returns a 32-char hex digest."""
    from codomyrmex.utils.mcp_tools import utils_hash_content

    result = utils_hash_content("hello world", algorithm="md5")
    assert isinstance(result, str)
    assert len(result) == 32


def test_json_loads_valid() -> None:
    """utils_json_loads parses valid JSON correctly."""
    from codomyrmex.utils.mcp_tools import utils_json_loads

    result = utils_json_loads('{"key": "value"}')
    assert isinstance(result, dict)
    assert result["key"] == "value"


def test_json_loads_invalid_returns_default() -> None:
    """utils_json_loads returns default on invalid JSON."""
    from codomyrmex.utils.mcp_tools import utils_json_loads

    result = utils_json_loads("not json", default={"fallback": True})
    assert result == {"fallback": True}


def test_flatten_dict_nested() -> None:
    """utils_flatten_dict flattens nested dicts with dot separator."""
    from codomyrmex.utils.mcp_tools import utils_flatten_dict

    nested = {"a": {"b": {"c": 1}}, "d": 2}
    result = utils_flatten_dict(nested)
    assert isinstance(result, dict)
    assert "a.b.c" in result
    assert result["a.b.c"] == 1
    assert "d" in result


def test_flatten_dict_custom_sep() -> None:
    """utils_flatten_dict supports custom separators."""
    from codomyrmex.utils.mcp_tools import utils_flatten_dict

    nested = {"x": {"y": 42}}
    result = utils_flatten_dict(nested, sep="/")
    assert "x/y" in result
    assert result["x/y"] == 42


def test_flatten_dict_empty() -> None:
    """utils_flatten_dict with empty dict returns empty dict."""
    from codomyrmex.utils.mcp_tools import utils_flatten_dict

    result = utils_flatten_dict({})
    assert result == {}
