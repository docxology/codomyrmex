# Code Review -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Multi-tool code review system that aggregates results from external linters (pylint, flake8, mypy, bandit, vulture), custom structural analysis (`PyscnAnalyzer`), and quality-gate evaluation into unified reports. The `CodeReviewer` class uses a mixin architecture, delegating to five specialized mixins in `reviewer_impl/`.

## Architecture

```
CodeReviewer (facade)
  ├── LintToolsMixin        -- External tool execution (pylint, flake8, mypy, bandit, vulture)
  ├── AnalysisPatternsMixin -- Complexity, dead code, architecture compliance analysis
  ├── PerformanceOptMixin   -- Performance suggestion generation
  ├── DashboardMixin        -- Quality dashboard computation, code smell detection, tech debt scoring
  └── ReportingMixin        -- HTML, JSON, Markdown report generation
```

`PyscnAnalyzer` operates independently for structural analysis: cyclomatic complexity, dead-code detection, clone discovery, and coupling measurement.

## Key Classes

### `CodeReviewer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze_file` | `file_path: str` | `list[AnalysisResult]` | Run all enabled tools against a single file |
| `analyze_project` | `project_path: str` | `list[AnalysisResult]` | Recursive analysis of all supported files |
| `check_quality_gates` | `results: list[AnalysisResult]` | `list[QualityGateResult]` | Evaluate results against configured thresholds |

### `PyscnAnalyzer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze_complexity` | `source: str` | `list[ComplexityReductionSuggestion]` | Identify high-complexity functions |
| `detect_dead_code` | `project_path: str` | `list[DeadCodeFinding]` | Find unreachable or unused code |
| `find_clones` | `project_path: str` | `list[tuple]` | Detect near-duplicate code blocks |
| `analyze_coupling` | `project_path: str` | `dict` | Module coupling metrics |
| `generate_report` | `results, format: str` | `str` | Format results as html, json, or markdown |

## Data Types

| Type | Key Fields | Notes |
|------|-----------|-------|
| `AnalysisResult` | `file`, `analysis_type`, `severity`, `message`, `line`, `column`, `rule` | Core result unit |
| `AnalysisSummary` | `total`, `errors`, `warnings`, `info`, `by_type` | Aggregate counts |
| `CodeMetrics` | `loc`, `sloc`, `complexity`, `maintainability_index` | Per-file metrics |
| `QualityDashboard` | `overall_score`, `category_scores`, `code_smells`, `tech_debt_hours` | Dashboard aggregate |
| `QualityGateResult` | `gate_name`, `passed`, `threshold`, `actual` | Pass/fail per gate |
| `ComplexityReductionSuggestion` | `function_name`, `current_complexity`, `suggestion` | Refactoring advice |
| `DeadCodeFinding` | `file`, `line`, `code_type`, `name` | Unreachable code |
| `ArchitectureViolation` | `source_module`, `target_module`, `violation_type` | Layer/dependency violations |

## Enums

| Enum | Values |
|------|--------|
| `AnalysisType` | LINT, TYPE_CHECK, SECURITY, COMPLEXITY, DEAD_CODE, ARCHITECTURE |
| `SeverityLevel` | ERROR, WARNING, INFO, HINT |
| `Language` | PYTHON, JAVASCRIPT, TYPESCRIPT, JAVA, GO, RUST |

## Dependencies

- **Internal**: `logging_monitoring`, `reviewer_impl/` (five mixins)
- **External**: pylint, flake8, mypy, bandit, vulture (all optional; detected at runtime)

## Constraints

- At least one external tool must be installed; `_check_tools_availability()` raises `ToolNotFoundError` otherwise.
- Configuration via `.codereview.yaml`; schema validated at load time.
- Report generation is synchronous; large projects may take significant time.
- Zero-mock: real tool execution required; no fallback results.

## Error Handling

| Exception | When |
|-----------|------|
| `ToolNotFoundError` | No analysis tools found on PATH |
| `ConfigurationError` | Invalid `.codereview.yaml` schema |
| `CodeReviewError` | General review pipeline failure |
| `PyscnError` | `PyscnAnalyzer` internal failure |
