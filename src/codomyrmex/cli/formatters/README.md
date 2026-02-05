# cli/formatters

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

CLI output formatters. Provides consistent output formatting across different formats for the command-line interface. Includes plain text, JSON, rich bordered tables, and YAML-like formatters. All formatters implement a common `OutputFormatter` ABC with methods for generic data, tables, lists, and key-value pairs. The `TableFormatter` supports four border styles (single, double, ascii, none) with configurable headers and row separators.

## Key Exports

### Data Classes

- **`Column`** -- Table column definition with name, key, optional width, alignment (left/right/center), and optional formatter callable; provides `format_value()` for rendering

### Abstract Base

- **`OutputFormatter`** -- ABC defining `format_data(data)`, `format_table(data, columns)`, `format_list(items)`, and `format_key_value(data)` interface

### Formatter Implementations

- **`PlainFormatter`** -- Plain text output; auto-detects column widths, pipe-separated tables, indented lists
- **`JSONFormatter`** -- Machine-readable JSON output with configurable indent and compact mode
- **`TableFormatter`** -- Rich bordered table output with single/double/ascii/none border styles, optional header and row separators
- **`YAMLFormatter`** -- YAML-like human-readable output with recursive formatting of nested structures

### Factory

- **`create_formatter()`** -- Factory function accepting format_type ("plain", "json", "table", "yaml") with optional kwargs

## Directory Contents

- `__init__.py` - Package init; contains all formatter classes inline (single-file module)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [cli](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
