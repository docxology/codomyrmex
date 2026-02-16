# Schemas Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Shared schema registry providing standardized types used across all Codomyrmex modules. Foundation layer type library that replaces per-module type definitions and enables interoperability between modules at every layer. Provides 27 exports (9 enums, 18 dataclasses) across 3 submodules.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Core Types** -- `Result`, `ResultStatus`, `Task`, `TaskStatus`, `Config`, `ModuleInfo`, `ToolDefinition`, `Notification`.
- **Code Types** -- `CodeEntity`, `AnalysisResult`, `SecurityFinding`, `TestResult` with severity enums.
- **Infrastructure Types** -- `Deployment`, `Pipeline`, `Resource`, `BuildArtifact`, `Metric`, `Credential`, `Permission`.

## Quick Start

```python
from codomyrmex.schemas import Result, ResultStatus, Config

# Create a standard result envelope
result = Result(
    status=ResultStatus.SUCCESS,
    data={"files_processed": 42},
    message="Analysis complete",
)
if result.ok:
    print(result.data)

# Module configuration with get/set helpers
config = Config(name="deployment", values={"region": "us-east-1"})
region = config.get("region")  # "us-east-1"
```

## API Reference

### Core Types (`core.py`)

| Export | Kind | Description |
|--------|------|-------------|
| `ResultStatus` | Enum | SUCCESS, FAILURE, PARTIAL, SKIPPED, TIMEOUT |
| `TaskStatus` | Enum | PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED |
| `Result` | Dataclass | Standard result envelope with `ok` property |
| `Task` | Dataclass | Work item with dependencies and input/output data |
| `Config` | Dataclass | Module configuration with `get`/`set` methods |

### Code Types (`code.py`)

| Export | Kind | Description |
|--------|------|-------------|
| `CodeEntity` | Dataclass | Represents a code entity with file path and language |
| `AnalysisResult` | Dataclass | Static analysis finding with severity |
| `SecurityFinding` | Dataclass | Security vulnerability with CWE and remediation |
| `TestResult` | Dataclass | Test execution result with timing |

### Infrastructure Types (`infra.py`)

| Export | Kind | Description |
|--------|------|-------------|
| `Deployment` | Dataclass | Deployment operation with target and version |
| `Pipeline` | Dataclass | CI/CD pipeline with stages |
| `Metric` | Dataclass | Metric measurement with type and labels |
| `Permission` | Dataclass | Permission grant with subject and action |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k schemas -v
```

## Related Modules

- [Exceptions](../exceptions/README.md)
- [Validation](../validation/README.md)

## Navigation

- **Source**: [src/codomyrmex/schemas/](../../../src/codomyrmex/schemas/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/schemas/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/schemas/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
