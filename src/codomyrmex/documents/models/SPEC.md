# documents/models — Technical Specification

## Overview

Defines the canonical data models for the document management subsystem. Two main dataclasses (`Document` and `DocumentMetadata`) plus two enums (`DocumentType` and `DocumentFormat`) form the schema that all document operations share.

## Architecture

Pure data layer with no I/O or external dependencies beyond the standard library. All classes are dataclasses for immutability-friendly usage and built-in equality.

## Enums

### DocumentType

| Value | Meaning |
|-------|---------|
| `TEXT` | Plain text documents |
| `MARKUP` | Markdown, HTML, RST |
| `STRUCTURED` | JSON, YAML, XML, CSV, TOML, INI |
| `BINARY` | PDF and other binary formats |
| `CODE` | Python, JavaScript source files |

### DocumentFormat (13 formats)

`MARKDOWN`, `HTML`, `JSON`, `YAML`, `XML`, `CSV`, `PDF`, `TEXT`, `RST`, `TOML`, `INI`, `PYTHON`, `JS`

Each format maps to a `DocumentType` via the module-level `_FORMAT_TYPE_MAP` dict.

## Dataclasses

### Document

| Field | Type | Default |
|-------|------|---------|
| `content` | `str \| bytes` | required |
| `format` | `DocumentFormat` | required |
| `file_path` | `str \| None` | `None` |
| `encoding` | `str` | `"utf-8"` |
| `metadata` | `dict[str, Any]` | `{}` |
| `id` | `str` | `uuid4().hex` |
| `document_type` | `DocumentType \| None` | derived from format |
| `created_at` | `datetime` | `datetime.now()` |
| `modified_at` | `datetime` | `datetime.now()` |

Methods: `get_content_as_string() -> str`, `to_dict() -> dict[str, Any]`.

### MetadataField

| Field | Type | Default |
|-------|------|---------|
| `name` | `str` | required |
| `value` | `Any` | required |
| `data_type` | `str` | `"string"` |
| `source` | `str` | `""` |

### DocumentMetadata

| Field | Type | Default |
|-------|------|---------|
| `title` | `str` | `""` |
| `author` | `str` | `""` |
| `created_at` | `datetime \| None` | `None` |
| `modified_at` | `datetime \| None` | `None` |
| `version` | `str` | `""` |
| `tags` | `list[str]` | `[]` |
| `custom_fields` | `dict[str, MetadataField]` | `{}` |

Methods: `to_dict() -> dict`, `from_dict(data) -> DocumentMetadata` (classmethod), `copy() -> DocumentMetadata`.

## Dependencies

Standard library only: `dataclasses`, `datetime`, `uuid`, `typing`.
