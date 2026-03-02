# Testing - Technical Specification

## Overview

Framework for validating, running, and benchmarking Codomyrmex skills. Provides three capabilities: test case execution with expected-value comparison, metadata validation, and performance measurement.

## Key Classes

### `SkillTestRunner` (__init__.py)

| Method | Parameters | Returns |
|--------|-----------|---------|
| `test_skill` | `skill`, `test_cases: list[dict]` | `list[SkillTestResult]` |
| `validate_skill` | `skill` | `dict` with `valid: bool`, `issues: list[str]`, `skill_name: str` |
| `benchmark_skill` | `skill`, `iterations: int = 100`, `**kwargs` | `dict` with timing stats |

**test_skill** test case dict format:
- `name`: Test case name (default: "unnamed")
- `inputs`: Dict of keyword arguments passed to `skill.execute(**inputs)`
- `expected`: Optional expected return value for equality check

**benchmark_skill** return dict:
- `skill`: Skill name
- `iterations`: Number of runs
- `errors`: Count of exceptions
- `total_time`, `avg_time`, `min_time`, `max_time`: Timing in seconds (via `time.monotonic()`)

### `SkillTestResult` (__init__.py)

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Test case name |
| `passed` | `bool` | Whether the test passed |
| `expected` | `Any \| None` | Expected value (if provided) |
| `actual` | `Any \| None` | Actual return value |
| `error` | `str \| None` | Error message on exception |

Method: `to_dict() -> dict[str, Any]` -- excludes None fields.

### Skill Interface (expected by SkillTestRunner)

| Attribute/Method | Required By |
|-----------------|-------------|
| `metadata.name` | `validate_skill`, `test_skill`, `benchmark_skill` (for logging) |
| `metadata.description` | `validate_skill` |
| `metadata.id` | `validate_skill` |
| `execute(**kwargs)` | `test_skill`, `benchmark_skill` |
| `validate_params()` | `validate_skill` |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config` (with fallback to stdlib logging)
- **External**: `time` (stdlib)

## Constraints

- All timing uses `time.monotonic()` for benchmark accuracy.
- Exception during `test_skill` execution is caught and recorded as a failed result with error message.
- Exception during `benchmark_skill` increments error count but does not halt the benchmark.
