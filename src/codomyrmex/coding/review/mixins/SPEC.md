# Review Mixins -- Technical Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Nine mixin classes that decompose `CodeReviewer` responsibilities into independently testable concerns. Each mixin accesses shared state (`self.config`, `self.logger`, `self.pyscn_analyzer`, `self.project_root`) set by `CodeReviewer.__init__()`.

## Design Principles

- **Single Responsibility**: Each mixin owns exactly one analysis domain.
- **Composition over Inheritance**: Mixins compose via Python MRO into `CodeReviewer`.
- **Graceful Degradation**: Tool failures are logged at WARNING level and return empty results rather than propagating exceptions.
- **Zero-Mock**: Tests execute real tools; missing tools trigger `@pytest.mark.skipif`.

## Architecture

```
mixins/
  pyscn.py           -- PyscnMixin: pyscn analyzer integration
  traditional.py     -- TraditionalMixin: subprocess-based linter execution
  complexity.py      -- ComplexityMixin: cyclomatic complexity analysis
  deadcode.py        -- DeadCodeMixin: dead code pattern enhancement
  codesmells.py      -- CodeSmellsMixin: anti-pattern detection
  architecture.py    -- ArchitectureMixin: layer violation checking
  performance.py     -- PerformanceMixin: optimization suggestion generation
  metrics.py         -- MetricsMixin: quality dashboard computation
  refactoring.py     -- RefactoringMixin: prioritized refactoring plans
  reporting.py       -- ReportingMixin: HTML/JSON/Markdown report generation
```

## Functional Requirements

### PyscnMixin

- `_run_pyscn_analysis(file_path: str) -> list[AnalysisResult]` -- Run pyscn complexity, dead code, duplication, and clone detection on a Python file. Skips non-Python files and returns empty list when pyscn is disabled.

### TraditionalMixin

- `_run_traditional_analysis(file_path: str, analysis_types: list[str]) -> list[AnalysisResult]` -- Route to individual tool runners based on `analysis_types` (quality, style, security). Each runner parses tool output into `AnalysisResult` items.
- Tool runners: `_run_pylint`, `_run_flake8`, `_run_mypy`, `_run_bandit`, `_run_vulture`

### ComplexityMixin

- `analyze_complexity_patterns() -> list[ComplexityReductionSuggestion]` -- Identify functions exceeding `config["max_complexity"]` and generate extract-method or strategy-pattern suggestions.

### DeadCodeMixin

- `analyze_dead_code_patterns() -> list[DeadCodeFinding]` -- Enhance raw pyscn dead code data with auto-fix availability and specific removal suggestions.

### CodeSmellsMixin

- `detect_code_smells() -> list[dict]` -- Detect long methods, large classes, feature envy, data clumps, and primitive obsession patterns.

### ArchitectureMixin

- `analyze_architecture_compliance() -> list[ArchitectureViolation]` -- Check layering violations, circular dependencies, and naming convention adherence.

### PerformanceMixin

- `optimize_performance() -> dict[str, Any]` -- Generate categorized optimization suggestions for memory, CPU, I/O, and caching opportunities.

### MetricsMixin

- `generate_quality_dashboard() -> QualityDashboard` -- Compute overall score, grade, category scores (complexity, maintainability, testability, reliability, security, performance), top issues, and priority actions.

### RefactoringMixin

- `generate_refactoring_plan() -> dict[str, Any]` -- Aggregate complexity reductions, dead code removals, architecture improvements, and priority actions into a structured plan with effort estimates.

### ReportingMixin

- `generate_report(output_path: str, format: str) -> bool` -- Render results as HTML, JSON, or Markdown to `output_path`. Returns `True` on success.

## Interface Contracts

All mixins import models from `codomyrmex.coding.review.models`:
- `AnalysisResult`, `AnalysisSummary`, `AnalysisType`, `SeverityLevel`, `Language`
- `QualityDashboard`, `ArchitectureViolation`, `ComplexityReductionSuggestion`, `DeadCodeFinding`

All mixins use `codomyrmex.logging_monitoring.core.logger_config.get_logger` for logging.

Optional `codomyrmex.performance.monitor_performance` decorator applied where available.

## Dependencies

- **Internal**: `coding.review.models` (all dataclasses and enums), `logging_monitoring`
- **External (optional)**: pylint, flake8, mypy, bandit, vulture (via subprocess)
- **External (optional)**: `codomyrmex.performance` for `@monitor_performance` decorator

## Constraints

- Mixins must not define `__init__`.
- `CodeSmellsMixin` complexity threshold is hardcoded at 20.
- `MetricsMixin` is the largest mixin at ~600 lines; scoring algorithms are internal.
- `ReportingMixin` returns `False` for unsupported format strings.

## Navigation

- **Parent**: [review](../SPEC.md)
- **Root**: [codomyrmex](../../../../../../README.md)
