# Documents Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Document handling module providing document parsing, generation, and manipulation capabilities. Supports multiple formats including Markdown, JSON, YAML, HTML, XML, CSV, PDF, and plain text.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Read and parse documents in multiple formats | Direct Python import |
| **BUILD** | Generate documents and merge content from multiple sources | Direct Python import |
| **EXECUTE** | Transform document formats and convert between types | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent uses `read_document` and `convert_document` to parse inputs during OBSERVE and transform outputs during EXECUTE.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`DocumentsConfig`** — Configuration for document operations.
- **`DocumentsError`** — Base exception class for all Documents module errors.
- **`DocumentReadError`** — Raised when document reading fails.
- **`DocumentWriteError`** — Raised when document writing fails.
- **`DocumentParseError`** — Raised when document parsing fails.
- **`DocumentValidationError`** — Raised when document validation fails.
- **`DocumentConversionError`** — Raised when document format conversion fails.
- **`UnsupportedFormatError`** — Raised when an unsupported document format is requested.

### Functions
- **`get_config()`** — Get the global documents configuration.
- **`set_config()`** — Set the global documents configuration.

### Submodules
- **`core/`** — Core document operations.
- **`formats/`** — Format-specific document handlers.
- **`metadata/`** — Document metadata operations.
- **`models/`** — Document data models.
- **`search/`** — Document search and indexing operations.
- **`transformation/`** — Document transformation operations.
- **`utils/`** — Document utilities.

## Quick Start

```python
from codomyrmex.documents import (
    Document, DocumentFormat,
    read_document, write_document, parse_document, validate_document,
    convert_document, merge_documents, split_document,
)

# Read a document (auto-detects format and encoding)
doc = read_document("example.md")

# Create a document in-memory
doc = Document(content="# Hello World", format=DocumentFormat.MARKDOWN)

# Write to file
write_document(doc, "output.md")

# Convert between formats
json_doc = convert_document(doc, DocumentFormat.JSON)

# Merge multiple documents
merged = merge_documents([doc1, doc2, doc3])

# Split a document
chunks = split_document(doc, {"method": "by_sections"})
```

## Submodules

### Core (`core/`)
- `DocumentReader` / `read_document` - Read documents from files with auto-detection
- `DocumentWriter` / `write_document` - Write documents to files
- `DocumentParser` / `parse_document` - Parse content strings into Document objects
- `DocumentValidator` / `validate_document` - Validate documents against schemas

### Models (`models/`)
- `Document` - Core document dataclass with auto-generated ID, type detection, and content serialization
- `DocumentFormat` - Enum of supported formats (MARKDOWN, TEXT, HTML, JSON, XML, YAML, CSV, PDF, etc.)
- `DocumentType` - Enum of document types (TEXT, MARKUP, STRUCTURED, BINARY, CODE)
- `DocumentMetadata` - Metadata container with serialization and copy support
- `MetadataField` - Individual metadata field descriptor

### Formats (`formats/`)
Format-specific read/write handlers:
- `markdown_handler` - Markdown files
- `json_handler` - JSON files with optional schema validation
- `yaml_handler` - YAML files
- `text_handler` - Plain text files with encoding fallback
- `html_handler` - HTML files with tag stripping utility
- `xml_handler` - XML files with parse validation
- `csv_handler` - CSV files (read as list of dicts, write from list of dicts)
- `pdf_handler` - PDF files (requires pypdf or PyPDF2)

### Transformation (`transformation/`)
- `convert_document` - Convert between formats
- `merge_documents` - Merge multiple documents
- `split_document` - Split by sections, size, lines, or pages
- `format_document` - Format JSON/YAML with compact or pretty styles

### Search (`search/`)
- `InMemoryIndex` - In-memory inverted index for document search
- `index_document` / `create_index` - Index documents for search
- `search_documents` / `search_index` - Search with TF-based scoring
- `QueryBuilder` / `build_query` - Fluent query construction

### Metadata (`metadata/`)
- `extract_metadata` - Extract file system and format-specific metadata
- `update_metadata` - Update markdown frontmatter
- `get_document_version` / `set_document_version` - Version management

### Utils (`utils/`)
- `detect_encoding` - Encoding detection (uses chardet if available)
- `detect_format_from_path` / `detect_mime_type` - Format and MIME type detection
- `validate_file_path` / `check_file_size` - File validation

### Config (`config.py`)
- `DocumentsConfig` - Configuration (encoding, max file size, caching, validation)
- `get_config` / `set_config` - Global configuration management

## Supported Formats

| Format | Read | Write | Convert From | Convert To |
|--------|------|-------|-------------|------------|
| Markdown | Yes | Yes | Yes | Yes |
| JSON | Yes | Yes | Yes | Yes |
| YAML | Yes | Yes | Yes | Yes |
| Text | Yes | Yes | Yes | Yes |
| HTML | Yes | Yes | - | - |
| XML | Yes | Yes | - | - |
| CSV | Yes | Yes | - | - |
| PDF | Yes* | Yes* | - | - |

*Requires optional dependencies (pypdf, reportlab, or fpdf)

## Directory Contents

- `API_SPECIFICATION.md` - Detailed API documentation
- `__init__.py` - Module exports
- `config.py` - Configuration management
- `exceptions.py` - Exception classes
- `core/` - Core read/write/parse/validate operations
- `formats/` - Format-specific handlers
- `metadata/` - Metadata extraction and management
- `models/` - Data models
- `search/` - Search and indexing
- `transformation/` - Convert, merge, split, format
- `utils/` - Encoding detection, file validation

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k documents -v
```

## Navigation

- **Full Documentation**: [docs/modules/documents/](../../../docs/modules/documents/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
