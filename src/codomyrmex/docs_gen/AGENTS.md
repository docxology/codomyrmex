# docs_gen -- Agents

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `docs_gen` module provides agents with programmatic documentation extraction, full-text search indexing, and static site generation capabilities. Agents operating within the codomyrmex ecosystem use this module to introspect Python source code at the AST level, build searchable documentation indices, and generate MkDocs-compatible site configurations. This module does not expose MCP tools -- agents consume it as a direct Python library import.

## Active Components

| Component | Type | File | Status |
|-----------|------|------|--------|
| `APIDocExtractor` | Class | `api_doc_extractor.py` | Active -- AST-based source parser |
| `ModuleDoc` | Dataclass | `api_doc_extractor.py` | Active -- structured module documentation |
| `ClassDoc` | Dataclass | `api_doc_extractor.py` | Active -- structured class documentation |
| `FunctionDoc` | Dataclass | `api_doc_extractor.py` | Active -- structured function documentation |
| `SearchIndex` | Class | `search_index.py` | Active -- in-memory inverted index |
| `IndexEntry` | Dataclass | `search_index.py` | Active -- indexed document entry |
| `SearchResult` | Dataclass | `search_index.py` | Active -- search hit with score and snippet |
| `SiteGenerator` | Class | `site_generator.py` | Active -- site config orchestrator |
| `SiteConfig` | Dataclass | `site_generator.py` | Active -- MkDocs configuration model |

## Quick Verification

```bash
# Verify module imports successfully
uv run python -c "from codomyrmex.docs_gen import APIDocExtractor, SearchIndex, SiteGenerator; print('docs_gen: all core classes import OK')"

# Verify extraction works on live source
uv run python -c "
from codomyrmex.docs_gen import APIDocExtractor
import inspect, codomyrmex.docs_gen.search_index as mod
ext = APIDocExtractor()
doc = ext.extract_from_source(inspect.getsource(mod), 'search_index')
print(f'Extracted: {len(doc.classes)} classes, {len(doc.functions)} functions')
"

# Verify search index round-trip
uv run python -c "
from codomyrmex.docs_gen import SearchIndex
idx = SearchIndex()
idx.add('test', title='Test Doc', content='inverted index tokenization')
results = idx.search('tokenization')
print(f'Search: {len(results)} results, top score={results[0].score}')
"

# Verify site generation end-to-end
uv run python -c "
from codomyrmex.docs_gen import SiteGenerator
gen = SiteGenerator(title='Verify')
gen.add_module_source('def hello(): pass', 'verify_mod')
cfg = gen.generate_config()
print(f'Site: {len(cfg.nav)} nav items, {gen.page_count} pages, {gen.module_count} modules')
"
```

## Operating Contracts

1. **Python library only** -- This module has no MCP tools. Agents must import it directly via `from codomyrmex.docs_gen import ...`. Do not attempt MCP tool calls against this module.

2. **Source code input** -- `APIDocExtractor.extract_from_source()` requires raw Python source code as a string, not file paths or module objects. Agents must read source files before passing them to the extractor.

3. **No file system writes** -- Neither `SearchIndex` nor `SiteGenerator` write files to disk. They produce in-memory data structures (`SearchResult` lists, `SiteConfig` dataclasses, page content dicts). The agent or calling code is responsible for persisting output.

4. **Stateful index** -- `SearchIndex` maintains mutable internal state. Documents added via `add()` remain indexed until explicitly removed via `remove()`. Agents sharing an index instance across operations must account for accumulated state.

5. **AST parsing constraints** -- `APIDocExtractor` uses `ast.parse()` which requires syntactically valid Python. Agents must not pass partial code fragments, non-Python files, or source with syntax errors. Invalid input raises `SyntaxError`.

6. **Zero-mock testing** -- All tests for this module follow the codomyrmex zero-mock policy. No `unittest.mock`, `MagicMock`, or `monkeypatch`. Tests operate on real source code and real index state. Use `@pytest.mark.skipif` guards for any environment-specific dependencies.

## Integration Points

### Upstream Dependencies

- **Python standard library** (`ast`, `re`, `collections`, `dataclasses`) -- no external packages required.

### Downstream Consumers

- **CI/CD pipelines** -- `SiteGenerator.to_mkdocs_yaml()` produces configuration consumed by documentation build steps.
- **documentation module** (`src/codomyrmex/documentation/`) -- higher-level documentation maintenance orchestration may invoke `docs_gen` for extraction.
- **PAI BUILD phase** -- agents generating documentation for newly created modules use `APIDocExtractor` to verify public API surface completeness.
- **PAI OBSERVE phase** -- agents use `SearchIndex` to discover and search existing module capabilities before making changes.
- **PAI VERIFY phase** -- agents use `SearchIndex.search()` to confirm that new modules are indexed and discoverable.

### Data Flow

```
Python source (str) --> APIDocExtractor.extract_from_source()
    --> ModuleDoc (classes, functions, docstrings, exports)
        --> APIDocExtractor.to_markdown() --> Markdown (str)
        --> SiteGenerator.add_module_source() --> indexed + paged
            --> SiteGenerator.generate_config() --> SiteConfig
            --> SiteGenerator.to_mkdocs_yaml() --> mkdocs.yml content
            --> SiteGenerator.generate_pages() --> dict[path, markdown]

SearchIndex.add(doc_id, title, content, path, tags)
    --> SearchIndex.search(query, limit) --> list[SearchResult]
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, doc template design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, documentation quality validation | OBSERVED |

### Engineer Agent
**Use Cases**: Generate documentation via APIDocExtractor, build search indices, configure site generation during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Design documentation templates, validate extraction pipeline architecture, review search index strategy

### QATester Agent
**Use Cases**: Validate doc extraction accuracy, verify search index round-trip correctness, test site generation completeness

## Navigation

- **Module**: `src/codomyrmex/docs_gen/`
- **PAI integration**: [PAI.md](PAI.md)
- **Module overview**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **API specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Parent PAI map**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge document
