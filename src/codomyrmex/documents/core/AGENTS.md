# documents/core — Agent Coordination

## Purpose

Provides document I/O and validation primitives that agents use to read, write, parse, and validate documents in multiple formats (Markdown, JSON, YAML, PDF, plain text).

## Key Components

| Component | Role |
|-----------|------|
| `DocumentReader` | Reads files with auto-format detection via MIME type and encoding detection |
| `DocumentWriter` | Writes `Document` objects to disk, auto-creating parent directories |
| `DocumentValidator` | Validates document content; supports JSON/YAML syntax and jsonschema validation |
| `DocumentParser` | Parses raw content strings into `Document` objects with format inference |
| `read_document()` | Convenience function wrapping `DocumentReader.read()` |
| `write_document()` | Convenience function wrapping `DocumentWriter.write()` |
| `validate_document()` | Convenience function wrapping `DocumentValidator.validate()` |
| `parse_document()` | Convenience function wrapping `DocumentParser.parse()` |

## Operating Contracts

- `DocumentReader.read(path)` returns a `Document` with content loaded as bytes or string depending on format.
- `DocumentWriter.write(doc, path)` serializes the document content to the specified path. Creates intermediate directories.
- `DocumentValidator.validate(doc)` returns a `ValidationResult` with `is_valid`, `errors`, and `warnings` lists.
- Schema validation via `_validate_against_schema()` requires the `jsonschema` package.
- All four classes follow the same pattern: stateless class instantiation, single primary method, plus a module-level convenience function.

## Integration Points

- **Models**: Uses `Document`, `DocumentFormat`, and `DocumentType` from `documents.models`.
- **Search**: Validated and parsed documents feed into `documents.search` for indexing.
- **Logging**: Uses `codomyrmex.logging_monitoring.get_logger` for structured logging.

## Navigation

- **Parent**: [documents README](../README.md)
- **Siblings**: [models](../models/AGENTS.md) | [search](../search/AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
