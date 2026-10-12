# terminal_interface - MCP Tool Specification

## Overview

This document specifies the Model Context Protocol (MCP) tools provided by the `terminal_interface` module. The tools are defined with the `@mcp_tool` decorator and are surfaced by the PAI MCP bridge as `codomyrmex.<name>`.

| Tool | Defined in | Purpose |
| :--- | :--- | :--- |
| `terminal_info` | `mcp_tools.py` | Report terminal type, shell and dimensions |
| `terminal_list_themes` | `mcp_tools.py` | List the named output themes |
| `terminal_format` | `mcp_tools.py` | Prefix and measure text for a named style |
| `create_ascii_art` | `utils/terminal_utils.py` | Render text as plain or block-letter ASCII art |

None of these tools execute commands or start shells.

## Tool Registration

Tools are defined with the `@mcp_tool` decorator in `mcp_tools.py` (and `utils/terminal_utils.py`) and are auto-discovered by the PAI MCP bridge; no manual registration call is needed. The decorated functions can also be called directly:

```python
from codomyrmex.terminal_interface.mcp_tools import terminal_info, terminal_list_themes

info = terminal_info()
themes = terminal_list_themes()
```

## Related Documentation

- [Module README](./README.md)
- [API Specification](./API_SPECIFICATION.md)
- [Usage Examples](../README.md) (See README for examples)

---

## Tool: `terminal_info`

### 1. Tool Purpose and Description

Reads the terminal environment: `TERM`, `SHELL`, `COLORTERM`, `TERM_PROGRAM` and the terminal size (falling back to 80x24).

### 2. Invocation Name

`terminal_info`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "terminal": "xterm-256color",
  "shell": "/bin/zsh",
  "columns": 80,
  "lines": 24,
  "colorterm": "truecolor",
  "term_program": ""
}
```

Unset variables are reported as `"unknown"` (`terminal`, `shell`) or `""` (`colorterm`, `term_program`). On failure the tool returns `{"status": "error", "message": "<error>"}`.

## Tool: `terminal_list_themes`

### 1. Tool Purpose and Description

Lists the named terminal output themes (`default`, `rich`, `minimal`, `json`) with one-line descriptions.

### 2. Invocation Name

`terminal_list_themes`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "themes": {
    "default": "Standard terminal output with basic formatting",
    "rich": "Rich text formatting with colors, tables, and syntax highlighting",
    "minimal": "Minimal output, no decorations or colors",
    "json": "JSON-structured output for machine consumption"
  },
  "count": 4
}
```

## Tool: `terminal_format`

### 1. Tool Purpose and Description

Prefixes every line of `text` with the marker for `style` followed by a space (`title` → `#`, `success` → `✓`, `error` → `✗`, `warning` → `⚠`); `code` indents by two spaces and `default` or unknown styles add nothing. No ANSI colour codes are added and lines are not wrapped; `width` is only reported back.

### 2. Invocation Name

`terminal_format`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `string` | Yes | Text to format | `"Build finished"` |
| `style` | `string` | No | `default`, `title`, `success`, `error`, `warning` or `code` (default `default`) | `"success"` |
| `width` | `integer` | No | Width to report; `0` or less uses the terminal width (default `0`) | `100` |

### 4. Output Schema (Return Value)

```json
{
  "status": "success",
  "formatted": "✓ Build finished",
  "style": "success",
  "width": 100,
  "line_count": 1
}
```

## Tool: `create_ascii_art`

### 1. Tool Purpose and Description

Returns `text` unchanged for the `simple` style, or five rows of block letters for the `block` style. Block glyphs exist for `A`, `B`, `C` and space; other characters render as a solid block. Unknown styles return `text` unchanged.

### 2. Invocation Name

`create_ascii_art`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `string` | Yes | Text to render | `"CAB"` |
| `style` | `string` | No | `simple` or `block` (default `simple`) | `"block"` |

### 4. Output Schema (Return Value)

A plain string (not a dictionary): the ASCII art, with rows separated by newlines.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
