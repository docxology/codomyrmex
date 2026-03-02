# Output Formatters -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides pluggable output formatting for the codomyrmex CLI. Defines an `OutputFormatter` abstract base class with four abstract methods (`format_data`, `format_table`, `format_list`, `format_key_value`) and four concrete implementations: `PlainFormatter`, `JSONFormatter`, `TableFormatter` (Unicode/ASCII bordered tables), and `YAMLFormatter`. A `create_formatter` factory function selects the appropriate formatter by name.

## Architecture

Single-file design in `__init__.py`. The `OutputFormatter` ABC defines the formatting contract. Each formatter implements all four methods independently. `Column` dataclass provides column metadata with alignment, width, and optional custom formatter function. `create_formatter` maps string keys to formatter classes.

## Key Classes and Methods

### Column (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | -- | Display name (used as header) |
| `key` | `str` | -- | Data key to extract from row dicts |
| `width` | `int or None` | `None` | Fixed width; auto-detected if None |
| `align` | `str` | `"left"` | Alignment: `left`, `right`, or `center` |
| `formatter` | `Callable or None` | `None` | Optional value transformation function |

Method `format_value(value)` applies the formatter, converts to string, and pads to width with alignment.

### OutputFormatter (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `format_data` | `data: Any` | `str` | Format arbitrary data for output |
| `format_table` | `data: list[dict], columns: list[Column] or None` | `str` | Format tabular data with optional column specs |
| `format_list` | `items: list[Any]` | `str` | Format a list of items |
| `format_key_value` | `data: dict[str, Any]` | `str` | Format key-value pairs |

### PlainFormatter

Auto-detects column widths from data. Tables use `" | "` separators with a dash separator line. Lists are prefixed with `"  - "`. Key-value pairs are left-aligned with colon separator.

### JSONFormatter

| Constructor | `indent: int = 2, compact: bool = False` |
|-------------|------------------------------------------|

When `compact=True`, sets `indent=None` for single-line output. All four methods delegate to `json.dumps` with `default=str`.

### TableFormatter

| Constructor | `border_style: str = "single", show_header: bool = True, row_separator: bool = False` |
|-------------|----------------------------------------------------------------------------------------|

Border styles: `single` (Unicode box-drawing: `---`), `double` (double-line Unicode: `===`), `ascii` (`+--+`), `none` (spaces). Tables include top border, optional header with separator, data rows with optional row separators, and bottom border. `format_list` wraps items into single-column table. `format_key_value` wraps into two-column Key/Value table.

### YAMLFormatter

| Constructor | `indent: int = 2` |
|-------------|-------------------|

Recursive `_format_value` handles dicts (colon-separated), lists (dash-prefixed), `None` as `"null"`, booleans as `"true"`/`"false"`, strings with colons or newlines are double-quoted.

### create_formatter (factory function)

| Parameter | Type | Description |
|-----------|------|-------------|
| `format_type` | `str` | One of `"plain"`, `"json"`, `"table"`, `"yaml"` |
| `**kwargs` | -- | Passed to formatter constructor |

Raises `ValueError` for unknown format types.

## Dependencies

- **Internal**: None
- **External**: `json`, `abc`

## Constraints

- `PlainFormatter.format_table` auto-computes column widths as `max(header_len, max_value_len)` when `Column.width` is None.
- `TableFormatter` border character sets are hardcoded in `_get_borders()` for four styles.
- `JSONFormatter` uses `default=str` for non-serializable types.
- `YAMLFormatter` does not use the `pyyaml` library; it implements YAML-like formatting manually.
- All formatters return strings; none write to stdout directly.

## Error Handling

- `create_formatter` raises `ValueError` for unrecognized `format_type`.
- `Column.format_value` converts `None` values to empty string.
- No formatter method raises exceptions for malformed input; they degrade gracefully via `str()` conversion.
