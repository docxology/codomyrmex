# documents/core — Technical Specification

## Overview

The core subpackage provides four complementary classes for document lifecycle operations: reading from disk, writing to disk, parsing in-memory content, and validating document correctness.

## Architecture

All classes are stateless and instantiated without arguments. Each exposes a single primary method plus a module-level convenience function that wraps it.

## Key Classes

### DocumentReader

| Method | Signature | Returns |
|--------|-----------|---------|
| `read` | `(file_path: str, format: DocumentFormat \| None = None) -> Document` | Loaded document |
| `_detect_format` | `(file_path: str) -> DocumentFormat` | Auto-detected format via MIME type |

Supports formats: `MARKDOWN`, `JSON`, `YAML`, `PDF`, `TEXT`. Uses `mimetypes.guess_type()` for detection. Falls back to `TEXT` for unknown types.

### DocumentWriter

| Method | Signature | Returns |
|--------|-----------|---------|
| `write` | `(document: Document, output_path: str) -> None` | None |

Creates parent directories via `os.makedirs(exist_ok=True)`. Encodes content using document's `encoding` attribute (default UTF-8).

### DocumentValidator

| Method | Signature | Returns |
|--------|-----------|---------|
| `validate` | `(document: Document) -> ValidationResult` | Validation result |
| `_validate_json` | `(content: str) -> ValidationResult` | JSON parse check |
| `_validate_yaml` | `(content: str) -> ValidationResult` | YAML parse check |
| `_validate_against_schema` | `(data: dict, schema: dict) -> ValidationResult` | jsonschema check |

`ValidationResult` is a dataclass with fields: `is_valid: bool`, `errors: list[str]`, `warnings: list[str]`.

### DocumentParser

| Method | Signature | Returns |
|--------|-----------|---------|
| `parse` | `(content: str, format: DocumentFormat \| None = None) -> Document` | Parsed document |
| `_parse_content` | `(content: str, format: DocumentFormat) -> Any` | Format-specific parsed data |

## Dependencies

- `mimetypes` (stdlib) for format detection
- `json`, `yaml` (PyYAML) for structured format parsing
- `jsonschema` (optional) for schema validation
- `documents.models.Document`, `DocumentFormat`

## Error Handling

- `FileNotFoundError` raised by `DocumentReader.read()` for missing files.
- `ValidationResult.errors` collects parse errors without raising exceptions.
- `json.JSONDecodeError` and `yaml.YAMLError` caught and returned as validation errors.
