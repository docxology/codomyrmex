# pattern_matching

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Code analysis and pattern recognition module that identifies structures, dependencies, and patterns within codebases. Built on the `cased/kit` toolkit, it provides repository indexing, dependency analysis, text search with context extraction, code summarization, docstring indexing, symbol extraction and usage analysis, and chunking utilities. The `get_embedding_function()` factory enables semantic search and similarity computations. All analysis functions operate on repository paths and return structured results.

## Key Exports

### Primary Functions

- **`get_embedding_function()`** -- Factory that returns an embedding function for semantic search and similarity
- **`analyze_repository_path()`** -- Analyze a repository at a given path, returning structural information
- **`run_full_analysis()`** -- Execute all analysis passes on a repository in sequence
- **`print_once()`** -- Utility to print a message only once (deduplicates repeated output)

### Analysis Functions

- **`_perform_repository_index()`** -- Index a repository for fast file and symbol lookup
- **`_perform_dependency_analysis()`** -- Analyze import/dependency relationships between modules
- **`_perform_text_search()`** -- Search repository contents for text patterns
- **`_perform_code_summarization()`** -- Generate natural-language summaries of code files
- **`_perform_docstring_indexing()`** -- Index all docstrings for searchable documentation
- **`_perform_symbol_extraction()`** -- Extract function, class, and variable definitions from source
- **`_perform_symbol_usage_analysis()`** -- Analyze where and how extracted symbols are used
- **`_perform_text_search_context_extraction()`** -- Extract surrounding context for text search matches
- **`_perform_chunking_examples()`** -- Demonstrate code chunking strategies for embedding pipelines

## Directory Contents

- `__init__.py` - Module entry point re-exporting all analysis functions
- `run_codomyrmex_analysis.py` - Core implementation of all analysis and embedding functions
- `requirements.txt` - Module-specific dependencies (cased/kit toolkit)

## Navigation

- **Full Documentation**: [docs/modules/pattern_matching/](../../../docs/modules/pattern_matching/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
