# Agent Guidelines - Documents

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Document processing: parsing, extraction, and transformation.

## Key Classes

- **DocumentParser** — Parse various formats
- **TextExtractor** — Extract text content
- **DocumentConverter** — Format conversion
- **ChunkSplitter** — Split into chunks

## Agent Instructions

1. **Detect format** — Auto-detect document type
2. **Extract metadata** — Title, author, date
3. **Chunk for LLM** — Split large documents
4. **Handle encoding** — UTF-8 by default
5. **Preserve structure** — Maintain headings

## Common Patterns

```python
from codomyrmex.documents import (
    DocumentParser, TextExtractor, ChunkSplitter
)

# Parse document
parser = DocumentParser()
doc = parser.parse("report.pdf")
print(f"Title: {doc.metadata.title}")
print(f"Pages: {doc.page_count}")

# Extract text
extractor = TextExtractor()
text = extractor.extract("document.docx")
text = extractor.extract_from_bytes(pdf_bytes, format="pdf")

# Split into chunks for RAG
splitter = ChunkSplitter(
    chunk_size=1000,
    overlap=100,
    separator="paragraph"
)
chunks = splitter.split(text)
for chunk in chunks:
    embed_and_store(chunk)

# Convert formats
from codomyrmex.documents import DocumentConverter
pdf = DocumentConverter.to_pdf("input.docx")
```

## Testing Patterns

```python
# Verify parsing
parser = DocumentParser()
doc = parser.parse_string("# Heading\n\nText", format="markdown")
assert doc.metadata is not None

# Verify chunking
splitter = ChunkSplitter(chunk_size=100)
chunks = splitter.split("A" * 300)
assert len(chunks) > 1
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Process and convert documents (PDF, DOCX, Markdown) during BUILD/EXECUTE phases; chunk documents for RAG pipelines; direct module instantiation

### Architect Agent
**Use Cases**: Document pipeline design review, format support analysis, chunking strategy evaluation

### QATester Agent
**Use Cases**: Unit and integration test execution, document parsing validation, format conversion verification

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
