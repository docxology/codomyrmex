# Technical Specification - Schemas

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.validation.schemas`\
**Last Updated**: 2026-01-29

## 1. Purpose

Shared Foundation-layer type library: plain dataclasses and enums (results, tasks,
code-analysis records, infrastructure records) that modules exchange instead of
defining per-module equivalents.

## 2. Architecture

### 2.1 Components

```text
schemas/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
├── core.py              # Result, Task, Config, ModuleInfo, ToolDefinition, Notification
├── code.py              # CodeEntity, AnalysisResult, SecurityFinding, TestResult
└── infra.py             # Deployment, Pipeline, Resource, BuildArtifact, Metric, ...
```

### 2.2 Dependencies

- Python 3.10+ standard library only (`dataclasses`, `enum`, `typing`)
- Parent module: `validation`

## 3. Interfaces

### 3.1 Public API

```python
# Core types (core.py)
from codomyrmex.validation.schemas import (
    Config, ModuleInfo, Notification, Result, ResultStatus, Task, TaskStatus, ToolDefinition,
)

# Code types (code.py)
from codomyrmex.validation.schemas import (
    AnalysisResult, AnalysisSeverity, CodeEntity, CodeEntityType,
    SecurityFinding, SecuritySeverity, TestResult, TestStatus,
)

# Infrastructure types (infra.py)
from codomyrmex.validation.schemas import (
    BuildArtifact, Credential, Deployment, DeploymentStatus, Metric, MetricType,
    Permission, Pipeline, PipelineStatus, Resource, WorkflowStep,
)

ok = Result.success(data={"files": 3})
failed = Result.failure("lint failed", errors=["E501 line too long"])
assert ok.ok and not failed.ok
assert Result.from_dict(ok.to_dict()).status is ResultStatus.SUCCESS
```

### 3.2 Configuration

None. The types hold data only and read no environment variables.

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Plain data types**: Every type is a `dataclass` or `Enum` with `to_dict()` (and, where needed, `from_dict()`) helpers and no third-party dependencies, so any layer can import it without creating upward dependencies.

### 4.2 Limitations

- No runtime validation: field types and value ranges are not enforced, and there is no constraint or JSON Schema model.
- No schema versioning or migration; callers must manage changes to these types.

## 5. Testing

```bash
# Run tests for this module
uv run pytest tests/unit/schemas/test_schemas.py tests/unit/validation/test_infra_schemas.py tests/unit/validation/test_hypothesis_schemas.py
```

## 6. Future Considerations

- JSON Schema draft 7/2020-12 support: derive standard JSON Schema from these dataclasses, enabling interoperability with external validators and schema registries.
- Schema versioning and migration: track schema version history and provide migration helpers that transform data conforming to an older schema version into the current schema, reducing manual upgrade work.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
