# Model Evaluation — Functional Specification

**Module**: `codomyrmex.model_evaluation`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

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

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `benchmarks.py` | Benchmark suite management for model evaluation. |
| `quality.py` | Quality scoring for LLM outputs. |
| `scorers.py` | Output scoring functions for model evaluation. |

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Scorer`
- `ExactMatchScorer`
- `ContainsScorer`
- `LengthScorer`
- `RegexScorer`
- `CompositeScorer`
- `WeightedScorer`
- `create_default_scorer`
- `BenchmarkCase`
- `BenchmarkResult`
- `BenchmarkSuite`
- `SuiteResult`
- `QualityDimension`
- `DimensionScore`
- `QualityReport`
- `QualityAnalyzer`
- `analyze_quality`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_evaluation -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Docs](../../../docs/modules/model_evaluation/)
