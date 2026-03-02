# Agent Guidelines - Exceptions

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

The `exceptions` package is the centralized source for all error types in Codomyrmex. Agents should strictly use these exceptions instead of generic Python exceptions (like `RuntimeError` or `ValueError`) whenever possible to ensure proper error tracking and context propagation. All exceptions inherit from `CodomyrmexError` which provides a consistent interface with `message`, `context` dict, `error_code`, and `to_dict()` serialization. The hierarchy is organized by domain: AI, analysis, config, execution, git, I/O, network, orchestration, visualization, CEREBRUM, and specialized.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Re-exports all 60+ exception classes from domain files |
| `base.py` | `CodomyrmexError` root class with `message`, `context`, `error_code`, `to_dict()`; utility functions `format_exception_chain()`, `create_error_context()` |
| `ai.py` | `AIProviderError` (provider_name, model_name), `CodeGenerationError` (language, prompt_preview), `CodeEditingError` (file_path, edit_type), `ModelContextError` (protocol_version, operation) |
| `config.py` | `ConfigurationError` (config_key, config_file), `EnvironmentError` (variable_name, expected_value), `DependencyError` (dependency_name, required_version, installed_version) |
| `execution.py` | `CodeExecutionError` (exit_code, stdout, stderr), `SandboxError`, `ContainerError`, `BuildError`, `SynthesisError` |
| `git.py` | `GitOperationError`, `RepositoryError` |
| `network.py` | `NetworkError` (url, status_code), `APIError`, `ValidationError`, `SchemaError`, `TimeoutError` |
| `orchestration.py` | `OrchestrationError`, `WorkflowError`, `ProjectManagementError`, `TaskExecutionError` |
| `io.py` | `FileOperationError` (file_path, operation), `DirectoryError` (directory_path, operation) |
| `cerebrum.py` | `CerebrumError`, `CaseError`, `CaseNotFoundError`, `InvalidCaseError`, `InferenceError`, `BayesianInferenceError`, `ActiveInferenceError`, `ModelError`, `NetworkStructureError`, `TransformationError` |
| `analysis.py` | `StaticAnalysisError`, `PatternMatchingError`, `SecurityAuditError` |
| `viz.py` | `VisualizationError`, `PlottingError`, `DocumentationError`, `APIDocumentationError` |
| `specialized.py` | Domain-specific: `DatabaseError`, `CacheError`, `PluginError`, `EncryptionError`, `EventError`, `DeploymentError`, `IDEError`, `IDEConnectionError`, `TerminalError`, `InteractiveShellError`, `PerformanceError`, `LoggingError`, `SystemDiscoveryError`, `CapabilityScanError`, `MemoryError`, `SessionError`, `ArtifactError`, `SerializationError`, `CompressionError`, `CircuitOpenError`, `BulkheadFullError`, `AuthenticationError`, `SkillError`, `TemplateError`, `ResourceError`, `CICDError`, `Modeling3DError`, `PhysicalManagementError`, `SimulationError`, `SpatialError`, `CommandExecutionError` |

## Key Classes

- **CodomyrmexError** -- Root exception. All Codomyrmex exceptions inherit from this. Provides `message: str`, `context: dict`, `error_code: str`, `to_dict() -> dict`. Context is populated via `**kwargs` in constructor.
- **AIProviderError** -- AI provider failures. Context fields: `provider_name`, `model_name`.
- **CodeGenerationError** -- Code generation failures. Context fields: `language`, `prompt_preview`.
- **CodeEditingError** -- Code editing failures. Context fields: `file_path`, `edit_type`.
- **ModelContextError** -- MCP protocol failures. Context fields: `protocol_version`, `operation`.
- **ConfigurationError** -- Configuration issues. Context fields: `config_key`, `config_file`.
- **EnvironmentError** -- Environment setup issues. Context fields: `variable_name`, `expected_value`.
- **DependencyError** -- Missing/incompatible dependencies. Context fields: `dependency_name`, `required_version`, `installed_version`.
- **CodeExecutionError** -- Code execution failures. Context fields: `exit_code`, `stdout`, `stderr`.
- **SandboxError** -- Sandbox/isolation failures.
- **ContainerError** -- Container operation failures.
- **BuildError** -- Build process failures.
- **GitOperationError** -- Git command failures.
- **RepositoryError** -- Repository state failures.
- **NetworkError** -- Network operation failures. Context fields: `url`, `status_code`.
- **APIError** -- API call failures.
- **ValidationError** -- Data validation failures.
- **SchemaError** -- Schema validation failures.
- **FileOperationError** -- File operation failures. Context fields: `file_path`, `operation`.
- **DirectoryError** -- Directory operation failures. Context fields: `directory_path`, `operation`.
- **OrchestrationError** -- Workflow orchestration failures.
- **WorkflowError** -- Workflow execution failures.
- **CerebrumError** -- CEREBRUM cognitive engine root error.
- **InferenceError** -- Inference operation failures.
- **DatabaseError** -- Database operation failures.
- **CacheError** -- Cache operation failures.
- **PluginError** -- Plugin system failures.
- **EncryptionError** -- Encryption/decryption failures.
- **EventError** -- Event system failures.
- **CircuitOpenError** -- Circuit breaker control flow signal (inherits from `Exception`, NOT `CodomyrmexError`).
- **BulkheadFullError** -- Bulkhead pattern control flow signal.

