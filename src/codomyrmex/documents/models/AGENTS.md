# documents/models — Agent Coordination

## Purpose

Defines the data models that represent documents and their metadata throughout the document processing pipeline. All document operations in `documents.core` and `documents.search` depend on these models.

## Key Components

| Component | Role |
|-----------|------|
| `DocumentType` | Enum classifying documents: `TEXT`, `MARKUP`, `STRUCTURED`, `BINARY`, `CODE` |
| `DocumentFormat` | Enum of 13 supported formats: `MARKDOWN`, `HTML`, `JSON`, `YAML`, `XML`, `CSV`, `PDF`, `TEXT`, `RST`, `TOML`, `INI`, `PYTHON`, `JS` |
| `_FORMAT_TYPE_MAP` | Dict mapping each `DocumentFormat` to its `DocumentType` category |
| `Document` | Primary dataclass holding content, format, metadata, timestamps, and an auto-generated UUID |
| `MetadataField` | Dataclass for a single metadata entry: `name`, `value`, `data_type`, `source` |
| `DocumentMetadata` | Dataclass for structured metadata: title, author, version, tags, custom fields |

## Operating Contracts

- `Document` fields: `content` (str or bytes), `format` (DocumentFormat), `file_path` (optional str), `encoding` (default `"utf-8"`), `metadata` (dict), `id` (auto UUID4), `document_type` (derived from format via `_FORMAT_TYPE_MAP`), `created_at`/`modified_at` (datetime).
- `Document.get_content_as_string()` decodes bytes content using the document's encoding.
- `Document.to_dict()` serializes all fields to a plain dict for JSON export.
- `DocumentMetadata.to_dict()` and `from_dict()` support round-trip serialization.
- `DocumentMetadata.copy()` returns a deep copy of the metadata instance.

## Integration Points

- **Core**: `DocumentReader`, `DocumentWriter`, `DocumentParser`, `DocumentValidator` all accept/return `Document` instances.
- **Search**: `InMemoryIndex` stores and retrieves `Document` objects by ID.
- **Serialization**: `to_dict()` methods enable JSON persistence and MCP tool responses.

## Navigation

- **Parent**: [documents README](../README.md)
- **Siblings**: [core](../core/AGENTS.md) | [search](../search/AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
