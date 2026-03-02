# Codomyrmex Agents -- src/codomyrmex/coding/static_analysis

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Multi-language static analysis orchestration. `StaticAnalyzer` dispatches to external tool runners (pylint, flake8, mypy, bandit, radon, vulture, safety, pyrefly for Python; eslint, tsc for JavaScript/TypeScript; spotbugs for Java), collects results into a unified `AnalysisResult` model, computes `CodeMetrics`, and exports to JSON or CSV. Exposes two MCP tools: `analyze_file` and `analyze_project`.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `static_analyzer.py` | `StaticAnalyzer` | Main orchestrator: `analyze_file()`, `analyze_project()`, `calculate_metrics()`, `export_results()` |
| `tool_runners.py` | `ToolRunner` | Subprocess wrappers for 11 external tools: pylint, flake8, mypy, bandit, radon, vulture, safety, pyrefly, eslint, tsc, spotbugs |
| `pyrefly_runner.py` | `PyreflyRunner` | Dedicated runner for Meta's Pyrefly type checker |
| `pyrefly_runner.py` | `PyreflyIssue`, `PyreflyResult` | Dataclasses for Pyrefly-specific output |
| `pyrefly_runner.py` | `run_pyrefly()`, `check_pyrefly_available()` | Convenience functions |
| `models.py` | `AnalysisType` | Enum: LINT, TYPE_CHECK, SECURITY, COMPLEXITY, DEAD_CODE, ARCHITECTURE |
| `models.py` | `SeverityLevel` | Enum: ERROR, WARNING, INFO, HINT |
| `models.py` | `AnalysisResult`, `AnalysisSummary`, `CodeMetrics` | Core data types for analysis output |
| `exceptions.py` | Exception hierarchy | `ParserError`, `LintError`, `TypeCheckError`, `ComplexityError`, `DependencyAnalysisError`, `SecurityVulnerabilityError`, `ASTError`, `MetricsError` |
| `__init__.py` | Package exports and `cli_commands()` | Re-exports public API; Click CLI group for static analysis |
| `complexity/` | `ComplexityAnalyzer` | Cyclomatic complexity, line counts, function-level metrics |
| `linting/` | `Linter`, `LintRule` | Pluggable rule-based linter with built-in rules |

## Operating Contracts

- `StaticAnalyzer.analyze_file()` auto-detects language from file extension and runs appropriate tool subset.
- `StaticAnalyzer.analyze_project()` walks directory recursively, skipping directories matching `.gitignore` patterns.
- `ToolRunner` methods return `list[AnalysisResult]`; missing tools return empty lists (logged at DEBUG).
- `export_results()` accepts `format` parameter: `"json"` or `"csv"`.
- `calculate_metrics()` returns a `CodeMetrics` dataclass with `loc`, `sloc`, `complexity`, `maintainability_index`.
- MCP tools `analyze_file` and `analyze_project` are decorated with `@mcp_tool()` in `static_analyzer.py`.
- Errors propagate as typed exceptions from `exceptions.py`.

## Integration Points

- **Depends on**: `logging_monitoring`, `complexity/`, `linting/`, external tools via subprocess
- **Used by**: `coding` package exports, `coding.mcp_tools`, CI quality pipelines, `review.reviewer_impl.LintToolsMixin`

## Navigation

- **Children**: [complexity](complexity/), [linting](linting/)
- **Parent**: [coding](../README.md)
- **Sibling**: [pattern_matching](../pattern_matching/README.md), [review](../review/README.md), [parsers](../parsers/README.md)
- **Root**: [Root](../../../../../README.md)
