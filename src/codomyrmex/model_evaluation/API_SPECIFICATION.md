# Model Evaluation API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `model_evaluation` module provides a composable scoring system, benchmark management, and heuristic quality analysis for evaluating LLM outputs. All scoring is deterministic and requires no external LLM calls.

## Scorers API

### Scorer (ABC)

Abstract base class for all output scorers.

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `name` | `@property -> str` | `str` | Human-readable scorer name |
| `score` | `(output: str, reference: str) -> float` | `float` | Score output against reference (0.0-1.0) |
| `score_batch` | `(pairs: list[tuple[str, str]]) -> list[float]` | `list[float]` | Score multiple pairs |

### ExactMatchScorer

Scores 1.0 on exact match, 0.0 otherwise.

```python
ExactMatchScorer(case_sensitive: bool = True, strip_whitespace: bool = True)
```

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `case_sensitive` | `bool` | `True` | Case-sensitive comparison |
| `strip_whitespace` | `bool` | `True` | Strip leading/trailing whitespace |

### ContainsScorer

Scores 1.0 if output contains reference as substring, 0.0 otherwise.

```python
ContainsScorer(case_sensitive: bool = False)
```

### LengthScorer

Scores based on output length relative to a target range. Returns 1.0 within range, linearly decays outside.

```python
LengthScorer(min_length: int = 1, max_length: int = 500)
```

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `min_length` | `int` | `1` | Minimum acceptable character count |
| `max_length` | `int` | `500` | Maximum acceptable character count |

**Raises:** `ValueError` if `min_length < 0` or `max_length < min_length`.

### RegexScorer

Scores 1.0 if output matches reference as a regex pattern, 0.0 otherwise.

```python
RegexScorer(flags: int = 0, full_match: bool = False)
```

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `flags` | `int` | `0` | Regex flags (e.g., `re.IGNORECASE`) |
| `full_match` | `bool` | `False` | If True, entire output must match pattern |

### WeightedScorer (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `scorer` | `Scorer` | (required) | The scorer instance |
| `weight` | `float` | `1.0` | Associated weight |

### CompositeScorer

Weighted average of multiple scorers.

```python
CompositeScorer(scorers: list[WeightedScorer] | None = None)
```

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `add_scorer` | `(scorer: Scorer, weight: float = 1.0) -> CompositeScorer` | `self` | Add a scorer with weight. Raises `ValueError` if weight <= 0 |
| `score` | `(output: str, reference: str) -> float` | `float` | Weighted average score |
| `score_detailed` | `(output: str, reference: str) -> dict` | `dict` | Score with per-scorer breakdown |
| `scorer_count` | `@property -> int` | `int` | Number of scorers |

### create_default_scorer

```python
def create_default_scorer() -> CompositeScorer
```

Returns a CompositeScorer with ExactMatchScorer (weight 2.0), ContainsScorer (weight 1.0), and LengthScorer (weight 0.5).

---

## Benchmarks API

### BenchmarkCase (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `input_text` | `str` | (required) | Input prompt for the model |
| `expected_output` | `str` | (required) | Expected/reference output |
| `id` | `str` | auto-generated | Unique case identifier |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |
| `tags` | `list[str]` | `[]` | Tags for filtering |

### BenchmarkResult (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `case_id` | `str` | (required) | Benchmark case ID |
| `score` | `float` | (required) | Score from scorer (0.0-1.0) |
| `duration_ms` | `float` | (required) | Execution time in milliseconds |
| `scorer_name` | `str` | (required) | Name of scorer used |
| `actual_output` | `str` | `""` | Actual model output |
| `metadata` | `dict[str, Any]` | `{}` | Additional metadata |

**Properties:**

| Property | Type | Description |
|:---------|:-----|:------------|
| `passed` | `bool` | True if score >= 0.5 |

### SuiteResult (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `suite_name` | `str` | (required) | Name of the suite |
| `results` | `list[BenchmarkResult]` | `[]` | Individual results |
| `total_duration_ms` | `float` | `0.0` | Total execution time |
| `metadata` | `dict[str, Any]` | `{}` | Additional metadata |

