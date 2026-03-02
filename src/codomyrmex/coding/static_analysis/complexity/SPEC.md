# Complexity Analysis -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pure-Python cyclomatic complexity engine using the `ast` module. Counts decision points per function and aggregates metrics at the file level. No external dependencies.

## Architecture

Single-module design in `__init__.py` (~267 lines). Three layers:

1. **Primitives** -- `calculate_cyclomatic_complexity()` and `count_lines()` operate on individual AST nodes or source strings.
2. **Data model** -- `ComplexityLevel` enum, `ComplexityMetric`, `FunctionMetrics`, `FileMetrics` dataclasses.
3. **Orchestrator** -- `ComplexityAnalyzer` walks files and aggregates function-level metrics into `FileMetrics`.

## Key Functions

### `calculate_cyclomatic_complexity`

| Parameter | Type | Description |
|-----------|------|-------------|
| `node` | `ast.AST` | AST node to measure (typically function or class) |
| **Returns** | `int` | Complexity score >= 1 |

Decision points counted: `If`, `IfExp`, `For`, `AsyncFor`, `While`, `ExceptHandler`, `With`, `AsyncWith`, `Assert`, `BoolOp` (each `and`/`or` adds 1).

### `count_lines`

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | `str` | Python source code string |
| **Returns** | `tuple[int, int, int, int]` | (total, code, blank, comment) |

### `ComplexityAnalyzer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze_file` | `file_path: str` | `FileMetrics` | Parse file and compute all metrics |
| `analyze_directory` | `dir_path: str` | `list[FileMetrics]` | Recursive analysis of `.py` files |
| `get_high_complexity` | `metrics: list[FileMetrics], threshold: int = 10` | `list[FunctionMetrics]` | Filter functions above threshold |

## Data Types

| Type | Fields | Notes |
|------|--------|-------|
| `ComplexityLevel` | LOW, MODERATE, HIGH, VERY_HIGH | Enum with integer range boundaries |
| `ComplexityMetric` | `name`, `complexity`, `level`, `line` | Single function measurement |
| `FunctionMetrics` | `name`, `lines`, `complexity`, `params`, `returns` | Extended function metrics |
| `FileMetrics` | `path`, `total_lines`, `code_lines`, `blank_lines`, `comment_lines`, `functions: list[FunctionMetrics]` | Per-file aggregate |

## Dependencies

- **Internal**: None
- **External**: Python `ast` stdlib only

## Constraints

- Python source only; `SyntaxError` raised for non-Python or syntactically invalid files.
- Complexity baseline is 1 (a function with no branches has complexity 1).
- `ComplexityLevel` thresholds are not configurable; they follow McCabe's standard ranges.
- Zero-mock: real AST parsing from real source files required.
