# Schemas - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Schemas module. The schemas module provides standardized shared types (enums and dataclasses) used across all Codomyrmex modules. It contains no callable functions or services -- only data type definitions that other modules import and use.

All types are importable from the top-level package:

```python
from codomyrmex.schemas import Result, ResultStatus, Task, TaskStatus
```

---

## Enums

### `ResultStatus`

- **Module**: `core.py`
- **Description**: Status of an operation result.
- **Values**:

| Member | Value |
|--------|-------|
| `SUCCESS` | `"success"` |
| `FAILURE` | `"failure"` |
| `PARTIAL` | `"partial"` |
| `SKIPPED` | `"skipped"` |
| `TIMEOUT` | `"timeout"` |

### `TaskStatus`

- **Module**: `core.py`
- **Description**: Status of a task.
- **Values**:

| Member | Value |
|--------|-------|
| `PENDING` | `"pending"` |
| `IN_PROGRESS` | `"in_progress"` |
| `COMPLETED` | `"completed"` |
| `FAILED` | `"failed"` |
| `CANCELLED` | `"cancelled"` |

### `CodeEntityType`

- **Module**: `code.py`
- **Description**: Type of code entity.
- **Values**:

| Member | Value |
|--------|-------|
| `FILE` | `"file"` |
| `CLASS` | `"class"` |
| `FUNCTION` | `"function"` |
| `METHOD` | `"method"` |
| `VARIABLE` | `"variable"` |
| `MODULE` | `"module"` |
| `PACKAGE` | `"package"` |
| `IMPORT` | `"import"` |

### `AnalysisSeverity`

- **Module**: `code.py`
- **Description**: Severity level for analysis findings.
- **Values**:

| Member | Value |
|--------|-------|
| `INFO` | `"info"` |
| `LOW` | `"low"` |
| `MEDIUM` | `"medium"` |
| `HIGH` | `"high"` |
| `CRITICAL` | `"critical"` |

### `SecuritySeverity`

- **Module**: `code.py`
- **Description**: Severity level for security findings.
- **Values**:

| Member | Value |
|--------|-------|
| `LOW` | `"low"` |
| `MEDIUM` | `"medium"` |
| `HIGH` | `"high"` |
| `CRITICAL` | `"critical"` |

### `TestStatus`

- **Module**: `code.py`
- **Description**: Status of a test execution.
- **Values**:

| Member | Value |
|--------|-------|
| `PASSED` | `"passed"` |
| `FAILED` | `"failed"` |
| `SKIPPED` | `"skipped"` |
| `ERROR` | `"error"` |
| `XFAIL` | `"xfail"` |

### `DeploymentStatus`

- **Module**: `infra.py`
- **Description**: Status of a deployment.
- **Values**:

| Member | Value |
|--------|-------|
| `PENDING` | `"pending"` |
| `IN_PROGRESS` | `"in_progress"` |
| `DEPLOYED` | `"deployed"` |
| `FAILED` | `"failed"` |
| `ROLLING_BACK` | `"rolling_back"` |
| `ROLLED_BACK` | `"rolled_back"` |

### `PipelineStatus`

- **Module**: `infra.py`
- **Description**: Status of a CI/CD pipeline.
- **Values**:

| Member | Value |
|--------|-------|
| `QUEUED` | `"queued"` |
| `RUNNING` | `"running"` |
| `SUCCEEDED` | `"succeeded"` |
| `FAILED` | `"failed"` |
| `CANCELLED` | `"cancelled"` |

### `MetricType`

- **Module**: `infra.py`
- **Description**: Type of metric.
- **Values**:

| Member | Value |
|--------|-------|
| `COUNTER` | `"counter"` |
| `GAUGE` | `"gauge"` |
| `HISTOGRAM` | `"histogram"` |
| `SUMMARY` | `"summary"` |

---

## Dataclasses

### `Result`

- **Module**: `core.py`
- **Description**: Standard result type for module operations. Every module operation should return a Result to enable consistent error handling and status checking.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | `ResultStatus` | *(required)* | Operation outcome |
| `data` | `Any` | `None` | Result payload |
| `message` | `str` | `""` | Human-readable message |
| `errors` | `list[str]` | `[]` | List of error strings |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |
| `duration_ms` | `float \| None` | `None` | Operation duration in milliseconds |

- **Properties**:
  - `ok -> bool`: Returns `True` if `status == ResultStatus.SUCCESS`, `False` otherwise.
- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to a plain dictionary. Enum values are converted to their string value.

### `Task`

