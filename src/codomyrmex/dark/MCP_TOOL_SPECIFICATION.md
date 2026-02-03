# Dark Module - MCP Tool Specification

## Overview

This document defines Model Context Protocol (MCP) tools for the dark module, enabling AI models to apply dark mode filters to PDF documents.

## Tools

### apply_dark_mode_pdf

Apply dark mode filters to a PDF document.

#### Schema

```json
{
  "name": "apply_dark_mode_pdf",
  "description": "Apply dark mode filters to a PDF document. Inverts colors and adjusts brightness, contrast, and sepia for comfortable reading in dark environments.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "input_path": {
        "type": "string",
        "description": "Path to the input PDF file"
      },
      "output_path": {
        "type": "string",
        "description": "Path for the output PDF file"
      },
      "preset": {
        "type": "string",
        "enum": ["dark", "sepia", "high_contrast", "low_light"],
        "default": "dark",
        "description": "Named filter preset. 'dark' for standard dark mode, 'sepia' for warm tones, 'high_contrast' for maximum contrast, 'low_light' for dim environments"
      },
      "inversion": {
        "type": "number",
        "minimum": 0.0,
        "maximum": 1.0,
        "description": "Inversion amount (0.0-1.0). Overrides preset value if provided"
      },
      "brightness": {
        "type": "number",
        "minimum": 0.1,
        "maximum": 3.0,
        "description": "Brightness multiplier (0.1-3.0). Overrides preset value if provided"
      },
      "contrast": {
        "type": "number",
        "minimum": 0.1,
        "maximum": 3.0,
        "description": "Contrast multiplier (0.1-3.0). Overrides preset value if provided"
      },
      "sepia": {
        "type": "number",
        "minimum": 0.0,
        "maximum": 1.0,
        "description": "Sepia amount (0.0-1.0). Overrides preset value if provided"
      },
      "dpi": {
        "type": "integer",
        "minimum": 36,
        "default": 150,
        "description": "Resolution for rendering PDF pages (default 150)"
      }
    },
    "required": ["input_path", "output_path"]
  }
}
```

#### Example

```json
{
  "name": "apply_dark_mode_pdf",
  "arguments": {
    "input_path": "/path/to/document.pdf",
    "output_path": "/path/to/document_dark.pdf",
    "preset": "dark"
  }
}
```

#### Response

```json
{
  "success": true,
  "output_path": "/path/to/document_dark.pdf",
  "pages_processed": 10,
  "preset": "dark",
  "filters_applied": {
    "inversion": 0.90,
    "brightness": 0.90,
    "contrast": 0.90,
    "sepia": 0.10
  }
}
```

#### Error Response

```json
{
  "success": false,
  "error": "FileNotFoundError",
  "message": "Input PDF not found: /path/to/document.pdf"
}
```
