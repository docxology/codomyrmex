"""Tests for templating MCP tools.

Zero-mock policy: tests use the real Jinja2 template engine.
"""

from __future__ import annotations


def test_import_mcp_tools() -> None:
    """Both MCP tools are importable without errors."""
    from codomyrmex.templating.mcp_tools import template_render, template_validate

    assert callable(template_render)
    assert callable(template_validate)


def test_render_simple_template() -> None:
    """template_render substitutes context variables."""
    from codomyrmex.templating.mcp_tools import template_render

    result = template_render("Hello {{ name }}!", {"name": "World"})
    assert result == "Hello World!"


def test_render_no_context() -> None:
    """template_render works with an empty context."""
    from codomyrmex.templating.mcp_tools import template_render

    result = template_render("static text")
    assert result == "static text"


def test_render_with_loop() -> None:
    """template_render handles Jinja2 for-loops."""
    from codomyrmex.templating.mcp_tools import template_render

    result = template_render(
        "{% for item in items %}{{ item }},{% endfor %}", {"items": [1, 2, 3]}
    )
    assert result == "1,2,3,"


def test_validate_valid_template() -> None:
    """template_validate returns valid=True for syntactically correct template."""
    from codomyrmex.templating.mcp_tools import template_validate

    result = template_validate("Hello {{ name }}!")
    assert result["valid"] is True
    assert result["error"] is None


def test_validate_invalid_template() -> None:
    """template_validate returns valid=False for a broken template."""
    from codomyrmex.templating.mcp_tools import template_validate

    # Unclosed block tag — Jinja2 parse error
    result = template_validate("{% if %}broken")
    assert result["valid"] is False
    assert isinstance(result["error"], str)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta for bridge discovery."""
    from codomyrmex.templating.mcp_tools import template_render, template_validate

    for fn in (template_render, template_validate):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
