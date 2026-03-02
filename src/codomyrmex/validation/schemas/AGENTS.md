# Schemas Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Shared dataclass and enum definitions used across Codomyrmex modules. Agents import these schemas as the canonical type system for results, tasks, configurations, code analysis findings, security findings, and infrastructure resources.

## Key Components

| Component | Source | Role |
|-----------|--------|------|
| `Result` | `core.py` | Universal operation result with status, data, errors, duration |
| `Task` | `core.py` | Task with id, name, status, dependencies |
| `Config` | `core.py` | Configuration container with name, values, metadata |
| `ModuleInfo` | `core.py` | Module metadata: name, version, status, dependencies |
| `ToolDefinition` | `core.py` | MCP tool schema: name, description, parameters |
| `AnalysisResult` | `code.py` | Static analysis finding with severity, rule, suggestion |
| `SecurityFinding` | `code.py` | Security issue with CWE ID, OWASP category, remediation |
| `TestResult` | `code.py` | Test outcome with name, status, duration, error |
| `CodeEntity` | `code.py` | Parsed code entity (function, class, variable) with location |
| `Deployment` | `infra.py` | Deployment record with status, environment, version |
| `Pipeline` | `infra.py` | CI/CD pipeline with stages and status |
| `Metric` | `infra.py` | Named metric value with type (counter, gauge, histogram) |

## Operating Contracts

- All types are `@dataclass` with type annotations; use `from_dict()` class methods where available.
- Status enums (`ResultStatus`, `TaskStatus`, `DeploymentStatus`, etc.) use uppercase string values.
- `Result.ok` property returns `True` when status is `SUCCESS`.
- `SecurityFinding.severity` uses `SecuritySeverity` enum (CRITICAL, HIGH, MEDIUM, LOW, INFO).
- `AnalysisResult.severity` uses `AnalysisSeverity` enum (ERROR, WARNING, INFO, HINT).
- These schemas have no runtime dependencies beyond stdlib; they are pure data definitions.

## Integration Points

- Consumed by `validation`, `coding/static_analysis`, `security`, `ci_cd_automation`, `deployment`.
- Parent module `validation` exposes `validate_schema` and `validate_config` MCP tools.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [validation](../README.md)
