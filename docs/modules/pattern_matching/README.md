# Pattern Matching Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Advanced pattern matching with regex, glob, AST, and structural pattern support.


## Installation

```bash
pip install codomyrmex
```

## Key Features

- **PatternMatch** — Represents a pattern match.
- **AnalysisResult** — Result of pattern analysis.
- **PatternAnalyzer** — Analyzes code for patterns.
- `run_codomyrmex_analysis()` — Run pattern analysis on a directory.
- `get_embedding_function()` — Get the embedding function used for analysis.
- `analyze_repository_path()` — Analyze a repository path.
- `run_full_analysis()` — Run full analysis sequence.

## Quick Start

```python
from codomyrmex.pattern_matching import PatternMatch, AnalysisResult, PatternAnalyzer

instance = PatternMatch()
```

## Source Files

- `run_codomyrmex_analysis.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |
| `tutorials/` | Tutorials |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k pattern_matching -v
```

## Navigation

- **Source**: [src/codomyrmex/pattern_matching/](../../../src/codomyrmex/pattern_matching/)
- **Parent**: [Modules](../README.md)
