# Reviewer Implementation Mixins -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Five mixin classes that decompose `CodeReviewer` responsibilities. Each mixin is independently testable but designed to be composed together via Python's MRO into the `CodeReviewer` facade.

## Architecture

Mixin composition pattern. `CodeReviewer` inherits all five; method resolution order determines dispatch. Each mixin accesses shared state (`self.config`, `self.logger`) set by `CodeReviewer.__init__()`.

## Key Classes

### `LintToolsMixin` (lint_tools.py, ~303 lines)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `_run_pyscn_analysis` | `file_path: str` | `list[AnalysisResult]` | Run PyscnAnalyzer on a single file |
| `_run_traditional_analysis` | `file_path: str` | `list[AnalysisResult]` | Run all available external tools |
| `_run_pylint` | `file_path: str` | `list[AnalysisResult]` | pylint subprocess execution and output parsing |
| `_run_flake8` | `file_path: str` | `list[AnalysisResult]` | flake8 subprocess execution and output parsing |
| `_run_mypy` | `file_path: str` | `list[AnalysisResult]` | mypy subprocess execution and output parsing |
| `_run_bandit` | `file_path: str` | `list[AnalysisResult]` | bandit security analysis |
| `_run_vulture` | `file_path: str` | `list[AnalysisResult]` | vulture dead-code detection |

### `AnalysisPatternsMixin` (analysis.py, ~383 lines)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze_complexity_patterns` | `results: list[AnalysisResult]` | `list[ComplexityReductionSuggestion]` | Identify functions needing simplification |
| `analyze_dead_code_patterns` | `results: list[AnalysisResult]` | `list[DeadCodeFinding]` | Aggregate dead-code signals from multiple tools |
| `analyze_architecture_compliance` | `project_path: str` | `list[ArchitectureViolation]` | Check layer dependency rules |
| `generate_refactoring_plan` | `results: list[AnalysisResult]` | `list[dict]` | Prioritized refactoring suggestions |

### `PerformanceOptMixin` (performance.py, ~77 lines)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `optimize_performance` | `results: list[AnalysisResult]` | `list[str]` | Generate performance improvement suggestions |

### `DashboardMixin` (dashboard.py, ~940 lines)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate_quality_dashboard` | `results: list[AnalysisResult]` | `QualityDashboard` | Compute overall score, category breakdowns, code smells, tech debt hours |

### `ReportingMixin` (reporting.py, ~311 lines)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate_report` | `results, format: str` | `str` | Render results as HTML, JSON, or Markdown |
| `generate_comprehensive_report` | `results, dashboard` | `str` | Full report with dashboard, metrics, and recommendations |

## Dependencies

- **Internal**: `review.models` (all dataclasses and enums)
- **External**: pylint, flake8, mypy, bandit, vulture (via subprocess; optional)

## Constraints

- Mixins must not define `__init__`; shared state comes from `CodeReviewer.__init__()`.
- Each tool runner catches `subprocess.CalledProcessError` and logs; does not propagate.
- `DashboardMixin` is the largest mixin (~940 lines); scoring algorithms are internal and not individually overridable.
- Zero-mock: subprocess calls execute real tools; tests require tools installed or use `@pytest.mark.skipif`.

## Error Handling

- Individual tool failures (tool not on PATH, non-zero exit) are logged at WARNING level and return empty result lists.
- `AnalysisPatternsMixin` raises `CodeReviewError` if `project_path` does not exist.
- `ReportingMixin` raises `ValueError` for unsupported format strings.
