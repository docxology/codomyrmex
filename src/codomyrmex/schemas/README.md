# Schemas Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

Shared schema registry providing standardized types used across all Codomyrmex modules.
This is the Foundation layer type library that replaces per-module type definitions and enables interoperability between modules at every layer.

## Key Exports

### Core Types (`core.py`)

| Export | Kind | Purpose |
|--------|------|---------|
| `ResultStatus` | Enum | Operation outcome: SUCCESS, FAILURE, PARTIAL, SKIPPED, TIMEOUT |
| `TaskStatus` | Enum | Work item state: PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED |
| `Result` | Dataclass | Standard result envelope with status, data, errors, metadata, and `ok` property |
| `Task` | Dataclass | Work item with id, name, status, dependencies, and input/output data |
| `Config` | Dataclass | Module configuration with `get`/`set` convenience methods |
| `ModuleInfo` | Dataclass | Module metadata: name, version, layer, capabilities |
| `ToolDefinition` | Dataclass | MCP/CLI tool description with input/output schemas |
| `Notification` | Dataclass | Standard notification with title, message, level, source |

### Code Types (`code.py`)

| Export | Kind | Purpose |
|--------|------|---------|
| `CodeEntityType` | Enum | Entity kind: FILE, CLASS, FUNCTION, METHOD, VARIABLE, MODULE, PACKAGE, IMPORT |
| `AnalysisSeverity` | Enum | Analysis finding severity: INFO, LOW, MEDIUM, HIGH, CRITICAL |
| `SecuritySeverity` | Enum | Security finding severity: LOW, MEDIUM, HIGH, CRITICAL |
| `TestStatus` | Enum | Test execution outcome: PASSED, FAILED, SKIPPED, ERROR, XFAIL |
| `CodeEntity` | Dataclass | Represents a code entity with file path, line range, language |
| `AnalysisResult` | Dataclass | Static analysis finding with analyzer, rule, severity, suggestion |
| `SecurityFinding` | Dataclass | Security vulnerability with CWE, OWASP category, remediation |
| `TestResult` | Dataclass | Test execution result with timing, stdout/stderr capture |

### Infrastructure Types (`infra.py`)

| Export | Kind | Purpose |
|--------|------|---------|
| `DeploymentStatus` | Enum | Deployment state: PENDING, IN_PROGRESS, DEPLOYED, FAILED, ROLLING_BACK, ROLLED_BACK |
| `PipelineStatus` | Enum | Pipeline state: QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED |
| `MetricType` | Enum | Metric kind: COUNTER, GAUGE, HISTOGRAM, SUMMARY |
| `Deployment` | Dataclass | Deployment operation with target, version, environment, artifacts |
| `Pipeline` | Dataclass | CI/CD pipeline with stages and current stage tracking |
| `Resource` | Dataclass | Managed resource with type, provider, status, properties |
| `BuildArtifact` | Dataclass | Build output with path, type, size, checksum |
| `Metric` | Dataclass | Metric measurement with type, labels, unit |
| `Credential` | Dataclass | Credential reference (never stores secrets directly) |
| `Permission` | Dataclass | Permission grant with subject, action, resource, effect |
| `WorkflowStep` | Dataclass | Workflow step with action, status, dependencies |

**Total**: 27 exports (9 enums, 18 dataclasses) across 3 submodules.

## Quick Start

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

```python
from codomyrmex.schemas import Config

# Module configuration with get/set helpers
config = Config(name="deployment", values={"region": "us-east-1"})
region = config.get("region")          # "us-east-1"
config.set("replicas", 3)             # adds new key
missing = config.get("timeout", 30)   # returns default
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/schemas/ -v
```

## Documentation

- [API Specification](API_SPECIFICATION.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md)

## Navigation

- [PAI](PAI.md) | [API_SPECIFICATION](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
