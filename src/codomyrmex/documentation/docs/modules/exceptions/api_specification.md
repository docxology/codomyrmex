# Exceptions - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Exceptions module. This module provides a comprehensive, hierarchical error handling system for the entire Codomyrmex ecosystem. All exceptions inherit from a single root class (`CodomyrmexError`) and are organized into domain-specific categories across 12 source files.

## Endpoints / Functions / Interfaces

### Class: `CodomyrmexError`

- **Description**: The root exception class for all Codomyrmex-related errors. Provides a consistent interface with structured context information, error codes, and serialization support. All other project exceptions inherit from this class.
- **Module**: `codomyrmex.exceptions.base`
- **Inherits**: `Exception`
- **Parameters/Arguments** (constructor):
    - `message` (str): The error message
    - `context` (dict[str, Any] | None, optional): Additional context information about the error. Defaults to `{}`
    - `error_code` (str | None, optional): A unique error code. Defaults to the class name
    - `**kwargs` (Any): Additional keyword arguments merged into `context`
- **Attributes**:
    - `message` (str): The error message
    - `context` (dict[str, Any]): Structured context dictionary
    - `error_code` (str): Error code identifier (defaults to class name)
- **Methods**:
    - `__str__() -> str`: Returns formatted string `[error_code] message (Context: key=value, ...)`.
    - `to_dict() -> dict[str, Any]`: Serializes the exception to a dictionary with keys `error_type`, `error_code`, `message`, and `context`.

### Function: `format_exception_chain(exception: Exception) -> str`

- **Description**: Formats an exception chain for display, walking the `__cause__` and `__context__` chain and returning a newline-separated string of formatted error messages.
- **Module**: `codomyrmex.exceptions.base`
- **Parameters/Arguments**:
    - `exception` (Exception): The exception to format
- **Returns/Response**: `str` - A formatted string representation of the full exception chain.

### Function: `create_error_context(**kwargs: Any) -> dict[str, Any]`

- **Description**: Utility function to create a context dictionary for exception handling. Filters out `None` values automatically.
- **Module**: `codomyrmex.exceptions.base`
- **Parameters/Arguments**:
    - `**kwargs` (Any): Key-value pairs to include in the context
- **Returns/Response**: `dict[str, Any]` - A dictionary with all non-None values.

---

## Exception Categories

### Configuration and Setup (`config.py`)

#### `ConfigurationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when there is an issue with configuration settings.
- **Additional Parameters**:
    - `config_key` (str | None, optional): The configuration key that caused the error
    - `config_file` (str | Path | None, optional): Path to the configuration file

#### `EnvironmentError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when the environment is not properly set up.

#### `DependencyError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when a required dependency is missing or incompatible.

---

### File and I/O (`io.py`)

#### `FileOperationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when file operations fail.
- **Additional Parameters**:
    - `file_path` (str | Path | None, optional): Path to the file that caused the error

#### `DirectoryError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when directory operations fail.

---

### AI and Code Generation (`ai.py`)

#### `AIProviderError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when AI provider operations fail.

#### `CodeGenerationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when code generation fails.

#### `CodeEditingError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when code editing operations fail.

#### `ModelContextError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when model context protocol operations fail.

---

### Analysis (`analysis.py`)

#### `StaticAnalysisError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when static analysis operations fail.

#### `PatternMatchingError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when pattern matching operations fail.

#### `SecurityAuditError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when security audit operations fail.

---

### Execution and Build (`execution.py`)

#### `CodeExecutionError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when code execution fails.
- **Additional Parameters**:
    - `exit_code` (int | None, optional): Process exit code
    - `stdout` (str | None, optional): Captured standard output
    - `stderr` (str | None, optional): Captured standard error

#### `SandboxError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when sandbox operations fail.

#### `ContainerError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when container operations fail.

#### `BuildError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when build operations fail.

#### `SynthesisError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when code synthesis operations fail.

---

### Git and Version Control (`git.py`)

#### `GitOperationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when git operations fail.
- **Additional Parameters**:
    - `git_command` (str | None, optional): The git command that failed
    - `repository_path` (str | Path | None, optional): Path to the repository

#### `RepositoryError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when repository operations fail.

---

### Visualization and Documentation (`viz.py`)

#### `VisualizationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when data visualization operations fail.

#### `PlottingError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when plotting operations fail.

#### `DocumentationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when documentation operations fail.

#### `APIDocumentationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when API documentation generation fails.

---

### Orchestration (`orchestration.py`)

#### `OrchestrationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when orchestration operations fail.

#### `WorkflowError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when workflow execution fails.

#### `ProjectManagementError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when project management operations fail.

