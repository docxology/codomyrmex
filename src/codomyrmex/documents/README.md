# Documents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `documents` module is the information processing engine of Codomyrmex. It is responsible for the ingestion, parsing, transformation, and retrieval of documents across the system. Whether it's reading a PDF, converting Markdown to HTML, extracting metadata from source code, or indexing content for RAG (Retrieval-Augmented Generation), this module provides a robust pipeline for handling unstructured and structured text data.

## Key Features
- **Multi-Format Support**: The `formats` submodule handles parsing of Markdown, PDF, HTML, JSON, and source code files.
- **Transformation Pipeline**: The `transformation` submodule allows for document conversion, chunking, and summarization.
- **Metadata Extraction**: The `metadata` submodule automatically extracts tags, authors, and summaries from content.
- **Semantic Search**: The `search` submodule integrates with vector stores to enable semantic retrieval of document chunks.
- **Template Management**: The `templates` submodule manages standard document templates (like `SPEC.md`, `README.md`) for consistency.

## Quick Start

```python
from codomyrmex.documents.core import DocumentLoader
from codomyrmex.documents.transformation import TextChunker

# Load a markdown file
loader = DocumentLoader()
doc = loader.load("path/to/file.md")

# Extract metadata
print(f"Title: {doc.metadata.title}")

# Chunk for processing
chunker = TextChunker(chunk_size=1000)
chunks = chunker.split(doc)

print(f"Created {len(chunks)} chunks for processing.")
```

## Module Structure

- `core/`: Base classes for `Document`, `Loader`, and `Parser`.
- `formats/`: Format-specific parsers (e.g., `MarkdownParser`, `PDFParser`).
- `metadata/`: Logic for metadata extraction and validation.
- `search/`: Interfaces for vector databases and embedding generation.
- `transformation/`: Utilities for text processing, cleaning, and chunking.
- `templates/`: Jinja2 templates for generating project documentation.
- `utils/`: Helper functions for file I/O and encoding.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
