# Model Evaluation Module

**Version**: v0.1.0 | **Status**: Active

Tools for evaluating LLM model outputs including composable scorer protocols, benchmark suite management, and heuristic quality analysis across multiple dimensions. No external LLM dependencies required.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes

- **`Scorer`** -- Abstract base class for output scorers.
- **`ExactMatchScorer`** -- Binary exact string match scorer.
- **`ContainsScorer`** -- Substring containment scorer.
- **`LengthScorer`** -- Output length relative to target range scorer.
- **`RegexScorer`** -- Regex pattern matching scorer.
- **`CompositeScorer`** -- Weighted combination of multiple scorers.
- **`WeightedScorer`** -- A scorer paired with a weight for composites.
- **`BenchmarkCase`** -- Individual benchmark test case definition.
- **`BenchmarkResult`** -- Per-case evaluation result with `passed` property.
- **`BenchmarkSuite`** -- Collection runner that scores model outputs.
- **`SuiteResult`** -- Aggregated suite-level results with statistics.
- **`QualityDimension`** -- Enum: COHERENCE, RELEVANCE, COMPLETENESS, CONCISENESS, ACCURACY.
- **`DimensionScore`** -- Score for a single quality dimension.
- **`QualityReport`** -- Full quality report across all dimensions.
- **`QualityAnalyzer`** -- Heuristic-based multi-dimension quality scorer.

### Functions

- **`create_default_scorer()`** -- Create a default CompositeScorer with sensible weights.
- **`analyze_quality()`** -- Convenience function for quality analysis with defaults.

## Quick Start

### Score Model Output

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

### Composite Scoring

```python
from codomyrmex.model_evaluation import (
    CompositeScorer, WeightedScorer, ExactMatchScorer, ContainsScorer, LengthScorer
)

composite = CompositeScorer()
composite.add_scorer(ExactMatchScorer(case_sensitive=False), weight=2.0)
composite.add_scorer(ContainsScorer(), weight=1.0)
composite.add_scorer(LengthScorer(min_length=10, max_length=200), weight=0.5)

score = composite.score("The quick brown fox", "the quick brown fox")
print(f"Score: {score}")

# Detailed breakdown
details = composite.score_detailed("The quick brown fox", "the quick brown fox")
print(details)
```

### Run Benchmark Suite

```python
from codomyrmex.model_evaluation import BenchmarkSuite, ExactMatchScorer

suite = BenchmarkSuite(name="math-basics", scorer=ExactMatchScorer(case_sensitive=False))

suite.add_case(input_text="What is 2+2?", expected_output="4")
suite.add_case(input_text="What is 3*3?", expected_output="9")

def my_model(input_text: str) -> str:
    if "2+2" in input_text:
        return "4"
    return "unknown"

result = suite.run(my_model)
print(f"Pass rate: {result.pass_rate}")
print(f"Average score: {result.average_score}")
```

### Analyze Output Quality

```python
from codomyrmex.model_evaluation import analyze_quality

report = analyze_quality(
    output="Machine learning is a subset of AI that enables systems to learn from data. "
           "It encompasses supervised, unsupervised, and reinforcement learning approaches.",
    context="Explain machine learning concepts"
)

print(f"Overall: {report.overall_score:.2f}")
print(f"Strongest: {report.strongest_dimension}")
print(f"Weakest: {report.weakest_dimension}")

for dim, ds in report.scores.items():
    print(f"  {dim.value}: {ds.score:.2f} - {ds.explanation}")
```

## Directory Structure

- `scorers.py` -- Scorer ABC and implementations (Exact, Contains, Length, Regex, Composite)
- `benchmarks.py` -- BenchmarkCase, BenchmarkResult, SuiteResult, BenchmarkSuite
- `quality.py` -- QualityDimension, QualityAnalyzer, QualityReport, analyze_quality
- `__init__.py` -- Public API re-exports

## Exports

| Export | Type | Description |
| :--- | :--- | :--- |
| `Scorer` | ABC | Abstract base for all scorers |
| `ExactMatchScorer` | Class | Binary exact match (configurable case/whitespace) |
| `ContainsScorer` | Class | Substring containment check |
| `LengthScorer` | Class | Length within target range |
| `RegexScorer` | Class | Regex pattern matching |
| `CompositeScorer` | Class | Weighted combination of scorers |
| `WeightedScorer` | Dataclass | Scorer + weight pair |
| `create_default_scorer` | Function | Factory for default composite scorer |
| `BenchmarkCase` | Dataclass | Test case with input, expected output, tags |
| `BenchmarkResult` | Dataclass | Per-case result with score and passed property |
| `BenchmarkSuite` | Class | Collection runner with scoring |
| `SuiteResult` | Dataclass | Aggregated suite statistics |
| `QualityDimension` | Enum | COHERENCE, RELEVANCE, COMPLETENESS, CONCISENESS, ACCURACY |
| `DimensionScore` | Dataclass | Per-dimension score with explanation |
| `QualityReport` | Dataclass | Full multi-dimension quality report |
| `QualityAnalyzer` | Class | Heuristic quality scorer |
| `analyze_quality` | Function | Convenience quality analysis |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/model_evaluation/ -v
```

## Navigation

- [API_SPECIFICATION](API_SPECIFICATION.md) | [PAI](PAI.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
