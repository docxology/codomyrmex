# coding -- Technical Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unified module providing code execution, sandboxing, review, monitoring, and debugging. Organized into six submodules with two consolidated sub-packages (`pattern_matching`, `static_analysis`).

## Design Principles

- **Sandbox-first**: All code execution runs in isolated environments with resource limits.
- **Composable review**: Code review is decomposed into mixin classes for testability.
- **Multi-language**: Execution supports multiple languages via `SUPPORTED_LANGUAGES` registry.
- **Graceful degradation**: Missing external tools (pylint, bandit, etc.) are skipped with warnings.

## Architecture

```
coding/
  __init__.py          -- Package root (re-exports ~40 symbols)
  mcp_tools.py         -- 5 MCP tool definitions
  execution/           -- execute_code(), SUPPORTED_LANGUAGES, validation
  sandbox/             -- ExecutionLimits, Docker isolation, resource_limits_context
  review/              -- CodeReviewer, PyscnAnalyzer, models, analyzer
    mixins/            -- 9 analysis mixin classes
    reviewer_impl/     -- 5 CodeReviewer decomposition mixins
  monitoring/          -- ExecutionMonitor, MetricsCollector, ResourceMonitor
  debugging/           -- Debugger, ErrorAnalyzer, PatchGenerator, FixVerifier
  pattern_matching/    -- Code pattern recognition (consolidated)
  static_analysis/     -- Linting, security scanning (consolidated)
```

## Functional Requirements

### Execution
- `execute_code(language: str, code: str, timeout: int = 30) -> dict` -- Execute code in sandbox, return stdout/stderr/exit_code.
- `validate_language(language: str) -> bool` -- Check against `SUPPORTED_LANGUAGES`.

### Sandbox
- `run_code_in_docker(...)` -- Container-level isolation for untrusted code.
- `execute_with_limits(...)` -- Process-level resource limits (CPU, memory, time).
- `resource_limits_context(...)` -- Context manager for resource limiting.

### Review
- `CodeReviewer(project_root: str)` -- Main orchestrator composing 14 mixins.
- `analyze_file(path: str) -> AnalysisResult` -- Single-file analysis.
- `analyze_project(path: str) -> AnalysisSummary` -- Directory-wide analysis.
- `check_quality_gates() -> QualityGateResult` -- Threshold verification.
- `generate_report(format: str) -> str` -- HTML/JSON/Markdown output.

### Debugging
- `Debugger.debug(code, stdout, stderr, exit_code) -> dict` -- Error analysis and patch generation.

## Interface Contracts

All MCP tools return:
- Success: `{"status": "ok", ...}` with tool-specific result keys
- Failure: `{"status": "error", "error": "<message>"}`

Key data models from `review.models`:
- `AnalysisResult(file_path, line_number, column_number, severity, message, rule_id, category, suggestion)`
- `QualityDashboard(overall_score, grade, analysis_timestamp, ...)`
- `SeverityLevel`: INFO, WARNING, ERROR, CRITICAL

## Dependencies

- **Internal**: `logging_monitoring`, `validation.schemas`, `model_context_protocol.decorators`
- **External (optional)**: pylint, flake8, mypy, bandit, vulture (via subprocess)
- **External (optional)**: Docker (for container sandbox)

## Constraints

- Code execution timeout defaults to 30 seconds; configurable per call.
- `code_execute` is a destructive MCP tool requiring TRUSTED trust level.
- Review mixins do not define `__init__`; shared state set by `CodeReviewer`.
- The module version is `0.1.0` (internal), project version `1.0.8`.

## Navigation

- [Root](../../../../../../README.md)
