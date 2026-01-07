# pattern_matching

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Code analysis through AST parsing, pattern recognition, and embedding generation for semantic search and similarity. Provides multi-step pipeline (Parse -> Recognize -> Embed -> Analyze) with configurable patterns for code smells and other patterns. Utilizes the `cased/kit` toolkit for code analysis and pattern recognition.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `docs/` – Subdirectory
- `requirements.txt` – File
- `run_codomyrmex_analysis.py` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.pattern_matching import (
    analyze_repository_path,
    run_full_analysis,
    get_embedding_function,
)

# Analyze repository
results = analyze_repository_path("src/")
print(f"Patterns found: {len(results.patterns)}")
print(f"Dependencies: {len(results.dependencies)}")

# Run full analysis
analysis = run_full_analysis(
    repo_path="src/",
    include_dependencies=True,
    include_text_search=True
)
print(f"Analysis complete: {analysis.summary}")

# Get embedding function for semantic search
embed_fn = get_embedding_function()
embedding = embed_fn("function to calculate fibonacci")
print(f"Embedding dimension: {len(embedding)}")
```

