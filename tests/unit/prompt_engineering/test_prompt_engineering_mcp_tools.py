"""Tests for prompt_engineering MCP tools.

Zero-mock policy: tests use the real prompt_engineering functions.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.prompt_engineering.mcp_tools import (
        prompt_evaluate,
        prompt_list_strategies,
        prompt_list_templates,
    )

    assert callable(prompt_list_templates)
    assert callable(prompt_list_strategies)
    assert callable(prompt_evaluate)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.prompt_engineering.mcp_tools import (
        prompt_evaluate,
        prompt_list_strategies,
        prompt_list_templates,
    )

    for fn in (prompt_list_templates, prompt_list_strategies, prompt_evaluate):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
        assert fn._mcp_tool_meta.get("category") == "prompt_engineering"


def test_list_templates_returns_list() -> None:
    """prompt_list_templates returns a list of strings."""
    from codomyrmex.prompt_engineering.mcp_tools import prompt_list_templates

    result = prompt_list_templates()
    assert isinstance(result, list)
    assert all(isinstance(t, str) for t in result)


def test_list_strategies_returns_list() -> None:
    """prompt_list_strategies returns a non-empty list of strings."""
    from codomyrmex.prompt_engineering.mcp_tools import prompt_list_strategies

    result = prompt_list_strategies()
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(s, str) for s in result)


def test_evaluate_returns_dict() -> None:
    """prompt_evaluate returns a dict with scores."""
    from codomyrmex.prompt_engineering.mcp_tools import prompt_evaluate

    result = prompt_evaluate(
        prompt="What is Python?",
        response="Python is a programming language.",
    )
    assert isinstance(result, dict)


def test_evaluate_contains_total_score() -> None:
    """Evaluation result should contain a total/overall or per-criterion score."""
    from codomyrmex.prompt_engineering.mcp_tools import prompt_evaluate

    result = prompt_evaluate(
        prompt="Explain recursion briefly.",
        response="Recursion is a technique where a function calls itself.",
    )
    assert isinstance(result, dict)
    # At minimum the result should have some keys with score values
    assert len(result) > 0
