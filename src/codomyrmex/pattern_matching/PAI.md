# Personal AI Infrastructure — Pattern Matching Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Pattern Matching module identifies patterns and structures within codebases using the `cased/kit` toolkit. It provides repository indexing, dependency analysis, text search, code summarization, docstring indexing, symbol extraction, and chunking capabilities. This is a **Core Layer** module that supports the PAI OBSERVE and THINK phases with code understanding capabilities.

## PAI Capabilities

### Full Repository Analysis

Run comprehensive analysis across an entire repository:

```python
from codomyrmex.pattern_matching import run_full_analysis, analyze_repository_path

# Determine the repository root
repo_path = analyze_repository_path(".")

# Run all analysis passes
run_full_analysis(repo_path)
```

### Individual Analysis Functions

Each analysis capability can be invoked independently:

```python
from codomyrmex.pattern_matching import (
    _perform_repository_index,          # Index repository file structure
    _perform_dependency_analysis,       # Analyze module dependencies
    _perform_text_search,               # Search for text patterns
    _perform_code_summarization,        # Summarize code blocks
    _perform_docstring_indexing,        # Index all docstrings
    _perform_symbol_extraction,         # Extract symbols (classes, functions, variables)
    _perform_symbol_usage_analysis,     # Analyze where symbols are used
    _perform_text_search_context_extraction,  # Search with surrounding context
    _perform_chunking_examples,         # Chunk code for embedding/analysis
)
```

### Embedding Support

Generate embeddings for code analysis:

```python
from codomyrmex.pattern_matching import get_embedding_function

embed_fn = get_embedding_function()
# Returns a function compatible with cased/kit's embedding interface
```

### CLI Commands

```bash
codomyrmex pattern_matching patterns  # List known code pattern types
codomyrmex pattern_matching scan      # Scan current directory for patterns
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `run_full_analysis(path)` | Function | Run all 9 analysis passes on a repository |
| `analyze_repository_path(path)` | Function | Determine and validate repository root path |
| `get_embedding_function()` | Function | Get embedding function for code vectorization |
| `print_once(msg)` | Function | Utility to print a message only once (deduplication) |

### Analysis Passes (9 Total)

| Pass | Function | What It Does |
|------|----------|-------------|
| Repository Index | `_perform_repository_index` | Map file structure and module layout |
| Dependency Analysis | `_perform_dependency_analysis` | Trace import chains and module dependencies |
| Text Search | `_perform_text_search` | Find text patterns across the codebase |
| Code Summarization | `_perform_code_summarization` | Generate summaries of code blocks |
| Docstring Indexing | `_perform_docstring_indexing` | Extract and index all docstrings |
| Symbol Extraction | `_perform_symbol_extraction` | Find all classes, functions, variables |
| Symbol Usage | `_perform_symbol_usage_analysis` | Track where symbols are used |
| Context Search | `_perform_text_search_context_extraction` | Search with surrounding context lines |
| Chunking | `_perform_chunking_examples` | Split code into chunks for embedding/LLM processing |

## PAI Algorithm Phase Mapping

| Phase | Pattern Matching Contribution |
|-------|------------------------------|
| **OBSERVE** | `_perform_repository_index`, `_perform_symbol_extraction` — understand codebase structure |
| **THINK** | `_perform_dependency_analysis`, `_perform_symbol_usage_analysis` — reason about code relationships |
| **PLAN** | `_perform_code_summarization` — summarize modules to inform planning decisions |
| **VERIFY** | `_perform_text_search` — search for patterns that should or shouldn't exist |

## Architecture Role

**Core Layer** — Depends on `logging_monitoring` and `environment_setup` (Foundation). Relies on the `cased/kit` toolkit for code analysis. Used by reasoning modules (`cerebrum`, `graph_rag`) and agent modules for code understanding.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
