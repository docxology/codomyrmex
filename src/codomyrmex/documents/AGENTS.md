# Agent Guidelines - Documents

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Document processing: reading, writing, parsing, extraction, and transformation. Unified interface for multiple formats (MD, JSON, YAML, HTML, CSV, PDF, XML).

## Key Classes & Functions

- **Document** — Core model holding content and `DocumentMetadata`.
- **read_document / DocumentReader** — Unified reading with auto-detection.
- **write_document / DocumentWriter** — Unified writing.
- **convert_document** — Format conversion (e.g., Markdown to HTML).
- **merge_documents / split_document** — Content manipulation.
- **InMemoryIndex** — Basic search capabilities.

## Agent Instructions

1. **Prefer read_document** — Let the module handle format and encoding detection.
2. **Metadata first** — Use `doc.metadata.update()` to manage document properties.
3. **Structured Content** — For CSV, JSON, and YAML, `doc.content` will be a native Python list or dict.
4. **Transformations** — Use `convert_document` before merging if formats differ.
5. **Zero-Mock Policy** — All tests must use real file I/O and functional implementations.

## Common Patterns

```python
from codomyrmex.documents import (
    read_document, convert_document, split_document, DocumentFormat
)

# Read and auto-detect
doc = read_document("data.csv")
print(f"Rows: {len(doc.content)}")

# Convert and Split
md_doc = read_document("report.md")
html_doc = convert_document(md_doc, DocumentFormat.HTML)
sections = split_document(md_doc, {"method": "by_sections"})

# Search
from codomyrmex.documents import create_index, index_document, search_documents
index = create_index()
index_document(md_doc, index)
matches = search_documents("target keyword", index)
```

## Testing Patterns

```python
# Use tmp_path fixture for zero-mock file tests
def test_io(tmp_path):
    f = tmp_path / "test.md"
    write_document(Document("# Title", DocumentFormat.MARKDOWN), f)
    assert read_document(f).metadata.title == "Title"
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
