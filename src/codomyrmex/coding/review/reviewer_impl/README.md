# coding/review/reviewer_impl

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Five mixin classes that decompose `CodeReviewer` responsibilities into independently testable concerns. Each mixin is designed for Python MRO composition into the `CodeReviewer` facade defined in `review/reviewer.py`. The mixins cover external linter orchestration, structural pattern analysis, performance optimization suggestions, quality dashboards, and multi-format report generation.

## PAI Integration

| PAI Phase | Capability |
|-----------|-----------|
| VERIFY | Lint analysis via `LintToolsMixin`, architecture compliance via `AnalysisPatternsMixin` |
| OBSERVE | Quality dashboards via `DashboardMixin`, comprehensive reports via `ReportingMixin` |
| THINK | Refactoring plans via `AnalysisPatternsMixin.generate_refactoring_plan()` |

## Key Exports

Re-exported from `__init__.py`:

- **`LintToolsMixin`** -- Runs external linters (pylint, flake8, mypy, bandit, vulture) via subprocess
- **`AnalysisPatternsMixin`** -- Structural analysis: complexity patterns, dead code patterns, architecture compliance, refactoring plans
- **`PerformanceOptMixin`** -- Performance optimization suggestions for memory, CPU, I/O, and caching
- **`DashboardMixin`** -- Quality dashboard generation with overall scoring, category breakdowns, and tech debt estimation
- **`ReportingMixin`** -- Multi-format report output (HTML, JSON, Markdown) with comprehensive dashboard reports

## Quick Start

```python
# Mixins are not used standalone -- they compose into CodeReviewer
from codomyrmex.coding.review import CodeReviewer

reviewer = CodeReviewer("./src")
# All mixin methods are available on the reviewer instance:
dashboard = reviewer.generate_quality_dashboard()
print(f"Score: {dashboard.overall_score}, Grade: {dashboard.grade}")
```

## Architecture

```
reviewer_impl/
  __init__.py        -- Re-exports all five mixin classes
  lint_tools.py      -- LintToolsMixin (~303 lines)
  analysis.py        -- AnalysisPatternsMixin (~383 lines)
  performance.py     -- PerformanceOptMixin (~77 lines)
  dashboard.py       -- DashboardMixin (~940 lines)
  reporting.py       -- ReportingMixin (~311 lines)
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/coding/ -k "reviewer" -v
```

## Navigation

- **Parent**: [review](../README.md)
- **Sibling**: [mixins](../mixins/README.md)
- **Root**: [codomyrmex](../../../../../../README.md)
