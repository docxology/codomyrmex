# Documents Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Document parsing, extraction, and processing.

## Key Features

- **PDF** — PDF text extraction
- **DOCX** — Word document parsing
- **Chunking** — Split for RAG
- **Metadata** — Extract metadata

## Quick Start

```python
from codomyrmex.documents import DocumentParser

parser = DocumentParser()
doc = parser.parse("report.pdf")

print(f"Pages: {doc.page_count}")
print(doc.text[:500])
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/documents/](../../../src/codomyrmex/documents/)
- **Parent**: [Modules](../README.md)
