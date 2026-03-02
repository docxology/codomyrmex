# Personal AI Infrastructure — Docs Gen Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Docs Gen module extracts API documentation from Python source code, builds
searchable in-memory indices, and generates static documentation site configuration.
It is the codomyrmex documentation pipeline — taking live Python source as input and
producing browsable, searchable documentation output.

Three components work together:

- **APIDocExtractor** — inspects modules and extracts docstrings, type signatures,
  class hierarchies, and metadata into structured `ModuleDoc`, `ClassDoc`, and
  `FunctionDoc` objects.
- **SearchIndex** — builds an in-memory inverted index over extracted documentation
  for fast full-text search across all module APIs.
- **SiteGenerator** — orchestrates extraction and indexing, then outputs `SiteConfig`
  for rendering with documentation site generators (MkDocs, etc.).

## PAI Capabilities

### Python API (no MCP tools — use direct Python import)

Docs Gen does not expose MCP tools. Use it as a Python library within BUILD or
EXECUTE phase scripts.

**Extract documentation from a module:**

```python
from codomyrmex.docs_gen import APIDocExtractor, ModuleDoc

extractor = APIDocExtractor()
doc: ModuleDoc = extractor.extract("codomyrmex.search")
# doc.functions: list[FunctionDoc] — all public functions with signatures
# doc.classes: list[ClassDoc] — all public classes with methods
# doc.docstring: str — module-level docstring
```

**Build a searchable index and query it:**

```python
from codomyrmex.docs_gen import SearchIndex, SearchResult

index = SearchIndex()
index.add(doc)  # Add one or more ModuleDoc objects
results: list[SearchResult] = index.search("full-text search")
for r in results:
    print(r.module, r.symbol, r.snippet)
```

**Generate a documentation site config:**

```python
from codomyrmex.docs_gen import SiteGenerator, SiteConfig

generator = SiteGenerator(modules=["codomyrmex.search", "codomyrmex.events"])
config: SiteConfig = generator.generate()
# config.nav: navigation tree
# config.pages: list of page definitions ready for MkDocs/mkdocs-material
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `APIDocExtractor` | Class | Extract structured docs from Python modules |
| `ModuleDoc` | Dataclass | Structured representation of a module's documentation |
| `ClassDoc` | Dataclass | Structured representation of a class and its methods |
| `FunctionDoc` | Dataclass | Structured representation of a function with signature |
| `SearchIndex` | Class | In-memory inverted index for doc search |
| `IndexEntry` | Dataclass | A single indexed documentation entry |
| `SearchResult` | Dataclass | A search hit with module, symbol, score, and snippet |
| `SiteGenerator` | Class | Orchestrate extraction + indexing + site config generation |
| `SiteConfig` | Dataclass | Navigation tree and page definitions for a doc site |

## PAI Algorithm Phase Mapping

| Phase | Docs Gen Contribution | Key Classes |
|-------|-----------------------|-------------|
| **OBSERVE** (1/7) | Extract API signatures to understand module capabilities before work | `APIDocExtractor`, `SearchIndex` |
| **BUILD** (4/7) | Generate documentation for newly built modules | `SiteGenerator`, `APIDocExtractor` |
| **VERIFY** (6/7) | Confirm documentation was extracted and indexed correctly | `SearchIndex.search()` |
| **LEARN** (7/7) | Generate updated site config after learning-driven module changes | `SiteGenerator` |

### Concrete PAI Usage Pattern

In a BUILD phase where a new module was created, generate and verify documentation:

```python
from codomyrmex.docs_gen import APIDocExtractor, SearchIndex

extractor = APIDocExtractor()
doc = extractor.extract("codomyrmex.new_module")
# Verify documentation is non-empty
assert doc.functions or doc.classes, "New module has no documented public API"

# Verify searchable
index = SearchIndex()
index.add(doc)
results = index.search("new_module")
assert results, "New module not discoverable in documentation index"
```

## Architecture Role

**Service Layer** — Documentation pipeline. Depends on Foundation Layer
(`logging_monitoring`). Consumed by the documentation site build process in CI/CD.
No runtime dependency from other codomyrmex modules — purely a tooling consumer.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.docs_gen import ...`
- CLI: `codomyrmex docs_gen <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
