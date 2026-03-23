"""MCP tools for the terminal_interface module."""

import os
import shutil

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="terminal_interface")
def terminal_info() -> dict:
    """Get current terminal environment information.

    Returns:
        Dictionary with terminal type, shell, dimensions, and capability flags.
    """
    try:
        size = shutil.get_terminal_size(fallback=(80, 24))
        return {
            "status": "success",
            "terminal": os.environ.get("TERM", "unknown"),
            "shell": os.environ.get("SHELL", "unknown"),
            "columns": size.columns,
            "lines": size.lines,
            "colorterm": os.environ.get("COLORTERM", ""),
            "term_program": os.environ.get("TERM_PROGRAM", ""),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="terminal_interface")
def terminal_list_themes() -> dict:
    """list available terminal output themes for Codomyrmex rendering.

    Returns:
        Dictionary with available themes and their descriptions.
    """
    try:
        themes = {
            "default": "Standard terminal output with basic formatting",
            "rich": "Rich text formatting with colors, tables, and syntax highlighting",
            "minimal": "Minimal output, no decorations or colors",
            "json": "JSON-structured output for machine consumption",
        }
        return {"status": "success", "themes": themes, "count": len(themes)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="terminal_interface")
def terminal_format(
    text: str,
    style: str = "default",
    width: int = 0,
) -> dict:
    """Format text for terminal output using a named style.

    Args:
        text: Text content to format
        style: Output style ('default', 'title', 'success', 'error', 'warning', 'code')
        width: Wrap width in columns (0 = auto-detect from terminal)

    Returns:
        Dictionary with formatted text and applied style metadata.
    """
    try:
        if width <= 0:
            width = shutil.get_terminal_size(fallback=(80, 24)).columns

        style_prefixes = {
            "default": "",
            "title": "# ",
            "success": "✓ ",
            "error": "✗ ",
            "warning": "⚠ ",
            "code": "  ",
        }
        prefix = style_prefixes.get(style, "")
        lines = text.split("\n")
        formatted_lines = [f"{prefix}{line}" for line in lines]

        return {
            "status": "success",
            "formatted": "\n".join(formatted_lines),
            "style": style,
            "width": width,
            "line_count": len(formatted_lines),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
