# Agent Guidelines - Documents

**Version**: v1.2.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Document processing: reading, writing, parsing, extraction, and transformation. Provides a unified interface for multiple formats (Markdown, JSON, YAML, HTML, CSV, PDF, XML, plain text) with automatic format detection, encoding detection, and metadata extraction. Use `DocumentReader` and `DocumentWriter` for file I/O, `convert_document` for format conversion, and `merge_documents` / `split_document` for content manipulation. The `Document` dataclass is the central model, pairing content with `DocumentMetadata` and format information.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports all public classes and functions; feature-flags availability per subsystem (`CORE_AVAILABLE`, `FORMATS_AVAILABLE`, etc.) |
| `core/document_reader.py` | `DocumentReader` class and `read_document()` convenience function with auto-detection |
| `core/document_writer.py` | `DocumentWriter` class and `write_document()` convenience function; creates parent dirs |
| `core/document_parser.py` | `DocumentParser` and `parse_document()` for structured content extraction |
| `core/document_validator.py` | `DocumentValidator`, `ValidationResult`, and `validate_document()` |
| `models/document.py` | `Document` dataclass, `DocumentFormat` enum, `DocumentType` enum |
| `models/metadata.py` | `DocumentMetadata` dataclass, `MetadataField` dataclass |
| `transformation/converter.py` | `convert_document()` for format-to-format conversion |
| `transformation/merger.py` | `merge_documents()` for combining multiple documents |
| `transformation/splitter.py` | `split_document()` for splitting documents by sections or size |
| `transformation/formatter.py` | `format_document()` for applying formatting rules |
| `formats/markdown_handler.py` | `read_markdown()` / `write_markdown()` |
| `formats/json_handler.py` | `read_json()` / `write_json()` |
| `formats/yaml_handler.py` | `read_yaml()` / `write_yaml()` |
| `formats/html_handler.py` | `read_html()` / `write_html()` |
| `formats/xml_handler.py` | `read_xml()` / `write_xml()` |
| `formats/csv_handler.py` | `read_csv()` / `write_csv()` |
| `formats/pdf_handler.py` | `read_pdf()` / `write_pdf()` / `PDFDocument` (optional dependency) |
| `search/indexer.py` | `InMemoryIndex`, `create_index()`, `index_document()` |
| `search/searcher.py` | `search_documents()`, `search_index()` |
| `search/query_builder.py` | `QueryBuilder`, `build_query()` |

## Key Classes

- **Document** -- Core dataclass holding content, `DocumentFormat`, `DocumentType`, encoding, `DocumentMetadata`, and timestamps. Use `get_content_as_string()` for text representation.
- **DocumentMetadata** -- Metadata container with `title`, `author`, `created_at`, `modified_at`, `version`, `tags`, and `custom_fields`. Supports `update()`, `copy()`, `to_dict()`, and `from_dict()`.
- **MetadataField** -- Single metadata field with name, value, data_type, and source.
- **DocumentFormat** -- Enum: MARKDOWN, TEXT, HTML, JSON, XML, YAML, CSV, PDF, RTF, DOCX, XLSX, PY, JS.
- **DocumentType** -- Enum: TEXT, MARKUP, STRUCTURED, BINARY, CODE.
- **DocumentReader** -- Reads files with auto-format and auto-encoding detection. Delegates to per-format handlers.
- **DocumentWriter** -- Writes documents to files. Automatically creates parent directories.
- **DocumentParser** -- Extracts structured content from raw documents.
- **DocumentValidator** / **ValidationResult** -- Validates document structure and content.
- **InMemoryIndex** -- In-memory search index for full-text document search.
- **QueryBuilder** -- Builds search queries for the index.
- **PDFDocument** -- PDF-specific document wrapper (requires optional `pdf` dependency).

## Agent Instructions

1. **Prefer read_document** -- Let the module handle format and encoding detection.
2. **Metadata first** -- Use `doc.metadata.update()` to manage document properties.
3. **Structured Content** -- For CSV, JSON, and YAML, `doc.content` will be a native Python list or dict.
4. **Transformations** -- Use `convert_document` before merging if formats differ.
5. **Zero-Mock Policy** -- All tests must use real file I/O and functional implementations.

## Operating Contracts

- `DocumentReader.read()` is read-only -- it never modifies the source file.
- `DocumentWriter.write()` automatically creates parent directories via `file_path.parent.mkdir(parents=True, exist_ok=True)`.
- `Document.metadata` is mutable via `update()`, but **do not replace the metadata object after document creation** -- always use `doc.metadata.update()` to modify in-place.
- `convert_document()` always returns a **new** `Document` instance -- it never mutates the input document.
- `DocumentMetadata.copy()` returns a deep copy via `copy.deepcopy()` -- safe for independent modification.
- CSV content for `DocumentWriter` **must** be a `list[dict]` -- other shapes raise `DocumentWriteError`.
- Format auto-detection falls back to `DocumentFormat.TEXT` for unknown extensions.
- **DO NOT** call `write_document()` with a `Document` whose `format` is `None` without providing an explicit `format` argument.
- **DO NOT** modify `Document.id` or `Document.created_at` after construction -- these are identity fields.

## Common Patterns

### Read, Transform, Write Pipeline

```python
from codomyrmex.documents import (
    read_document, write_document, convert_document, DocumentFormat
)

# Read a markdown file (format and encoding auto-detected)
doc = read_document("report.md")
print(f"Title: {doc.metadata.title}, Format: {doc.format.value}")

# Convert to HTML
html_doc = convert_document(doc, DocumentFormat.HTML)

# Write the converted document
write_document(html_doc, "report.html")
```

### Merge and Split

```python
from codomyrmex.documents import (
    read_document, merge_documents, split_document
)

doc_a = read_document("part_a.md")
doc_b = read_document("part_b.md")

merged = merge_documents([doc_a, doc_b])
sections = split_document(merged, {"method": "by_sections"})
```

### Search and Index

```python
from codomyrmex.documents import create_index, index_document, search_documents

index = create_index()
index_document(read_document("notes.md"), index)
matches = search_documents("target keyword", index)
```

## Testing Patterns

```python
# Use tmp_path fixture for zero-mock file tests
from codomyrmex.documents import Document, DocumentFormat, write_document, read_document

def test_round_trip(tmp_path):
    f = tmp_path / "test.md"
    doc = Document(content="# Title\nBody text", format=DocumentFormat.MARKDOWN)
    write_document(doc, f)
    result = read_document(f)
    assert result.format == DocumentFormat.MARKDOWN
    assert "Title" in result.get_content_as_string()
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |
| **Researcher** | Read-only | Document reading and search operations | SAFE |

### Engineer Agent
**Use Cases**: Read, write, and transform documents during BUILD/EXECUTE phases. Create conversion pipelines. Manage document metadata.

### Architect Agent
**Use Cases**: Review document format support matrix, design transformation pipelines, assess format handler architecture.

### QATester Agent
**Use Cases**: Validate round-trip read/write correctness, verify format auto-detection, test conversion fidelity.

### Researcher Agent
**Use Cases**: Read documents and search indexes for content analysis and information extraction.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
