# Pattern Matching Module — Agent Coordination

## Purpose

Pattern Matching Module for Codomyrmex.

## Key Capabilities

- Pattern Matching operations and management

## Agent Usage Patterns

```python
from codomyrmex.pattern_matching import *

# Agent uses pattern matching capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/pattern_matching/](../../../src/codomyrmex/pattern_matching/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`PatternMatch`** — Represents a pattern match.
- **`AnalysisResult`** — Result of pattern analysis.
- **`PatternAnalyzer`** — Analyzes code for patterns.
- **`run_codomyrmex_analysis()`** — Run pattern analysis on a directory.
- **`get_embedding_function()`** — Get the embedding function used for analysis.
- **`analyze_repository_path()`** — Analyze a repository path.
- **`run_full_analysis()`** — Run full analysis sequence.
- **`print_once()`** — Print a message only once.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k pattern_matching -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
