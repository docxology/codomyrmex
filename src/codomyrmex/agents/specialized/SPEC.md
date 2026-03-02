# Specialized — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Autonomous code improvement pipeline and iterative review loop for detecting anti-patterns, proposing fixes with confidence-gated approval, generating regression tests, and converging on code quality through repeated generate-test-review cycles.

## Architecture

Two independent but complementary workflows:

1. **Improvement Pipeline**: `AntiPatternDetector` -> fix generator -> test generator -> review verdict. Configurable via `ImprovementConfig` safety limits.
2. **Review Loop**: `CodeGenerator` -> `TestGenerator` -> quality scoring -> re-generate if below threshold. Converges when review score >= approval_threshold.

## Key Classes

### `ImprovementPipeline`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze` | `source: str`, `file_path: str` | `list[AntiPattern]` | Detect anti-patterns in source code |
| `improve` | `source: str`, `file_path: str` | `ImprovementReport` | Full pipeline: detect -> fix -> test -> review |

### `AntiPatternDetector`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze` | `source: str`, `file_path: str` | `list[AntiPattern]` | Regex scan for known anti-patterns with severity filtering |

### `ImprovementReport`

| Method/Property | Returns | Description |
|----------------|---------|-------------|
| `to_markdown()` | `str` | Render as markdown with diffs, anti-patterns, test results |
| `approved` | `bool` | True if verdict is APPROVE |
| `change_count` | `int` | Number of proposed changes |

### `ReviewLoop`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `spec: str` | `ReviewLoopResult` | Generate-test-review until convergence or max_iterations |

### `ImprovementConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_changes_per_run` | `int` | 10 | Maximum proposed changes per pipeline run |
| `min_confidence` | `float` | 0.7 | Minimum confidence to accept a change |
| `severity_threshold` | `float` | 0.3 | Minimum anti-pattern severity to address |
| `auto_apply` | `bool` | False | Apply fixes without human review |
| `max_file_size_kb` | `int` | 500 | Skip files larger than this |
| `exclude_patterns` | `list[str]` | `["test_*", "*_test.py"]` | File patterns to exclude |

## Built-in Anti-Patterns

| Name | Regex | Severity | Fix Template |
|------|-------|----------|-------------|
| `bare_except` | `except\s*:` | 0.7 | Typed exception clause |
| `mutable_default` | `def\s+\w+\([^)]*=\s*\[\]` | 0.8 | `=None` |
| `star_import` | `from\s+\S+\s+import\s+\*` | 0.5 | None (manual fix) |
| `print_debug` | `^\s*print\s*\(` | 0.3 | None (manual fix) |
| `todo_fixme` | `#\s*(TODO\|FIXME\|HACK\|XXX)` | 0.2 | None (manual fix) |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.coding.generator`, `codomyrmex.coding.test_generator`
- **External**: Standard library only (`re`, `time`, `dataclasses`, `enum`)

## Constraints

- Changes are capped at `max_changes_per_run` per pipeline invocation.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.
- Default fix generator returns `None` for patterns without a `fix_template`.

## Error Handling

- `ImprovementPipeline.improve()` does not propagate exceptions from fix or test generators; instead returns empty results.
- `ReviewLoop._review()` catches `SyntaxError` during `compile()` and records it as an issue rather than failing the loop.
