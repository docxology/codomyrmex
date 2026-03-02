# Terminal Utilities -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Terminal output formatting and command execution utilities providing ANSI color support with auto-detection, Unicode box-drawing tables, progress bars, and a subprocess runner with real-time output streaming.

## Architecture

Two main classes with a supporting MCP tool function:

- `TerminalFormatter`: Stateless formatter with ANSI color/style application, auto-detection of terminal color support, and structured output methods (headers, tables, boxes, progress bars).
- `CommandRunner`: Subprocess wrapper using `TerminalFormatter` for formatted command execution with real-time stdout/stderr streaming.
- `create_ascii_art`: MCP-exposed tool function for text-to-ASCII-art conversion.

## Key Classes

### `TerminalFormatter`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `use_colors: bool = None` | `None` | Auto-detects TTY color support if `use_colors` is None |
| `color` | `text: str, color: str, style: str = None` | `str` | Apply ANSI color and optional style (BOLD, ITALIC, etc.) |
| `success` / `error` / `warning` / `info` | `text: str` | `str` | Semantic message formatting with color and icon |
| `header` | `text: str, char: str, width: int` | `str` | Centered header between separator lines |
| `progress_bar` | `current: int, total: int, width: int` | `str` | Unicode block progress bar with percentage |
| `table` | `headers: list[str], rows: list[list[str]]` | `str` | Unicode box-drawing table with auto-width columns |
| `box` | `content: str, title: str = None` | `str` | Content wrapped in Unicode border with optional title |

### `CommandRunner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run_command` | `command: list[str], cwd, show_output, timeout` | `dict` | Execute subprocess with formatted output; returns dict with returncode, stdout, stderr, success |
| `run_python_module` | `module: str, args: list[str]` | `dict` | Run `python -m <module>` with formatting |
| `check_tool_available` | `tool: str` | `bool` | Check if CLI tool is on PATH via `shutil.which` |
| `get_system_info` | none | `dict` | System diagnostics: Python version, platform, tool availability |
| `run_diagnostic` | none | `None` | Print formatted diagnostic table |

### `create_ascii_art` (MCP Tool)

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Text to convert |
| `style` | `str` | `"simple"` (passthrough) or `"block"` (5-row block letters) |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (structured logging), `codomyrmex.model_context_protocol.decorators` (`@mcp_tool`)
- **External**: `os`, `sys`, `shutil`, `subprocess`, `pathlib` (stdlib)

## Constraints

- Color auto-detection checks `sys.stdout.isatty()`, `TERM`, `WT_SESSION`, and `COLORTERM` environment variables.
- Supported ANSI colors: 16 standard colors (8 normal + 8 bright). No 256-color or truecolor support.
- `progress_bar` handles `total=0` gracefully (shows 100%).
- Block-style ASCII art supports only letters A-C in current implementation; other characters render as solid blocks.
- Zero-mock: real subprocess execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `run_command` catches `subprocess.TimeoutExpired` and generic `Exception`, returning error dicts rather than raising.
- All errors logged before propagation.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
- Parent: [terminal_interface](../README.md)
