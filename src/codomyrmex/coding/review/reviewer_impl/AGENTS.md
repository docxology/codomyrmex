# Codomyrmex Agents -- src/codomyrmex/coding/review/reviewer_impl

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Five mixin classes that compose into `CodeReviewer`. Each mixin isolates a specific review concern: external tool execution, structural analysis, performance suggestions, quality dashboards, and report formatting.

## Key Components

| File | Class | Role |
|------|-------|------|
| `lint_tools.py` | `LintToolsMixin` | Runs external linters via subprocess: `_run_pyscn_analysis()`, `_run_traditional_analysis()`, plus individual runners for pylint, flake8, mypy, bandit, vulture |
| `analysis.py` | `AnalysisPatternsMixin` | Structural pattern analysis: `analyze_complexity_patterns()`, `analyze_dead_code_patterns()`, `analyze_architecture_compliance()`, `generate_refactoring_plan()` |
| `performance.py` | `PerformanceOptMixin` | Performance optimization suggestions: `optimize_performance()` with generators for common inefficiency patterns |
| `dashboard.py` | `DashboardMixin` | Quality dashboard generation: `generate_quality_dashboard()` computing overall scores, code smell detection, and technical debt estimation (~940 lines) |
| `reporting.py` | `ReportingMixin` | Multi-format report output: `generate_report()` (HTML/JSON/Markdown), `generate_comprehensive_report()`, dashboard HTML generation |
| `__init__.py` | _(re-exports)_ | Re-exports all five mixins for `CodeReviewer` composition |

## Operating Contracts

- All mixins expect to be mixed into a class that has `self.config` (dict from `.codereview.yaml`) and `self.logger`.
- `LintToolsMixin` runs tools via `subprocess.run()`; tools not on PATH are silently skipped per-analysis.
- `DashboardMixin.generate_quality_dashboard()` returns a `QualityDashboard` dataclass with `overall_score` in `[0.0, 100.0]`.
- `ReportingMixin.generate_report()` accepts `format` parameter: `"html"`, `"json"`, or `"markdown"`.
- `AnalysisPatternsMixin.generate_refactoring_plan()` returns a prioritized list of refactoring suggestions based on complexity and coupling metrics.
- Errors from individual tool runners are caught and logged; a single tool failure does not abort the overall analysis.

## Integration Points

- **Depends on**: `review.models` (dataclasses, enums, exceptions), `logging_monitoring`, external tools via subprocess
- **Used by**: `review.reviewer.CodeReviewer` (sole consumer; mixins are not used standalone)

## Navigation

- **Parent**: [review](../README.md)
- **Root**: [Root](../../../../../../README.md)
