# Docs Gen Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `docs_gen` module provides Python-native tools for extracting API documentation from source code, building searchable documentation indices, and generating static site configuration. It operates on Python source strings using AST — no execution required.

## 2. Core Components

### 2.1 API Doc Extractor (`api_doc_extractor.py`)

**Data Classes**:

- **`FunctionDoc`**: `name`, `signature`, `docstring`, `module`, `decorators: list[str]`, `is_async: bool`
- **`ClassDoc`**: `name`, `docstring`, `module`, `methods: list[FunctionDoc]`, `bases: list[str]`
- **`ModuleDoc`**: `name`, `docstring`, `path`, `classes: list[ClassDoc]`, `functions: list[FunctionDoc]`, `exports: list[str]`

**`APIDocExtractor`** class:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `extract_from_source` | `(source: str, module_name="")` | `ModuleDoc` | Parse Python source via AST; extract classes, functions, docstrings, `__all__` |
| `to_markdown` | `(doc: ModuleDoc)` | `str` | Render a `ModuleDoc` as Markdown reference documentation |

### 2.2 Search Index (`search_index.py`)

**Data Classes**:

- **`IndexEntry`**: `doc_id`, `title`, `content`, `path`, `tags: list[str]`
- **`SearchResult`**: `doc_id`, `title`, `snippet`, `score: float`, `path`

**`SearchIndex`** class — in-memory inverted index with token-overlap scoring:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `add` | `(doc_id, title="", content="", path="", tags=None)` | `None` | Index a document; tokenizes title + content; title matches score 2x |
| `remove` | `(doc_id: str)` | `bool` | Remove a document from index; returns `True` if existed |
| `search` | `(query: str, limit=10)` | `list[SearchResult]` | Search index; returns results sorted by score descending |
| `doc_count` | property | `int` | Number of indexed documents |

### 2.3 Site Generator (`site_generator.py`)

**`SiteConfig`** (dataclass): `title`, `theme`, `nav: list[dict]`, `plugins: list[str]`, `base_url`

**`SiteGenerator`** class — orchestrates extraction, indexing, and site config:

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `(title="Codomyrmex Documentation")` | — | Initialize with title; creates `APIDocExtractor` and `SearchIndex` internally |
| `add_module_source` | `(source: str, module_name: str)` | `ModuleDoc` | Extract, index, and generate a Markdown page for a module |
| `add_page` | `(path, content, title="")` | `None` | Add a custom page to the site and search index |
| `generate_config` | `()` | `SiteConfig` | Build navigation structure from added modules |
| `generate_pages` | `()` | `dict[str, str]` | Return all generated `{path: markdown_content}` pages |
| `to_mkdocs_yaml` | `()` | `str` | Generate `mkdocs.yml` content string |
| `module_count` | property | `int` | Number of added modules |
| `page_count` | property | `int` | Number of generated pages |
| `search_index` | property | `SearchIndex` | Access the underlying search index |

## 3. Usage Example

```python
from codomyrmex.docs_gen import APIDocExtractor, SearchIndex, SiteGenerator

# Extract docs from source
extractor = APIDocExtractor()
source = open("src/codomyrmex/events/__init__.py").read()
doc = extractor.extract_from_source(source, "events")
print(extractor.to_markdown(doc))

# Search index
index = SearchIndex()
index.add("events", title="Events Module", content="publish subscribe event bus")
results = index.search("event bus", limit=5)
for r in results:
    print(f"[{r.score:.1f}] {r.title} — {r.snippet}")

# Generate full documentation site
gen = SiteGenerator(title="Codomyrmex Docs")
gen.add_module_source(source, "events")
gen.add_page("index.md", "# Welcome\nCodomyrmex documentation.", title="Home")
print(gen.to_mkdocs_yaml())
pages = gen.generate_pages()
```