#### `TaskExecutionError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when task execution fails.

---

### Network, API, and Validation (`network.py`)

#### `NetworkError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when network operations fail.
- **Additional Parameters**:
    - `url` (str | None, optional): The URL that caused the error
    - `status_code` (int | None, optional): HTTP status code

#### `APIError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when API operations fail.

#### `ValidationError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when data validation fails.
- **Additional Parameters**:
    - `field_name` (str | None, optional): The field that failed validation
    - `validation_rule` (str | None, optional): The rule that was violated

#### `SchemaError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when schema validation fails.

#### `TimeoutError`

- **Inherits**: `CodomyrmexError`
- **Description**: Raised when operations timeout.
- **Additional Parameters**:
    - `timeout_seconds` (float | None, optional): The timeout duration that was exceeded

---

### CEREBRUM (`cerebrum.py`)

#### `CerebrumError`

- **Inherits**: `CodomyrmexError`
- **Description**: Base exception class for all CEREBRUM cognitive system errors.

#### `CaseError`

- **Inherits**: `CerebrumError`
- **Description**: Exception raised for case-related errors.

#### `CaseNotFoundError`

- **Inherits**: `CaseError`
- **Description**: Exception raised when a case is not found.

#### `InvalidCaseError`

- **Inherits**: `CaseError`
- **Description**: Exception raised when a case is invalid.

#### `BayesianInferenceError`

- **Inherits**: `CerebrumError`
- **Description**: Exception raised for Bayesian inference errors.

#### `InferenceError`

- **Inherits**: `BayesianInferenceError`
- **Description**: Exception raised when inference fails.

#### `NetworkStructureError`

- **Inherits**: `BayesianInferenceError`
- **Description**: Exception raised when Bayesian network structure is invalid.

#### `ActiveInferenceError`

- **Inherits**: `CerebrumError`
- **Description**: Exception raised for active inference errors.

#### `ModelError`

- **Inherits**: `CerebrumError`
- **Description**: Exception raised for model-related errors.

#### `TransformationError`

- **Inherits**: `CerebrumError`
- **Description**: Exception raised for model transformation errors.

---

### Specialized Domain Exceptions (`specialized.py`)

#### Performance and Monitoring

- **`PerformanceError`** (inherits `CodomyrmexError`): Raised when performance monitoring operations fail.
- **`LoggingError`** (inherits `CodomyrmexError`): Raised when logging operations fail.

#### System Discovery

- **`SystemDiscoveryError`** (inherits `CodomyrmexError`): Raised when system discovery operations fail.
- **`CapabilityScanError`** (inherits `CodomyrmexError`): Raised when capability scanning fails.

#### 3D Modeling and Physical Management

- **`Modeling3DError`** (inherits `CodomyrmexError`): Raised when 3D modeling operations fail.
- **`PhysicalManagementError`** (inherits `CodomyrmexError`): Raised when physical management operations fail.
- **`SimulationError`** (inherits `CodomyrmexError`): Raised when simulation operations fail.

#### Terminal and Interface

- **`TerminalError`** (inherits `CodomyrmexError`): Raised when terminal interface operations fail.
- **`InteractiveShellError`** (inherits `CodomyrmexError`): Raised when interactive shell operations fail.

#### Database

- **`DatabaseError`** (inherits `CodomyrmexError`): Raised when database operations fail.

#### CI/CD and Deployment

- **`CICDError`** (inherits `CodomyrmexError`): Raised when CI/CD operations fail.
- **`DeploymentError`** (inherits `CodomyrmexError`): Raised when deployment operations fail.

#### Resources and Memory

- **`ResourceError`** (inherits `CodomyrmexError`): Raised when resource operations fail.
- **`MemoryError`** (inherits `CodomyrmexError`): Raised when memory-related errors occur.

#### Spatial and Events

- **`SpatialError`** (inherits `CodomyrmexError`): Raised when spatial operations fail.
- **`EventError`** (inherits `CodomyrmexError`): Raised when event processing fails.

#### Skills and Templates

- **`SkillError`** (inherits `CodomyrmexError`): Raised when skill execution fails.
- **`TemplateError`** (inherits `CodomyrmexError`): Raised when template operations fail.

#### Plugins

- **`PluginError`** (inherits `CodomyrmexError`): Raised when plugin operations fail.
- **Additional Parameters**:
    - `plugin_name` (str | None, optional): Name of the plugin
    - `plugin_version` (str | None, optional): Version of the plugin

#### Authentication

- **`AuthenticationError`** (inherits `CodomyrmexError`): Raised when authentication fails.

