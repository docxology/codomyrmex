# Documents Tutorials

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tutorials for document parsing, extraction, and processing.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Parsing Documents](#parsing-documents) | Parse various document formats |
| [Text Extraction](#text-extraction) | Extract text from PDFs and DOCX |
| [Chunking for RAG](#chunking-for-rag) | Split documents for RAG pipelines |

## Parsing Documents

```python
from codomyrmex.documents import DocumentParser

parser = DocumentParser()
doc = parser.parse("report.pdf")

print(f"Title: {doc.metadata.title}")
print(f"Pages: {doc.page_count}")
print(doc.text[:500])
```

## Text Extraction

```python
from codomyrmex.documents import TextExtractor

extractor = TextExtractor()
text = extractor.extract("document.docx")

# Extract from bytes
text = extractor.extract_from_bytes(pdf_bytes, format="pdf")
```

## Chunking for RAG

```python
from codomyrmex.documents import ChunkSplitter

splitter = ChunkSplitter(chunk_size=1000, overlap=100)
chunks = splitter.split(document_text)

for chunk in chunks:
    embed_and_store(chunk)
```

## Navigation

- **Parent**: [Documents Documentation](../README.md)
- **Source**: [src/codomyrmex/documents/](../../../../src/codomyrmex/documents/)
