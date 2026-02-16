# Schemas — Functional Specification

**Module**: `codomyrmex.schemas`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Shared Schema Registry for Codomyrmex

Provides standardized types used across modules to enable interoperability.
This is the Foundation layer type library that replaces per-module type definitions.

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `code.py` | Code-related shared types for Codomyrmex. |
| `core.py` | Core shared types for Codomyrmex. |
| `infra.py` | Infrastructure shared types for Codomyrmex. |

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Result`
- `ResultStatus`
- `Task`
- `TaskStatus`
- `Config`
- `ModuleInfo`
- `ToolDefinition`
- `Notification`
- `CodeEntity`
- `CodeEntityType`
- `AnalysisResult`
- `AnalysisSeverity`
- `SecurityFinding`
- `SecuritySeverity`
- `TestResult`
- `TestStatus`
- `Deployment`
- `DeploymentStatus`
- `Pipeline`
- `PipelineStatus`
- `Resource`
- `BuildArtifact`
- `Metric`
- `MetricType`
- `Credential`
- `Permission`
- `WorkflowStep`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k schemas -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Docs](../../../docs/modules/schemas/)
