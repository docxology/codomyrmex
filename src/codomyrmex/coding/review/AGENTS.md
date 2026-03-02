# Codomyrmex Agents -- src/codomyrmex/coding/review

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Automated code review combining multi-tool static analysis (pylint, flake8, mypy, bandit, vulture), custom complexity analysis via `PyscnAnalyzer`, quality dashboards, and HTML/JSON/Markdown report generation. The `CodeReviewer` facade delegates to five mixins in `reviewer_impl/` for separation of concerns.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `reviewer.py` | `CodeReviewer` | Main facade; composes five mixins. Methods: `analyze_file()`, `analyze_project()`, `check_quality_gates()` |
| `reviewer.py` | `_load_config()` | Reads `.codereview.yaml` or falls back to defaults |
| `reviewer.py` | `_check_tools_availability()` | Probes for pylint, flake8, mypy, bandit, vulture executables |
| `analyzer.py` | `PyscnAnalyzer` | Structural analysis engine: `analyze_complexity()`, `detect_dead_code()`, `find_clones()`, `analyze_coupling()`, `generate_report()` |
| `models.py` | `AnalysisType` | Enum: LINT, TYPE_CHECK, SECURITY, COMPLEXITY, DEAD_CODE, ARCHITECTURE |
| `models.py` | `SeverityLevel` | Enum: ERROR, WARNING, INFO, HINT |
| `models.py` | `AnalysisResult` | Dataclass: file, type, severity, message, line, column, rule |
| `models.py` | `QualityDashboard` | Dataclass aggregating scores across categories |
| `models.py` | `QualityGateResult` | Dataclass: gate name, passed/failed, threshold, actual value |
| `models.py` | Exceptions | `CodeReviewError`, `PyscnError`, `ToolNotFoundError`, `ConfigurationError` |
| `api.py` | Convenience functions | `analyze_file()`, `analyze_project()`, `check_quality_gates()`, `generate_report()` |
| `__init__.py` | Package exports | Re-exports all public classes and convenience functions |

## Operating Contracts

- `CodeReviewer` requires at least one external tool available; raises `ToolNotFoundError` if none are found.
- `analyze_file()` returns `list[AnalysisResult]` sorted by severity descending.
- `check_quality_gates()` returns `list[QualityGateResult]`; callers check `.passed` on each.
- `PyscnAnalyzer.generate_report()` accepts format parameter: `"html"`, `"json"`, or `"markdown"`.
- Configuration loaded from `.codereview.yaml` in project root; missing config uses built-in defaults.
- Errors are logged via `logging_monitoring` before re-raising as typed exceptions.

## Integration Points

- **Depends on**: `logging_monitoring`, `reviewer_impl/` (five mixins), external tools (pylint, flake8, mypy, bandit, vulture)
- **Used by**: `coding` package exports, `coding.mcp_tools` (via `code_review_file`, `code_review_project`), CI quality gates

## Navigation

- **Child**: [reviewer_impl](reviewer_impl/)
- **Parent**: [coding](../README.md)
- **Sibling**: [pattern_matching](../pattern_matching/README.md), [static_analysis](../static_analysis/README.md), [parsers](../parsers/README.md)
- **Root**: [Root](../../../../../README.md)
