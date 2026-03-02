# Codomyrmex Agents -- src/codomyrmex/coding/static_analysis/complexity

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Python-native cyclomatic complexity calculation, line counting, and function-level metrics. Operates on Python source via the `ast` module without requiring external tools. Provides both standalone functions and a `ComplexityAnalyzer` class for batch analysis.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `ComplexityAnalyzer` | Batch analyzer: walks files, computes per-function and per-file metrics, returns `FileMetrics` |
| `__init__.py` | `calculate_cyclomatic_complexity` | Standalone function: counts decision points (if, elif, for, while, except, with, and, or, assert) in an AST node |
| `__init__.py` | `count_lines` | Standalone function: returns total lines, code lines, blank lines, comment lines for a source string |
| `__init__.py` | `ComplexityLevel` | Enum: LOW (1-5), MODERATE (6-10), HIGH (11-20), VERY_HIGH (21+) |
| `__init__.py` | `ComplexityMetric` | Dataclass: function name, complexity score, `ComplexityLevel`, line number |
| `__init__.py` | `FunctionMetrics` | Dataclass: function name, line count, complexity, parameter count, return count |
| `__init__.py` | `FileMetrics` | Dataclass: file path, total lines, code lines, blank lines, comment lines, list of `FunctionMetrics` |

## Operating Contracts

- `calculate_cyclomatic_complexity()` accepts an `ast.AST` node (typically `ast.FunctionDef` or `ast.AsyncFunctionDef`); returns `int >= 1`.
- `count_lines()` accepts a source string; returns a 4-tuple of `(total, code, blank, comment)`.
- `ComplexityAnalyzer` accepts a file path or directory; raises `FileNotFoundError` for invalid paths.
- `ComplexityLevel` thresholds are fixed: LOW 1-5, MODERATE 6-10, HIGH 11-20, VERY_HIGH 21+.
- All functions operate on Python source only; non-Python files raise `SyntaxError` during AST parsing.

## Integration Points

- **Depends on**: Python `ast` stdlib
- **Used by**: `static_analysis.StaticAnalyzer.calculate_metrics()`, `review.analyzer.PyscnAnalyzer.analyze_complexity()`

## Navigation

- **Parent**: [static_analysis](../README.md)
- **Sibling**: [linting](../linting/)
- **Root**: [Root](../../../../../../README.md)
