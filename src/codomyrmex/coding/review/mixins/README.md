# coding/review/mixins

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Nine mixin classes that provide code review analysis capabilities to `CodeReviewer` via Python MRO composition. Each mixin isolates a specific review concern: pyscn integration, traditional linter execution, complexity analysis, dead code detection, code smell identification, architecture compliance, performance optimization, quality metrics dashboards, refactoring plan generation, and report formatting.

## PAI Integration

| PAI Phase | Capability |
|-----------|-----------|
| VERIFY | `PyscnMixin` and `TraditionalMixin` run analysis tools; `ArchitectureMixin` checks layering |
| OBSERVE | `MetricsMixin` generates dashboards; `ReportingMixin` produces formatted reports |
| THINK | `ComplexityMixin` suggests simplifications; `RefactoringMixin` builds prioritized plans |

## Key Exports

All classes are defined in this package and consumed by `CodeReviewer`:

- **`PyscnMixin`** (`pyscn.py`) -- Runs pyscn-based analysis: complexity, dead code, duplication, clone detection
- **`TraditionalMixin`** (`traditional.py`) -- Orchestrates pylint, flake8, mypy, bandit, vulture via subprocess
- **`ComplexityMixin`** (`complexity.py`) -- Analyzes complexity patterns and generates reduction suggestions using `ComplexityReductionSuggestion`
- **`DeadCodeMixin`** (`deadcode.py`) -- Enhances dead code findings with auto-fix availability using `DeadCodeFinding`
- **`CodeSmellsMixin`** (`codesmells.py`) -- Detects long methods, large classes, feature envy, data clumps, primitive obsession
- **`ArchitectureMixin`** (`architecture.py`) -- Checks layering violations, circular dependencies, naming conventions using `ArchitectureViolation`
- **`PerformanceMixin`** (`performance.py`) -- Generates optimization suggestions for memory, CPU, I/O, and caching
- **`MetricsMixin`** (`metrics.py`) -- Computes `QualityDashboard` with overall score, grade, and category breakdowns
- **`RefactoringMixin`** (`refactoring.py`) -- Builds prioritized refactoring plans combining complexity, dead code, and architecture data
- **`ReportingMixin`** (`reporting.py`) -- Renders analysis results as HTML, JSON, or Markdown reports

## Quick Start

```python
# Mixins compose into CodeReviewer; not used standalone
from codomyrmex.coding.review import CodeReviewer

reviewer = CodeReviewer("./src")

# Complexity analysis (via ComplexityMixin)
suggestions = reviewer.analyze_complexity_patterns()

# Code smell detection (via CodeSmellsMixin)
smells = reviewer.detect_code_smells()

# Full refactoring plan (via RefactoringMixin)
plan = reviewer.generate_refactoring_plan()
```

## Architecture

```
mixins/
  __init__.py        -- Package marker
  pyscn.py           -- PyscnMixin (pyscn integration)
  traditional.py     -- TraditionalMixin (external linter subprocess calls)
  complexity.py      -- ComplexityMixin (complexity pattern analysis)
  deadcode.py        -- DeadCodeMixin (dead code enhancement)
  codesmells.py      -- CodeSmellsMixin (anti-pattern detection)
  architecture.py    -- ArchitectureMixin (layer compliance checking)
  performance.py     -- PerformanceMixin (optimization suggestions)
  metrics.py         -- MetricsMixin (quality dashboard generation)
  refactoring.py     -- RefactoringMixin (prioritized refactoring plans)
  reporting.py       -- ReportingMixin (multi-format report output)
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/coding/ -k "mixins or review" -v
```

## Navigation

- **Parent**: [review](../README.md)
- **Sibling**: [reviewer_impl](../reviewer_impl/README.md)
- **Root**: [codomyrmex](../../../../../../README.md)