- **Module**: `core.py`
- **Description**: Standard task type for work items across modules. Used by orchestrator, agents, and workflow systems.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | *(required)* | Unique task identifier |
| `name` | `str` | *(required)* | Human-readable task name |
| `status` | `TaskStatus` | `TaskStatus.PENDING` | Current task state |
| `description` | `str` | `""` | Task description |
| `module` | `str` | `""` | Owning module name |
| `input_data` | `dict[str, Any]` | `{}` | Task input parameters |
| `output_data` | `dict[str, Any]` | `{}` | Task output results |
| `dependencies` | `list[str]` | `[]` | IDs of dependent tasks |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to a plain dictionary.

### `Config`

- **Module**: `core.py`
- **Description**: Standard configuration type for modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Configuration name |
| `values` | `dict[str, Any]` | `{}` | Configuration key-value pairs |
| `version` | `str` | `"1.0.0"` | Configuration version |
| `module` | `str` | `""` | Owning module name |

- **Methods**:
  - `get(key: str, default: Any = None) -> Any`: Returns the value for `key` from `values`, or `default` if the key is missing.
  - `set(key: str, value: Any) -> None`: Sets `key` to `value` in `values`.

### `ModuleInfo`

- **Module**: `core.py`
- **Description**: Information about a codomyrmex module.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Module name |
| `version` | `str` | `"0.1.0"` | Module version |
| `layer` | `str` | `""` | Architecture layer (foundation, core, service, application) |
| `description` | `str` | `""` | Module description |
| `dependencies` | `list[str]` | `[]` | Module dependencies |
| `has_cli` | `bool` | `False` | Whether module exposes CLI commands |
| `has_mcp` | `bool` | `False` | Whether module exposes MCP tools |
| `has_events` | `bool` | `False` | Whether module emits events |

### `ToolDefinition`

- **Module**: `core.py`
- **Description**: Definition of a tool exposed via MCP or CLI.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Tool name |
| `description` | `str` | *(required)* | Tool description |
| `module` | `str` | *(required)* | Owning module name |
| `input_schema` | `dict[str, Any]` | `{}` | JSON Schema for input |
| `output_schema` | `dict[str, Any]` | `{}` | JSON Schema for output |
| `tags` | `list[str]` | `[]` | Categorization tags |

### `Notification`

- **Module**: `core.py`
- **Description**: Standard notification type.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `str` | *(required)* | Notification title |
| `message` | `str` | *(required)* | Notification body |
| `level` | `str` | `"info"` | Severity: info, warning, error, critical |
| `source` | `str` | `""` | Originating module or system |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

### `CodeEntity`

- **Module**: `code.py`
- **Description**: Represents a code entity (file, class, function, etc.). Used by static_analysis, pattern_matching, and coding modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Entity name |
| `entity_type` | `CodeEntityType` | *(required)* | Kind of entity |
| `file_path` | `str` | `""` | File containing the entity |
| `line_start` | `int` | `0` | Starting line number |
| `line_end` | `int` | `0` | Ending line number |
| `language` | `str` | `"python"` | Programming language |
| `content` | `str` | `""` | Source code content |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes fields to dictionary (note: `content` is excluded from output).

### `AnalysisResult`

- **Module**: `code.py`
- **Description**: Result of a code analysis operation. Used by static_analysis, coding, and security modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `analyzer` | `str` | *(required)* | Analyzer name (e.g. "ruff", "mypy") |
| `target` | `str` | *(required)* | Analysis target path |
| `severity` | `AnalysisSeverity` | `AnalysisSeverity.INFO` | Finding severity |
| `message` | `str` | `""` | Finding description |
| `file_path` | `str` | `""` | File where finding occurs |
| `line` | `int` | `0` | Line number |
| `column` | `int` | `0` | Column number |
| `rule_id` | `str` | `""` | Rule identifier (e.g. "E501") |
| `suggestion` | `str` | `""` | Suggested fix |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

### `SecurityFinding`

- **Module**: `code.py`
- **Description**: A security-related finding from analysis or scanning. Used by security and static_analysis modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `str` | *(required)* | Finding title |
| `severity` | `SecuritySeverity` | *(required)* | Finding severity |
| `description` | `str` | `""` | Detailed description |
| `file_path` | `str` | `""` | Affected file |
| `line` | `int` | `0` | Line number |
| `cwe_id` | `str` | `""` | CWE identifier (e.g. "CWE-79") |
| `owasp_category` | `str` | `""` | OWASP category |
| `remediation` | `str` | `""` | Suggested remediation |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

### `TestResult`

