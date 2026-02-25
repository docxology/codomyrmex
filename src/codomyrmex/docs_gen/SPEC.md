# docs_gen -- Specification

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `docs_gen` module provides AST-based Python documentation extraction, in-memory full-text search indexing with relevance scoring, and MkDocs-compatible static site configuration generation. It is a Service Layer module in the codomyrmex architecture with zero external runtime dependencies -- it relies exclusively on the Python standard library (`ast`, `re`, `collections`, `dataclasses`).

## Functional Requirements

### FR-1: API Documentation Extraction

The module must parse Python source code using `ast.parse()` and extract:

- Module-level docstrings (first `ast.Expr` containing a string constant).
- Module-level `__all__` export lists (from `ast.Assign` targeting `__all__`).
- Top-level class definitions including: name, docstring, base class names, and all method definitions.
- Top-level function and async function definitions including: name, parameter signature, docstring, decorator names, and async status.
- Class methods with the same attribute set as top-level functions.

### FR-2: Markdown Rendering

The module must render a `ModuleDoc` into Markdown format with:

- H1 header for the module name.
- H2 headers for each class and top-level function.
- H3 headers for each class method with signature.
- Docstrings rendered as body text below each header.

### FR-3: In-Memory Search Index

The module must provide an inverted index that:

- Tokenizes content into lowercase words of 2+ characters using `\w{2,}` regex.
- Maps tokens to document IDs for O(1) lookup per token.
- Supports adding documents with `doc_id`, `title`, `content`, `path`, and optional `tags`.
- Supports removing documents by `doc_id`, cleaning up all associated token mappings.
- Indexes tags as additional tokens for categorical search.

### FR-4: Relevance-Ranked Search

Search queries must return results ranked by:

- Base score: count of query tokens matching in the document's inverted index entries.
- Title bonus: 2x multiplier for each query token also found in the document title.
- Results sorted descending by total score.
- Configurable result limit (default: 10).

### FR-5: Snippet Extraction

Each search result must include a context snippet:

- Centered around the first matching token position in the document content.
- Maximum 200 characters in length.
- Prefixed with `"..."` if the snippet does not start at position 0.
- Suffixed with `"..."` if the snippet does not reach the end of the content.

### FR-6: Site Configuration Generation

The module must generate `SiteConfig` objects containing:

- Site title (configurable, default: `"Codomyrmex Documentation"`).
- Theme name (`"material"`).
- Plugin list (default: `["search", "mkdocstrings"]`).
- Navigation tree with a `"Home"` entry and an `"API Reference"` section containing one entry per added module.
- Base URL (default: `"/"`).

### FR-7: MkDocs YAML Output

`SiteGenerator.to_mkdocs_yaml()` must produce valid `mkdocs.yml` content including:

- `site_name`, `theme` block (with `name`, `palette.scheme`, `palette.primary`), `plugins` list, and `nav` structure.
- Theme palette uses `slate` scheme and `indigo` primary color.

## Interface Contract

### Public Exports (from `__init__.py`)

| Symbol | Type | Source File |
|--------|------|-------------|
| `APIDocExtractor` | Class | `api_doc_extractor.py` |
| `ModuleDoc` | Dataclass | `api_doc_extractor.py` |
| `ClassDoc` | Dataclass | `api_doc_extractor.py` |
| `FunctionDoc` | Dataclass | `api_doc_extractor.py` |
| `SearchIndex` | Class | `search_index.py` |
| `IndexEntry` | Dataclass | `search_index.py` |
| `SearchResult` | Dataclass | `search_index.py` |
| `SiteGenerator` | Class | `site_generator.py` |
| `SiteConfig` | Dataclass | `site_generator.py` |

### Key Method Signatures

```python
# api_doc_extractor.py
class APIDocExtractor:
    def extract_from_source(self, source: str, module_name: str = "") -> ModuleDoc: ...
    def to_markdown(self, doc: ModuleDoc) -> str: ...

# search_index.py
class SearchIndex:
    doc_count: int  # property
    def add(self, doc_id: str, title: str = "", content: str = "",
            path: str = "", tags: list[str] | None = None) -> None: ...
    def remove(self, doc_id: str) -> bool: ...
    def search(self, query: str, limit: int = 10) -> list[SearchResult]: ...

# site_generator.py
class SiteGenerator:
    module_count: int   # property
    page_count: int     # property
    search_index: SearchIndex  # property
    def __init__(self, title: str = "Codomyrmex Documentation") -> None: ...
    def add_module_source(self, source: str, module_name: str) -> ModuleDoc: ...
    def add_page(self, path: str, content: str, title: str = "") -> None: ...
    def generate_config(self) -> SiteConfig: ...
    def generate_pages(self) -> dict[str, str]: ...
    def to_mkdocs_yaml(self) -> str: ...
```

