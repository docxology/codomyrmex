# Personal AI Infrastructure — Documents Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Documents module provides PAI integration for document parsing and processing.

## PAI Capabilities

### Document Parsing

Parse documents:

```python
from codomyrmex.documents import DocumentParser

parser = DocumentParser()
doc = parser.parse("report.pdf")

print(f"Pages: {doc.page_count}")
print(doc.text[:500])
```

### Text Chunking

Chunk for RAG:

```python
from codomyrmex.documents import TextChunker

chunker = TextChunker(chunk_size=500)
chunks = chunker.chunk(doc.text)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `DocumentParser` | Parse documents |
| `TextChunker` | Chunk for RAG |
| `Metadata` | Extract metadata |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
