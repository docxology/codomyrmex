# Model Evaluation Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tools for evaluating LLM model outputs including composable scorer protocols, benchmark suite management, and heuristic quality analysis across multiple dimensions. No external LLM dependencies required; all scoring is heuristic-based.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Composable Scorers** -- ExactMatch, Contains, Length, Regex, and weighted Composite scorers.
- **Benchmark Suites** -- Systematic evaluation with case definitions and aggregated results.
- **Quality Analysis** -- Multi-dimension heuristic scoring: COHERENCE, RELEVANCE, COMPLETENESS, CONCISENESS, ACCURACY.

## Quick Start

```python
from codomyrmex.model_evaluation import ExactMatchScorer, CompositeScorer

# Simple exact match scoring
scorer = ExactMatchScorer(case_sensitive=False)
score = scorer.score("Hello World", "hello world")
print(score)  # 1.0

# Composite scoring with weights
composite = CompositeScorer()
composite.add_scorer(ExactMatchScorer(), weight=2.0)
composite.add_scorer(ContainsScorer(), weight=1.0)
result = composite.score("expected output", "expected output")
```

## API Reference

### Scorers

| Class | Description |
|-------|-------------|
| `Scorer` | Abstract base class for output scorers |
| `ExactMatchScorer` | Binary exact string match |
| `ContainsScorer` | Substring containment check |
| `LengthScorer` | Output length relative to target range |
| `RegexScorer` | Regex pattern matching |
| `CompositeScorer` | Weighted combination of multiple scorers |

### Benchmarks

| Class | Description |
|-------|-------------|
| `BenchmarkCase` | Individual test case definition |
| `BenchmarkSuite` | Collection runner with scoring |
| `BenchmarkResult` | Per-case evaluation result |
| `SuiteResult` | Aggregated suite-level results |

### Quality

| Class | Description |
|-------|-------------|
| `QualityAnalyzer` | Multi-dimension heuristic quality scorer |
| `QualityDimension` | Enum of quality dimensions |
| `QualityReport` | Structured quality assessment report |
| `analyze_quality()` | Convenience function for quality analysis |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_evaluation -v
```

## Related Modules

- [Prompt Engineering](../prompt_engineering/README.md)
- [Schemas](../schemas/README.md)

## Navigation

- **Source**: [src/codomyrmex/model_evaluation/](../../../src/codomyrmex/model_evaluation/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/model_evaluation/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/model_evaluation/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
