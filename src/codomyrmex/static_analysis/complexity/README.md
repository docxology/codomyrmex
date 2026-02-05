# complexity

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Code complexity analysis using AST-based cyclomatic and cognitive complexity metrics. Provides `ComplexityAnalyzer` for file-level and function-level analysis, including line counting, parameter counting, nesting depth tracking, and automatic severity classification.

## Key Exports

- **`ComplexityAnalyzer`** — Main analyzer with `analyze_file(path)` returning `FileMetrics` and `analyze_function(code)` returning `FunctionMetrics`. Configurable complexity and LOC thresholds. `get_high_complexity_functions()` filters by threshold.
- **`calculate_cyclomatic_complexity(code)`** — Calculates cyclomatic complexity via AST visitor (counts if/for/while/except/with/assert/comprehension/bool-op branches)
- **`calculate_cognitive_complexity(code)`** — Calculates cognitive complexity with nesting-depth bonus for control structures
- **`count_lines(code)`** — Returns dict with `total`, `code`, `comments`, `blank` line counts
- **`ComplexityLevel`** — Enum: `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`
- **`ComplexityMetric`** — Dataclass with name, value, level, and configurable thresholds. Factory method `from_value()` auto-classifies.
- **`FunctionMetrics`** — Per-function metrics: cyclomatic/cognitive complexity, LOC, parameter count, nesting depth. Property `overall_complexity` returns `ComplexityLevel`.
- **`FileMetrics`** — Per-file metrics: line counts, function/class counts, list of `FunctionMetrics`. Properties `average_complexity` and `max_complexity`.

## Navigation

- **Parent Module**: [static_analysis](../README.md)
- **Parent Directory**: [codomyrmex](../../README.md)