**Properties:**

| Property | Type | Description |
|:---------|:-----|:------------|
| `total_cases` | `int` | Total number of cases |
| `passed_cases` | `int` | Cases with score >= 0.5 |
| `failed_cases` | `int` | Cases with score < 0.5 |
| `average_score` | `float` | Mean score across all cases |
| `pass_rate` | `float` | Fraction of passed cases |

**Methods:**

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `get_result` | `(case_id: str) -> BenchmarkResult \| None` | `BenchmarkResult \| None` | Get result for specific case |
| `to_dict` | `() -> dict[str, Any]` | `dict` | Convert to plain dictionary |
| `to_result` | `() -> Result \| None` | `Result \| None` | Convert to codomyrmex Result |

### BenchmarkSuite

```python
BenchmarkSuite(name: str = "default", scorer: Scorer | None = None)
```

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `add_case` | `(input_text, expected_output, case_id, metadata, tags) -> BenchmarkCase` | `BenchmarkCase` | Add a case |
| `add_cases` | `(cases: list[BenchmarkCase]) -> None` | `None` | Add multiple cases |
| `remove_case` | `(case_id: str) -> bool` | `bool` | Remove case by ID |
| `get_cases_by_tag` | `(tag: str) -> list[BenchmarkCase]` | `list[BenchmarkCase]` | Filter by tag |
| `run` | `(model_fn, scorer=None) -> SuiteResult` | `SuiteResult` | Run all cases and score |
| `get_results` | `(model_fn, scorer=None) -> list[BenchmarkResult]` | `list[BenchmarkResult]` | Run and return results list |
| `clear` | `() -> None` | `None` | Remove all cases |

**Properties:** `name`, `cases`, `case_count`.

---

## Quality API

### QualityDimension (Enum)

| Value | Description |
|:------|:------------|
| `COHERENCE` | Sentence structure consistency and flow |
| `RELEVANCE` | Keyword overlap with context |
| `COMPLETENESS` | Presence of completion markers |
| `CONCISENESS` | Information density and unique word ratio |
| `ACCURACY` | Heuristic accuracy indicators |

### DimensionScore (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `dimension` | `QualityDimension` | (required) | The quality dimension |
| `score` | `float` | (required) | Score from 0.0 to 1.0 |
| `explanation` | `str` | `""` | Human-readable explanation |
| `raw_metrics` | `dict[str, Any]` | `{}` | Raw metrics that contributed to score |

### QualityReport (dataclass)

| Field | Type | Default | Description |
|:------|:-----|:--------|:------------|
| `scores` | `dict[QualityDimension, DimensionScore]` | `{}` | Per-dimension scores |
| `overall_score` | `float` | `0.0` | Weighted average |
| `output_text` | `str` | `""` | The analyzed output |
| `context_text` | `str` | `""` | The context provided |
| `metadata` | `dict[str, Any]` | `{}` | Additional metadata |

**Properties:**

| Property | Type | Description |
|:---------|:-----|:------------|
| `weakest_dimension` | `QualityDimension \| None` | Dimension with lowest score |
| `strongest_dimension` | `QualityDimension \| None` | Dimension with highest score |

**Methods:** `get_score(dimension)`, `get_explanation(dimension)`, `to_dict()`, `to_result()`.

### QualityAnalyzer

```python
QualityAnalyzer(dimension_weights: dict[QualityDimension, float] | None = None)
```

| Method | Signature | Returns | Description |
|:-------|:----------|:--------|:------------|
| `analyze` | `(output: str, context: str = "") -> QualityReport` | `QualityReport` | Analyze quality across all dimensions |

### analyze_quality

```python
def analyze_quality(output: str, context: str = "") -> QualityReport
```

Convenience function using default QualityAnalyzer settings.

## Error Handling

| Exception | Raised When |
|:----------|:------------|
| `ValueError` | `LengthScorer` with invalid min/max; `CompositeScorer.add_scorer` with non-positive weight |

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **Parent Directory**: [codomyrmex](../README.md)