#### Circuit Breaker / Bulkhead

- **`CircuitOpenError`** (inherits `Exception`): Raised when the circuit breaker is open. Note: does NOT inherit from `CodomyrmexError`.
- **`BulkheadFullError`** (inherits `Exception`): Raised when the bulkhead semaphore is exhausted. Note: does NOT inherit from `CodomyrmexError`.

#### Compression and Encryption

- **`CompressionError`** (inherits `CodomyrmexError`): Raised when compression operations fail.
- **`EncryptionError`** (inherits `CodomyrmexError`): Raised when encryption operations fail.

#### IDE

- **`IDEError`** (inherits `CodomyrmexError`): Base exception for IDE-related errors.
- **`IDEConnectionError`** (inherits `IDEError`): Raised when IDE connection fails.
- **`CommandExecutionError`** (inherits `IDEError`): Raised when an IDE command fails to execute.
- **`SessionError`** (inherits `IDEError`): Raised when there is a session-related error.
- **`ArtifactError`** (inherits `IDEError`): Raised when artifact operations fail.

#### Cache

- **`CacheError`** (inherits `CodomyrmexError`): Raised when cache operations fail.
- **Additional Parameters**:
    - `cache_key` (str | None, optional): The cache key that caused the error
    - `backend` (str | None, optional): The cache backend in use

#### Serialization

- **`SerializationError`** (inherits `CodomyrmexError`): Raised when serialization/deserialization operations fail.
- **Additional Parameters**:
    - `format_type` (str | None, optional): The serialization format (e.g., "json", "yaml")
    - `data_type` (str | None, optional): The type of data being serialized

## Data Models

All exceptions support serialization via the `to_dict()` method inherited from `CodomyrmexError`:

```python
{
    "error_type": "FileOperationError",
    "error_code": "FileOperationError",
    "message": "Cannot read file",
    "context": {"file_path": "/path/to/file.txt"}
}
```

## Inheritance Hierarchy

```
Exception
  +-- CodomyrmexError (base.py)
  |     +-- ConfigurationError (config.py)
  |     +-- EnvironmentError (config.py)
  |     +-- DependencyError (config.py)
  |     +-- FileOperationError (io.py)
  |     +-- DirectoryError (io.py)
  |     +-- AIProviderError (ai.py)
  |     +-- CodeGenerationError (ai.py)
  |     +-- CodeEditingError (ai.py)
  |     +-- ModelContextError (ai.py)
  |     +-- StaticAnalysisError (analysis.py)
  |     +-- PatternMatchingError (analysis.py)
  |     +-- SecurityAuditError (analysis.py)
  |     +-- CodeExecutionError (execution.py)
  |     +-- SandboxError (execution.py)
  |     +-- ContainerError (execution.py)
  |     +-- BuildError (execution.py)
  |     +-- SynthesisError (execution.py)
  |     +-- GitOperationError (git.py)
  |     +-- RepositoryError (git.py)
  |     +-- VisualizationError (viz.py)
  |     +-- PlottingError (viz.py)
  |     +-- DocumentationError (viz.py)
  |     +-- APIDocumentationError (viz.py)
  |     +-- OrchestrationError (orchestration.py)
  |     +-- WorkflowError (orchestration.py)
  |     +-- ProjectManagementError (orchestration.py)
  |     +-- TaskExecutionError (orchestration.py)
  |     +-- NetworkError (network.py)
  |     +-- APIError (network.py)
  |     +-- ValidationError (network.py)
  |     +-- SchemaError (network.py)
  |     +-- TimeoutError (network.py)
  |     +-- CerebrumError (cerebrum.py)
  |     |     +-- CaseError
  |     |     |     +-- CaseNotFoundError
  |     |     |     +-- InvalidCaseError
  |     |     +-- BayesianInferenceError
  |     |     |     +-- InferenceError
  |     |     |     +-- NetworkStructureError
  |     |     +-- ActiveInferenceError
  |     |     +-- ModelError
  |     |     +-- TransformationError
  |     +-- PerformanceError (specialized.py)
  |     +-- LoggingError (specialized.py)
  |     +-- SystemDiscoveryError (specialized.py)
  |     +-- ... (30+ more specialized exceptions)
  |     +-- IDEError (specialized.py)
  |           +-- IDEConnectionError
  |           +-- CommandExecutionError
  |           +-- SessionError
  |           +-- ArtifactError
  +-- CircuitOpenError (specialized.py)
  +-- BulkheadFullError (specialized.py)
```

## Authentication & Authorization

Not applicable for this internal exception module.

## Rate Limiting

Not applicable for this internal exception module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in the CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
