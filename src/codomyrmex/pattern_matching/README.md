# Pattern Matching Module

**Version**: v0.1.0 | **Status**: Active

Code pattern recognition and repository analysis using cased/kit.

## Quick Start

```python
from codomyrmex.pattern_matching import (
    run_full_analysis,
    analyze_repository_path,
    get_embedding_function
)

# Run full repository analysis
results = run_full_analysis("/path/to/repo")
print(f"Analyzed: {results['summary']}")

# Analyze specific path
analysis = analyze_repository_path("/path/to/repo/src")

# Get embedding function for custom analysis
embed = get_embedding_function()
embeddings = embed(["def foo():", "class Bar:"])
```

## Analysis Functions

| Function | Description |
|----------|-------------|
| `run_full_analysis(path)` | Full repository analysis |
| `analyze_repository_path(path)` | Analyze specific directory |
| `get_embedding_function()` | Get embeddings for code |
| `_perform_repository_index(path)` | Index repository structure |
| `_perform_dependency_analysis(path)` | Analyze dependencies |
| `_perform_text_search(path, query)` | Search code text |
| `_perform_code_summarization(path)` | Summarize code files |
| `_perform_docstring_indexing(path)` | Index docstrings |
| `_perform_symbol_extraction(path)` | Extract symbols |
| `_perform_symbol_usage_analysis(path)` | Analyze symbol usage |
| `_perform_chunking_examples(path)` | Generate code chunks |

## Prerequisites

- Requires `cased/kit` toolkit for code analysis
- Uses `logging_monitoring` for logging
- Uses `environment_setup` for dependency checks

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
