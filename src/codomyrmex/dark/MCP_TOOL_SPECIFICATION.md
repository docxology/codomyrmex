# Dark Module - MCP Tool Specification

## Overview

This document defines the Model Context Protocol (MCP) tools of the dark module. They are defined with `@mcp_tool` in `mcp_tools.py` and surfaced by the PAI MCP bridge as `codomyrmex.<name>`. Both tools are read-only: they report whether the PDF dependencies are installed and which filter presets exist.

Converting a PDF is not exposed as an MCP tool. Use the Python API instead:

```python
from codomyrmex.dark.pdf import apply_dark_mode

apply_dark_mode("input.pdf", "output.pdf", preset="dark")
```

PDF support needs the optional dependencies (`uv sync --extra dark`).

## Tools

### dark_status

Check whether the PDF dependencies are installed and list the preset names.

#### Schema

```json
{
  "name": "dark_status",
  "inputSchema": {"type": "object", "properties": {}, "required": []}
}
```

#### Response

```json
{
  "status": "success",
  "pdf_available": true,
  "version": "0.1.0",
  "presets": ["dark", "sepia", "high_contrast", "low_light"]
}
```

### dark_list_presets

List the filter presets with their parameter values.

#### Schema

```json
{
  "name": "dark_list_presets",
  "inputSchema": {"type": "object", "properties": {}, "required": []}
}
```

#### Response

```json
{
  "status": "success",
  "pdf_available": true,
  "presets": {
    "dark": {"inversion": 0.9, "brightness": 0.9, "contrast": 0.9, "sepia": 0.1},
    "sepia": {"inversion": 0.85, "brightness": 0.95, "contrast": 0.9, "sepia": 0.4},
    "high_contrast": {"inversion": 1.0, "brightness": 1.0, "contrast": 1.3, "sepia": 0.0},
    "low_light": {"inversion": 0.8, "brightness": 0.7, "contrast": 0.85, "sepia": 0.05}
  }
}
```

When the PDF dependencies are missing, `pdf_available` is `false`, `presets` is `{}` and `install_hint` is `"uv sync --extra dark"`.

#### Error Response

Both tools return `{"status": "error", "message": "<description>"}` if the module cannot be imported.

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