## Data Formats

### Input

- **Python source code**: Raw string containing syntactically valid Python. Passed to `APIDocExtractor.extract_from_source()`.
- **Markdown content**: Raw Markdown strings for custom pages via `SiteGenerator.add_page()`.
- **Search queries**: Plain text strings tokenized into lowercase words by `SearchIndex.search()`.

### Output

- **`ModuleDoc`**: `name: str`, `docstring: str`, `path: str`, `classes: list[ClassDoc]`, `functions: list[FunctionDoc]`, `exports: list[str]`.
- **`ClassDoc`**: `name: str`, `docstring: str`, `module: str`, `methods: list[FunctionDoc]`, `bases: list[str]`.
- **`FunctionDoc`**: `name: str`, `signature: str`, `docstring: str`, `module: str`, `decorators: list[str]`, `is_async: bool`.
- **`SearchResult`**: `doc_id: str`, `title: str`, `snippet: str`, `score: float`, `path: str`.
- **`IndexEntry`**: `doc_id: str`, `title: str`, `content: str`, `path: str`, `tags: list[str]`.
- **`SiteConfig`**: `title: str`, `theme: str`, `nav: list[dict[str, Any]]`, `plugins: list[str]`, `base_url: str`.
- **MkDocs YAML**: Plain text string suitable for writing to `mkdocs.yml`.

## Error Handling

| Condition | Error Type | Raised By |
|-----------|-----------|-----------|
| Invalid Python source (syntax error) | `SyntaxError` | `APIDocExtractor.extract_from_source()` via `ast.parse()` |
| Empty search query (no tokens after tokenization) | Returns empty list | `SearchIndex.search()` |
| Remove non-existent document | Returns `False` | `SearchIndex.remove()` |
| Source with no classes or functions | Returns `ModuleDoc` with empty lists | `APIDocExtractor.extract_from_source()` |
| Non-string AST node in `__all__` | Skipped silently | `APIDocExtractor.extract_from_source()` |

No custom exception classes are defined. The module propagates standard Python exceptions and uses return values to signal absence conditions.

## Performance Characteristics

- **Extraction**: O(n) in source code AST node count. Single-pass traversal of the syntax tree.
- **Indexing**: O(t) per document where t is the token count. Tokenization uses compiled regex.
- **Search**: O(q * d) where q is query token count and d is average documents per token. Practical performance is near-instant for indices under 10,000 documents.
- **Memory**: All state is in-memory. No disk I/O, no database connections, no network calls.
- **Snippet extraction**: O(t) per result where t is content length (single `str.find()` per query token).

## Dependencies

### Runtime Dependencies

- `ast` -- Python standard library (AST parsing)
- `re` -- Python standard library (tokenization regex)
- `collections.defaultdict` -- Python standard library (inverted index storage)
- `dataclasses` -- Python standard library (data model definitions)

### No External Dependencies

This module has zero third-party runtime dependencies. It does not require `pip install` of any package beyond the Python standard library.

## Security Considerations

- **`ast.parse()` is safe**: Unlike `eval()` or `exec()`, `ast.parse()` only parses source into a syntax tree without executing any code. No code execution occurs during documentation extraction.
- **No file system access**: The module does not read or write files. All input is provided as strings; all output is returned as data structures.
- **No network access**: No HTTP calls, no socket operations, no external service communication.
- **Input validation**: Only syntactically valid Python is accepted. Invalid input raises `SyntaxError` immediately.
- **No sensitive data handling**: The module processes source code structure (names, signatures, docstrings) but does not evaluate or execute any of the extracted code.

## Testing Requirements

Tests for `docs_gen` must follow the codomyrmex zero-mock policy:

- **No mocks**: Do not use `unittest.mock`, `MagicMock`, `monkeypatch`, or `pytest-mock`. All tests operate on real Python source strings and real index state.
- **Real source input**: Tests should use actual Python source code strings (inline or read from real module files) as input to `APIDocExtractor`.
- **Real index operations**: Tests should add, search, and remove from real `SearchIndex` instances -- never stub the index.
- **Skip guards**: Use `@pytest.mark.skipif` for any test that depends on optional external tooling (e.g., MkDocs being installed for YAML validation). Core extraction and indexing tests must never be skipped.
- **Assertions on structure**: Verify that extracted `ModuleDoc` objects contain the expected classes, functions, docstrings, and exports by name and count.
- **Search accuracy**: Verify that `SearchIndex.search()` returns expected documents with positive scores and non-empty snippets for known-good queries.
- **Round-trip verification**: Add a module source to `SiteGenerator`, then verify that `generate_config()` produces nav entries and `generate_pages()` produces non-empty Markdown content for the added module.

Run tests:

```bash
uv run pytest src/codomyrmex/tests/unit/docs_gen/ -v
```
