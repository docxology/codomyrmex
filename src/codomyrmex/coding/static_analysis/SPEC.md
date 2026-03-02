# Static Analysis -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Multi-language static analysis framework that orchestrates 11 external tools across Python, JavaScript/TypeScript, and Java ecosystems. Provides a unified result model, metrics computation, and export capabilities.

## Architecture

Layered delegation pattern:

1. **StaticAnalyzer** (facade) -- receives file or project path, detects language, selects tool subset, aggregates results.
2. **ToolRunner** -- subprocess wrappers for each external tool; parses tool-specific output into `AnalysisResult`.
3. **PyreflyRunner** -- specialized runner for Meta's Pyrefly type checker with its own result dataclasses.
4. **ComplexityAnalyzer** (subpackage) -- Python-native cyclomatic complexity calculation.
5. **Linter** (subpackage) -- pluggable rule-based linter for custom lint rules.

## Key Classes

### `StaticAnalyzer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze_file` | `file_path: str, tools: list[str] = None` | `list[AnalysisResult]` | Run selected tools on file; MCP tool |
| `analyze_project` | `project_path: str, tools: list[str] = None` | `list[AnalysisResult]` | Recursive directory analysis; MCP tool |
| `calculate_metrics` | `file_path: str` | `CodeMetrics` | LOC, SLOC, complexity, maintainability index |
| `export_results` | `results: list[AnalysisResult], format: str, output_path: str` | `None` | Write results as JSON or CSV |

### `ToolRunner`

| Method | Tool | Language |
|--------|------|----------|
| `run_pylint` | pylint | Python |
| `run_flake8` | flake8 | Python |
| `run_mypy` | mypy | Python |
| `run_bandit` | bandit | Python |
| `run_radon` | radon | Python |
| `run_vulture` | vulture | Python |
| `run_safety` | safety | Python (deps) |
| `run_pyrefly` | pyrefly | Python |
| `run_eslint` | eslint | JavaScript/TypeScript |
| `run_tsc` | tsc | TypeScript |
| `run_spotbugs` | spotbugs | Java |

All methods: `(file_path: str) -> list[AnalysisResult]`. Missing tools return empty list.

### `PyreflyRunner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `file_path: str` | `PyreflyResult` | Execute pyrefly and parse output |
| `check_pyrefly_available` | _(none)_ | `bool` | Check if pyrefly is on PATH |

## Data Types

| Type | Fields | Notes |
|------|--------|-------|
| `AnalysisResult` | `file`, `analysis_type`, `severity`, `message`, `line`, `column`, `rule` | Unified result from any tool |
| `AnalysisSummary` | `total`, `errors`, `warnings`, `info`, `by_type` | Aggregate statistics |
| `CodeMetrics` | `loc`, `sloc`, `complexity`, `maintainability_index` | Per-file metrics |
| `PyreflyIssue` | `file`, `line`, `column`, `message`, `severity` | Pyrefly-specific finding |
| `PyreflyResult` | `issues`, `summary`, `success` | Pyrefly execution result |

## Enums

| Enum | Values |
|------|--------|
| `AnalysisType` | LINT, TYPE_CHECK, SECURITY, COMPLEXITY, DEAD_CODE, ARCHITECTURE |
| `SeverityLevel` | ERROR, WARNING, INFO, HINT |
| `Language` | PYTHON, JAVASCRIPT, TYPESCRIPT, JAVA, GO, RUST |

## Dependencies

- **Internal**: `logging_monitoring`, `complexity/`, `linting/`
- **External**: pylint, flake8, mypy, bandit, radon, vulture, safety, pyrefly, eslint, tsc, spotbugs (all optional; detected at runtime)

## Constraints

- Language detection is extension-based (`.py`, `.js`, `.ts`, `.java`); ambiguous files default to Python.
- `ToolRunner` methods catch `subprocess.CalledProcessError` and `FileNotFoundError`; missing tools are silently skipped.
- `export_results()` raises `ValueError` for unsupported format strings.
- Zero-mock: real tool execution required; tests use `@pytest.mark.skipif` for absent tools.

## Error Handling

| Exception | When |
|-----------|------|
| `ParserError` | Source file cannot be parsed |
| `LintError` | Linter execution failure |
| `TypeCheckError` | Type checker failure |
| `ComplexityError` | Complexity calculation failure |
| `SecurityVulnerabilityError` | Security scanner failure |
| `ASTError` | AST traversal failure |
| `MetricsError` | Metrics computation failure |
| `DependencyAnalysisError` | Dependency graph failure |
