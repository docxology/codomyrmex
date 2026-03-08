# Documents Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

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
# Or for full document support:
uv sync --extra documents
```

## Key Exports

### Classes
- **`Document`** — Core document model with content and metadata.
- **`DocumentFormat`** — Enum for supported formats (MARKDOWN, JSON, YAML, CSV, etc.).
- **`DocumentMetadata`** — Container for document metadata.
- **`DocumentsConfig`** — Configuration for document operations.
- **`DocumentsError`** — Base exception class for all Documents module errors.

### Functions
- **`read_document(file_path)`** — Read a document with auto-detection.
- **`write_document(document, file_path)`** — Write a document to disk.
- **`convert_document(document, target_format)`** — Convert between formats.
- **`merge_documents(documents)`** — Merge multiple documents.
- **`split_document(document, criteria)`** — Split a document into chunks.

## Quick Start

```python
from codomyrmex.documents import (
    Document, DocumentFormat,
    read_document, write_document,
    convert_document, merge_documents, split_document,
)

# Read a document (auto-detects format and encoding)
doc = read_document("example.md")

# Create a document in-memory
doc = Document(content="# Hello World", format=DocumentFormat.MARKDOWN)
doc.metadata.title = "My Document"

# Write to file
write_document(doc, "output.md")

# Convert between formats
html_doc = convert_document(doc, DocumentFormat.HTML)

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
- `DocumentMetadata` - Metadata container with serialization and update support

### Formats (`formats/`)
Format-specific read/write handlers:
- `markdown_handler` - Markdown files
- `json_handler` - JSON files with optional schema validation
- `yaml_handler` - YAML files
- `text_handler` - Plain text files
- `html_handler` - HTML files with tag stripping utility
- `xml_handler` - XML files with parse validation
- `csv_handler` - CSV files (read/write as list of dicts)
- `pdf_handler` - PDF files (requires pypdf or PyPDF2)

### Transformation (`transformation/`)
- `convert_document` - Convert between formats (e.g., MD to HTML, JSON to YAML)
- `merge_documents` - Merge multiple documents into one
- `split_document` - Split by sections, size, lines, or CSV rows

### Search (`search/`)
- `InMemoryIndex` - In-memory inverted index for document search
- `index_document` / `create_index` - Index documents for search
- `search_documents` / `search_index` - Search with TF-based scoring

## Supported Formats

| Format | Read | Write | Convert From | Convert To |
|--------|------|-------|-------------|------------|
| Markdown | Yes | Yes | Yes | Yes |
| JSON | Yes | Yes | Yes | Yes |
| YAML | Yes | Yes | Yes | Yes |
| Text | Yes | Yes | Yes | Yes |
| HTML | Yes | Yes | Yes | Yes |
| XML | Yes | Yes | - | - |
| CSV | Yes | Yes | Yes | - |
| PDF | Yes* | Yes* | - | - |

*Requires optional dependencies (pypdf, reportlab, or fpdf)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/documents/ -v
```

## Orchestrator

The module includes a thin orchestrator for CLI operations:

```bash
# Run smoke tests
uv run python scripts/documents/orchestrate.py test

# Get document info
uv run python scripts/documents/orchestrate.py info -i sample.md

# Convert document
uv run python scripts/documents/orchestrate.py convert -i sample.md -o sample.html -f html
```
