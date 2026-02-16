# Model Evaluation Module — Agent Coordination

## Purpose

Model Evaluation Module for Codomyrmex.

Provides tools for evaluating LLM model outputs including:
- Output scoring with composable scorer protocols
- Benchmark suite management for systematic evaluation
- Heuristic quality analysis across multiple dimensions

Integration:
- Uses `codomyrmex.schemas` for Result/ResultStatus types where available.
- No external LLM dependencies required; all scoring is heuristic-based.

Available scorers:
- ExactMatchScorer: Binary exact string match
- ContainsScorer: Substring containment check
- LengthScorer: Output length relative to target range
- RegexScorer: Regex pattern matching
- CompositeScorer: Weighted combination of multiple scorers

Benchmark management:
- BenchmarkCase: Individual test case definition
- BenchmarkSuite: Collection runner with scoring
- BenchmarkResult: Per-case evaluation result
- SuiteResult: Aggregated suite-level results

Quality analysis:
- QualityAnalyzer: Multi-dimension heuristic quality scorer
- QualityDimension: COHERENCE, RELEVANCE, COMPLETENESS, CONCISENESS, ACCURACY
- QualityReport: Structured quality assessment report

## Key Capabilities

- **`Scorer`** -- Abstract base class for output scorers.
- **`ExactMatchScorer`** -- Binary exact string match scorer.
- **`ContainsScorer`** -- Substring containment scorer.
- **`LengthScorer`** -- Output length relative to target range scorer.
- **`RegexScorer`** -- Regex pattern matching scorer.
- **`CompositeScorer`** -- Weighted combination of multiple scorers.
- **`WeightedScorer`** -- A scorer paired with a weight for composites.
- **`BenchmarkCase`** -- Individual benchmark test case definition.

## Agent Usage Patterns

```python
from codomyrmex.model_evaluation import ExactMatchScorer, ContainsScorer

# Exact match scoring
scorer = ExactMatchScorer(case_sensitive=False)
score = scorer.score("Hello World", "hello world")
print(score)  # 1.0

# Substring containment
contains = ContainsScorer()
score = contains.score("The answer is 42", "42")
print(score)  # 1.0
```

## Key Components

| Export | Type |
|--------|------|
| `Scorer` | Public API |
| `ExactMatchScorer` | Public API |
| `ContainsScorer` | Public API |
| `LengthScorer` | Public API |
| `RegexScorer` | Public API |
| `CompositeScorer` | Public API |
| `WeightedScorer` | Public API |
| `create_default_scorer` | Public API |
| `BenchmarkCase` | Public API |
| `BenchmarkResult` | Public API |
| `BenchmarkSuite` | Public API |
| `SuiteResult` | Public API |
| `QualityDimension` | Public API |
| `DimensionScore` | Public API |
| `QualityReport` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `benchmarks.py` | Benchmark suite management for model evaluation. |
| `quality.py` | Quality scoring for LLM outputs. |
| `scorers.py` | Output scoring functions for model evaluation. |

## Integration Points

- **Source**: [src/codomyrmex/model_evaluation/](../../../src/codomyrmex/model_evaluation/)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_evaluation -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
