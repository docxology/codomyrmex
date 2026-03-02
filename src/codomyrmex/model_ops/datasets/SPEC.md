# Dataset Management — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a lightweight dataset abstraction for LLM training and evaluation data. Supports JSONL file I/O, format validation, and sanitization transforms (key removal, length filtering). No external dependencies beyond the standard library.

## Architecture

The module follows a data-container plus static-utility pattern. `Dataset` wraps a `list[dict[str, Any]]` with file I/O and validation methods. `DatasetSanitizer` provides stateless transform functions that produce new `Dataset` instances without mutating the original.

## Key Classes

### `Dataset`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `data: list[dict[str, Any]]` | `None` | Initialize with in-memory data |
| `from_file` | `file_path: str` | `Dataset` | Class method; loads JSONL file line-by-line |
| `to_jsonl` | `file_path: str` | `None` | Writes all items as JSONL to the given path |
| `validate` | — | `bool` | Returns `False` if any item lacks `messages` or `prompt` key |

### `DatasetSanitizer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `strip_keys` | `dataset: Dataset, keys_to_remove: list[str]` | `Dataset` | Remove specified keys from every item |
| `filter_by_length` | `dataset: Dataset, min_len: int, max_len: int` | `Dataset` | Keep only items whose content length falls within range |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`json`, `logging`)

## Constraints

- JSONL format required for file I/O (one JSON object per line).
- `validate()` stops at the first invalid item and logs the index via `logger.error`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `json.JSONDecodeError` raised if JSONL line is malformed during `from_file()`.
- Invalid dataset items logged with their index before `validate()` returns `False`.
- All errors logged before propagation.
