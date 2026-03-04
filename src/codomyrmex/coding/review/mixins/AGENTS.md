# Codomyrmex Agents -- src/codomyrmex/coding/review/mixins

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Nine mixin classes that compose into `CodeReviewer` to provide code quality analysis. Each mixin isolates one review concern: pyscn analysis, traditional linting, complexity patterns, dead code detection, code smell identification, architecture compliance, performance suggestions, quality dashboards, refactoring plans, and report formatting.

## Key Files

| File | Class | Role |
|------|-------|------|
| `pyscn.py` | `PyscnMixin` | Runs pyscn analyzer for complexity, dead code, duplication, and clone detection |
| `traditional.py` | `TraditionalMixin` | Orchestrates pylint, flake8, mypy, bandit, vulture via subprocess |
| `complexity.py` | `ComplexityMixin` | Analyzes complexity patterns, generates `ComplexityReductionSuggestion` items |
| `deadcode.py` | `DeadCodeMixin` | Enhances dead code findings with fix-availability metadata |
| `codesmells.py` | `CodeSmellsMixin` | Detects long methods, large classes, feature envy, data clumps |
| `architecture.py` | `ArchitectureMixin` | Checks layering violations, circular deps, naming conventions |
| `performance.py` | `PerformanceMixin` | Generates memory, CPU, I/O, and caching optimization suggestions |
| `metrics.py` | `MetricsMixin` | Computes `QualityDashboard` with scores, grades, and category breakdowns |
| `refactoring.py` | `RefactoringMixin` | Builds prioritized refactoring plans from complexity and dead code data |
| `reporting.py` | `ReportingMixin` | Produces HTML, JSON, or Markdown analysis reports |

## MCP Tools Available

No MCP tools are defined in this subpackage. MCP tools for coding review are defined in `coding/mcp_tools.py` (`code_review_file`, `code_review_project`, `code_debug`).

## Agent Instructions

1. All mixins expect `self.config`, `self.logger`, `self.pyscn_analyzer`, and `self.project_root` to be set by `CodeReviewer.__init__()` -- never instantiate mixins directly.
2. `TraditionalMixin` runs tools via `subprocess.run()`; tools not on PATH are silently skipped with a WARNING log.
3. `MetricsMixin.generate_quality_dashboard()` returns a `QualityDashboard` dataclass with `overall_score` in `[0.0, 100.0]`.
4. `ReportingMixin.generate_report()` accepts `format` parameter: `"html"`, `"json"`, or `"markdown"`.
5. All mixin methods catch exceptions internally and log errors rather than propagating, ensuring partial results are returned.

## Operating Contracts

- Mixins must not define `__init__`; shared state comes from `CodeReviewer.__init__()`.
- Each tool runner catches `subprocess.CalledProcessError` and logs at WARNING level; does not propagate.
- Zero-mock: subprocess calls execute real tools; tests require tools installed or use `@pytest.mark.skipif`.

## Common Patterns

```python
# All mixin methods are accessed through CodeReviewer
from codomyrmex.coding.review import CodeReviewer
reviewer = CodeReviewer("./src")

# ComplexityMixin
suggestions = reviewer.analyze_complexity_patterns()

# MetricsMixin
dashboard = reviewer.generate_quality_dashboard()

# ReportingMixin
reviewer.generate_report("/tmp/report.html", format="html")
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Primary Methods |
|-----------|-------------|-----------------|
| Engineer | Full | All mixin methods via CodeReviewer |
| QATester | Read | `generate_quality_dashboard()`, `generate_report()` |
| Architect | Read | `analyze_architecture_compliance()`, `generate_refactoring_plan()` |

## Navigation

- **Parent**: [review](../AGENTS.md)
- **Sibling**: [reviewer_impl](../reviewer_impl/AGENTS.md)
- **Root**: [codomyrmex](../../../../../../README.md)
