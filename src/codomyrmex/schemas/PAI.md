# Personal AI Infrastructure -- Schemas Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Schemas module is the **shared type foundation** for the entire codomyrmex ecosystem. Every other module depends on it for standardized data types, ensuring consistent data exchange across all layers. It provides 27 exports (8 enums, 19 dataclasses) organized into three submodules: core, code, and infrastructure.

## PAI Capabilities

### Standardized Type System

Every codomyrmex module uses schemas types for cross-module communication:

```python
from codomyrmex.schemas import Result, ResultStatus, Task, TaskStatus

# Standard operation result
result = Result(
    status=ResultStatus.SUCCESS,
    data={"analyzed": 42},
    message="Complete",
)

if result.ok:
    payload = result.to_dict()  # JSON-serializable dict
```

### Cross-Module Interoperability

All modules share the same type definitions, preventing drift and incompatible interfaces:

```python
from codomyrmex.schemas import (
    AnalysisResult, AnalysisSeverity,  # static_analysis, coding
    Deployment, DeploymentStatus,      # deployment, containerization
    Metric, MetricType,                # metrics, telemetry
)
```

## Key Exports

| Export | Kind | Submodule | Purpose |
|--------|------|-----------|---------|
| `Result` | Dataclass | core | Standard operation result envelope |
| `ResultStatus` | Enum | core | SUCCESS, FAILURE, PARTIAL, SKIPPED, TIMEOUT |
| `Task` | Dataclass | core | Work item for orchestration |
| `TaskStatus` | Enum | core | PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED |
| `Config` | Dataclass | core | Module configuration with get/set |
| `ModuleInfo` | Dataclass | core | Module metadata descriptor |
| `ToolDefinition` | Dataclass | core | MCP/CLI tool definition |
| `Notification` | Dataclass | core | Standard notification |
| `CodeEntity` | Dataclass | code | Code entity representation |
| `CodeEntityType` | Enum | code | FILE, CLASS, FUNCTION, METHOD, etc. |
| `AnalysisResult` | Dataclass | code | Static analysis finding |
| `AnalysisSeverity` | Enum | code | INFO, LOW, MEDIUM, HIGH, CRITICAL |
| `SecurityFinding` | Dataclass | code | Security vulnerability |
| `SecuritySeverity` | Enum | code | LOW, MEDIUM, HIGH, CRITICAL |
| `TestResult` | Dataclass | code | Test execution result |
| `TestStatus` | Enum | code | PASSED, FAILED, SKIPPED, ERROR, XFAIL |
| `Deployment` | Dataclass | infra | Deployment operation |
| `DeploymentStatus` | Enum | infra | PENDING through ROLLED_BACK |
| `Pipeline` | Dataclass | infra | CI/CD pipeline |
| `PipelineStatus` | Enum | infra | QUEUED through CANCELLED |
| `Resource` | Dataclass | infra | Managed resource |
| `BuildArtifact` | Dataclass | infra | Build output artifact |
| `Metric` | Dataclass | infra | Metric measurement |
| `MetricType` | Enum | infra | COUNTER, GAUGE, HISTOGRAM, SUMMARY |
| `Credential` | Dataclass | infra | Credential reference |
| `Permission` | Dataclass | infra | Permission grant |
| `WorkflowStep` | Dataclass | infra | Workflow step |

## PAI Algorithm Phase Mapping

| Phase | Schemas Module Contribution |
|-------|---------------------------|
| **OBSERVE** | `Result`, `AnalysisResult`, `SecurityFinding` provide structured observations |
| **ORIENT** | `ModuleInfo`, `Config` describe system capabilities and configuration |
| **DECIDE** | `Task`, `TaskStatus` model decision-making work items |
| **EXECUTE** | `Deployment`, `Pipeline`, `WorkflowStep` track execution state |
| **VERIFY** | `TestResult`, `TestStatus`, `Metric` capture verification outcomes |
| **LEARN** | All `to_dict()` methods enable serialization for pattern analysis |

## Architecture Role

**Foundation Layer** -- This module is imported by every other codomyrmex module. It has zero upward dependencies and must remain stable, lightweight, and free of side effects. All types are pure data definitions with no I/O or external dependencies.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