- **Module**: `code.py`
- **Description**: Result of a test execution. Used by testing and workflow_testing modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `test_name` | `str` | *(required)* | Test function/method name |
| `status` | `TestStatus` | *(required)* | Test outcome |
| `duration_ms` | `float` | `0.0` | Test duration in milliseconds |
| `module` | `str` | `""` | Module under test |
| `file_path` | `str` | `""` | Test file path |
| `message` | `str` | `""` | Status message or error text |
| `stdout` | `str` | `""` | Captured standard output |
| `stderr` | `str` | `""` | Captured standard error |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes fields to dictionary (note: `stdout` and `stderr` are excluded from output).

### `Deployment`

- **Module**: `infra.py`
- **Description**: Represents a deployment operation. Used by deployment, containerization, and edge_computing modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | *(required)* | Deployment identifier |
| `name` | `str` | *(required)* | Deployment name |
| `status` | `DeploymentStatus` | `DeploymentStatus.PENDING` | Current deployment state |
| `target` | `str` | `""` | Deployment target (e.g. cluster name) |
| `version` | `str` | `""` | Version being deployed |
| `environment` | `str` | `""` | Target environment |
| `artifacts` | `list[str]` | `[]` | Artifact references |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

### `Pipeline`

- **Module**: `infra.py`
- **Description**: Represents a CI/CD pipeline. Used by ci_cd_automation and build_synthesis modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | *(required)* | Pipeline identifier |
| `name` | `str` | *(required)* | Pipeline name |
| `status` | `PipelineStatus` | `PipelineStatus.QUEUED` | Current pipeline state |
| `stages` | `list[str]` | `[]` | Ordered list of stage names |
| `current_stage` | `str` | `""` | Currently executing stage |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

### `Resource`

- **Module**: `infra.py`
- **Description**: Represents a managed resource. Used by cloud, containerization, and service_mesh modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | *(required)* | Resource identifier |
| `name` | `str` | *(required)* | Resource name |
| `resource_type` | `str` | `""` | Resource type (e.g. "rds", "ec2") |
| `provider` | `str` | `""` | Cloud provider |
| `status` | `str` | `"active"` | Resource status |
| `properties` | `dict[str, Any]` | `{}` | Resource-specific properties |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

### `BuildArtifact`

- **Module**: `infra.py`
- **Description**: Represents a build artifact. Used by build_synthesis and ci_cd_automation modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Artifact name |
| `path` | `str` | *(required)* | Artifact file path |
| `artifact_type` | `str` | `""` | Type: binary, docker_image, package, etc. |
| `size_bytes` | `int` | `0` | File size in bytes |
| `checksum` | `str` | `""` | Integrity checksum |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

### `Metric`

- **Module**: `infra.py`
- **Description**: Represents a metric measurement. Used by metrics, telemetry, and observability_dashboard modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Metric name |
| `value` | `float` | *(required)* | Metric value |
| `metric_type` | `MetricType` | `MetricType.GAUGE` | Kind of metric |
| `labels` | `dict[str, str]` | `{}` | Metric labels/tags |
| `unit` | `str` | `""` | Unit of measurement |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

### `Credential`

- **Module**: `infra.py`
- **Description**: Represents a credential reference. Never stores secrets directly. Used by auth, encryption, and security modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | *(required)* | Credential identifier |
| `name` | `str` | *(required)* | Credential name |
| `credential_type` | `str` | `""` | Type: api_key, token, certificate, etc. |
| `provider` | `str` | `""` | Credential provider |
| `is_valid` | `bool` | `True` | Whether credential is currently valid |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

### `Permission`

- **Module**: `infra.py`
- **Description**: Represents a permission grant. Used by auth and security modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `subject` | `str` | *(required)* | Subject (e.g. "user:admin") |
| `action` | `str` | *(required)* | Action (e.g. "write", "read") |
| `resource` | `str` | *(required)* | Target resource |
| `effect` | `str` | `"allow"` | Effect: "allow" or "deny" |
| `conditions` | `dict[str, Any]` | `{}` | Conditional constraints |

### `WorkflowStep`

- **Module**: `infra.py`
- **Description**: Represents a step in a workflow. Used by orchestrator and logistics modules.
- **Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | *(required)* | Step identifier |
| `name` | `str` | *(required)* | Step name |
| `action` | `str` | *(required)* | Action to execute |
| `status` | `str` | `"pending"` | Step status |
| `input_data` | `dict[str, Any]` | `{}` | Step input parameters |
| `output_data` | `dict[str, Any]` | `{}` | Step output results |
| `dependencies` | `list[str]` | `[]` | IDs of prerequisite steps |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata |

- **Methods**:
  - `to_dict() -> dict[str, Any]`: Serializes all fields to dictionary.

---

## Authentication & Authorization

Not applicable. This module provides data type definitions only.

## Rate Limiting

Not applicable. This module provides data type definitions only.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. Current version: `0.1.0`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
