"""Tests for model_ops MCP tools.

Zero-mock policy: tests use the real scorer classes and Dataset/DatasetSanitizer.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.model_ops.mcp_tools import (
        model_ops_list_scorers,
        model_ops_sanitize_dataset,
        model_ops_score_output,
    )

    assert callable(model_ops_score_output)
    assert callable(model_ops_sanitize_dataset)
    assert callable(model_ops_list_scorers)


def test_list_scorers_returns_list() -> None:
    """model_ops_list_scorers returns a non-empty list of strings."""
    from codomyrmex.model_ops.mcp_tools import model_ops_list_scorers

    scorers = model_ops_list_scorers()
    assert isinstance(scorers, list)
    assert len(scorers) > 0
    assert "exact_match" in scorers
    assert "contains" in scorers


def test_score_output_exact_match_hit() -> None:
    """model_ops_score_output returns 1.0 exact_match for identical strings."""
    from codomyrmex.model_ops.mcp_tools import model_ops_score_output

    result = model_ops_score_output("hello", "hello", scorers=["exact_match"])
    assert result["scores"]["exact_match"] == 1.0


def test_score_output_exact_match_miss() -> None:
    """model_ops_score_output returns 0.0 exact_match for different strings."""
    from codomyrmex.model_ops.mcp_tools import model_ops_score_output

    result = model_ops_score_output("hello", "world", scorers=["exact_match"])
    assert result["scores"]["exact_match"] == 0.0


def test_score_output_default_scorers() -> None:
    """model_ops_score_output uses exact_match and contains by default."""
    from codomyrmex.model_ops.mcp_tools import model_ops_score_output

    result = model_ops_score_output("the quick brown fox", "quick")
    assert "exact_match" in result["scores"]
    assert "contains" in result["scores"]
    assert "overall" in result


def test_score_output_contains_hit() -> None:
    """contains scorer returns 1.0 when reference is a substring of output."""
    from codomyrmex.model_ops.mcp_tools import model_ops_score_output

    result = model_ops_score_output("the quick brown fox", "quick", scorers=["contains"])
    assert result["scores"]["contains"] == 1.0


def test_sanitize_dataset_filters_short_entries() -> None:
    """model_ops_sanitize_dataset removes entries shorter than min_length."""
    from codomyrmex.model_ops.mcp_tools import model_ops_sanitize_dataset

    data = [
        {"prompt": "hi", "completion": ""},          # length=2, too short
        {"prompt": "hello world", "completion": "!"},  # length=12, ok
    ]
    result = model_ops_sanitize_dataset(data, min_length=5, max_length=100)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["prompt"] == "hello world"


def test_sanitize_dataset_empty_input() -> None:
    """model_ops_sanitize_dataset returns empty list for empty input."""
    from codomyrmex.model_ops.mcp_tools import model_ops_sanitize_dataset

    assert model_ops_sanitize_dataset([]) == []


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.model_ops.mcp_tools import (
        model_ops_list_scorers,
        model_ops_sanitize_dataset,
        model_ops_score_output,
    )

    for fn in (model_ops_score_output, model_ops_sanitize_dataset, model_ops_list_scorers):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
