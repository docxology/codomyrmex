# Codomyrmex Agents — src/codomyrmex/model_ops/datasets

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides dataset management utilities for ML training and evaluation workflows. Handles loading datasets from JSONL files, serializing them back, validating LLM-compatible formats (requiring `messages` or `prompt` keys), and sanitizing data by stripping keys or filtering by content length.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `datasets.py` | `Dataset` | Core dataset container; loads from JSONL via `from_file()`, saves via `to_jsonl()`, validates LLM format via `validate()` |
| `datasets.py` | `DatasetSanitizer` | Static utility class for data cleaning; `strip_keys()` removes specified fields, `filter_by_length()` filters items by content character count |

## Operating Contracts

- `Dataset.validate()` checks every item for `messages` or `prompt` keys; returns `False` on first invalid item and logs the index.
- `Dataset.from_file()` expects one JSON object per line (JSONL format); invalid JSON will raise `json.JSONDecodeError`.
- `DatasetSanitizer` methods return new `Dataset` instances (immutable transform pattern).
- `filter_by_length()` measures length of the `prompt` field first, falling back to `messages` as a string.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`json`, `logging`)
- **Used by**: `model_ops.fine_tuning` (imports `Dataset` for fine-tuning jobs)

## Navigation

- **Parent**: [model_ops](../README.md)
- **Root**: [Root](../../../../README.md)
