# Schemas Module — Agent Coordination

## Purpose

Shared Schema Registry for Codomyrmex

Provides standardized types used across modules to enable interoperability.
This is the Foundation layer type library that replaces per-module type definitions.

## Key Capabilities


## Agent Usage Patterns

```python
from codomyrmex.schemas import Result, ResultStatus, Task, TaskStatus

# Create a result from a module operation
result = Result(
    status=ResultStatus.SUCCESS,
    data={"files_processed": 42},
    message="Analysis complete",
    duration_ms=350.0,
)

# Check if operation succeeded
if result.ok:
    print(result.data)

# Serialize for JSON transport
payload = result.to_dict()
# {"status": "success", "data": {...}, "message": "...", ...}

# Create a task for the orchestrator
task = Task(
    id="task-001",
    name="lint-check",
    status=TaskStatus.PENDING,
    module="static_analysis",
    input_data={"target": "src/"},
)
```

## Key Components

| Export | Type |
|--------|------|
| `Result` | Public API |
| `ResultStatus` | Public API |
| `Task` | Public API |
| `TaskStatus` | Public API |
| `Config` | Public API |
| `ModuleInfo` | Public API |
| `ToolDefinition` | Public API |
| `Notification` | Public API |
| `CodeEntity` | Public API |
| `CodeEntityType` | Public API |
| `AnalysisResult` | Public API |
| `AnalysisSeverity` | Public API |
| `SecurityFinding` | Public API |
| `SecuritySeverity` | Public API |
| `TestResult` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `code.py` | Code-related shared types for Codomyrmex. |
| `core.py` | Core shared types for Codomyrmex. |
| `infra.py` | Infrastructure shared types for Codomyrmex. |

## Integration Points

- **Docs**: [Module Documentation](../../../docs/modules/schemas/README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k schemas -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