## Key Rules

1. **Inheritance**: All new exceptions MUST inherit from `CodomyrmexError` (or a subclass).
2. **Context**: Always provide a `context` dictionary when raising errors with dynamic data (e.g., `file_path`, `status_code`, `user_id`).
3. **Re-exports**: If you add a new exception file, you MUST re-export its classes in `__init__.py`.
4. **Granularity**: Use specific exceptions (`FileOperationError`) over generic ones (`CodomyrmexError`).

## Agent Instructions

1. **Use typed exceptions** -- Always raise the most specific `CodomyrmexError` subclass available for the domain.
2. **Chain exceptions** -- Always use `raise XError("msg") from e` to preserve the original traceback.
3. **Provide context** -- Pass domain-specific named kwargs: `raise AIProviderError("msg", provider_name="OpenAI", model_name="gpt-4o")`.
4. **Catch specifically** -- Catch `CodomyrmexError` subclasses, not bare `Exception`. Use `e.context`, `e.error_code`, `e.to_dict()` for structured handling.
5. **Format chains** -- Use `format_exception_chain(e)` to produce readable multi-line error traces for logging.
6. **Create context helpers** -- Use `create_error_context(**kwargs)` to build context dicts that filter out `None` values.

## Operating Contracts

- All new exception classes MUST inherit from `CodomyrmexError` or a domain subclass -- never from bare `Exception`.
- Always chain exceptions with `from e` when re-raising to preserve the original cause.
- Never catch base `Exception` silently (`except: pass` or `except Exception: pass`) -- log and re-raise or raise a specific typed error.
- Use the most specific exception class available: `FileOperationError` over `CodomyrmexError`, `AIProviderError` over `CodeGenerationError` when the failure is provider-level.
- `CircuitOpenError` and `BulkheadFullError` inherit from `Exception` (not `CodomyrmexError`) because they are control flow signals, not domain errors.
- `CodomyrmexError.to_dict()` is the canonical serialization format for error reporting and API responses.
- **DO NOT** raise bare `RuntimeError`, `ValueError`, or `Exception` in Codomyrmex code -- always use typed codomyrmex exceptions.
- **DO NOT** suppress exceptions silently -- log and re-raise or raise a specific error.
- **DO NOT** use `CircuitOpenError` for domain errors -- it is a control-flow signal only.

## Usage Patterns

### Raising Exceptions

```python
from codomyrmex.exceptions import ConfigurationError, AIProviderError

# Domain-specific context via named parameters
if not config_file.exists():
    raise ConfigurationError(
        "Config file missing",
        config_file=path,
        config_key="api_key"
    )

# Another example with AI Provider
raise AIProviderError(
    "Rate limit exceeded",
    provider_name="OpenAI",
    model_name="gpt-4o"
)
```

### Catching Exceptions

```python
from codomyrmex.exceptions import CodomyrmexError

try:
    execute_workflow()
except CodomyrmexError as e:
    # All Codomyrmex errors have a consistent interface
    log_error(e.message, e.context, e.error_code)
```

### Chaining Exceptions

```python
from codomyrmex.exceptions import FileOperationError

try:
    data = open(path, "rb").read()
except OSError as e:
    raise FileOperationError(
        "Failed to read input file",
        file_path=path,
        operation="read"
    ) from e
```

## Special Cases

- **CEREBRUM**: Use `codomyrmex.exceptions.cerebrum` for all cognitive/inference errors.
- **Circuit Breakers**: Use `CircuitOpenError` (inherits from `Exception`, not `CodomyrmexError`, as it's a control flow signal).

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, raise/catch any exception class | TRUSTED |
| **Architect** | Read + Design | Exception hierarchy design, context propagation review | OBSERVED |
| **QATester** | Validation | Exception context validation, error code coverage testing | OBSERVED |
| **Researcher** | Read-only | Inspect exception types and structures for analysis | SAFE |

### Engineer Agent
**Use Cases**: Use typed exception classes for explicit error handling, raise `CodomyrmexError` subclasses during BUILD/EXECUTE phases.

### Architect Agent
**Use Cases**: Design error hierarchy, review exception granularity, ensure context propagation patterns are consistent.

### QATester Agent
**Use Cases**: Unit and integration test execution, exception context validation, error code coverage verification during VERIFY.

### Researcher Agent
**Use Cases**: Inspect exception structures to understand error patterns and domain boundaries.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
