<!-- readme: generated -->

# exceptions

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/exceptions/`

## Overview

Codomyrmex Exception Classes.

This package provides all exception classes used throughout the Codomyrmex
project. It maintains a hierarchical structure rooted at CodomyrmexError.

Exception Categories:
    - base: CodomyrmexError, utility functions
    - config: ConfigurationError, EnvironmentError, DependencyError
    - io: FileOperationError, DirectoryError
    - ai: AIProviderError, CodeGenerationError, CodeEditingError, ModelContextError
    - analysis: StaticAnalysisError, PatternMatchingError, SecurityAuditError
    - execution: CodeExecutionError, SandboxError, ContainerError, BuildError, SynthesisError
    - git: GitOperationError, RepositoryError
    - viz: VisualizationError, PlottingError, DocumentationError, APIDocumentationError
    - orchestration: OrchestrationError, WorkflowError, ProjectManagementError, TaskExecutionError
    - network: NetworkError, APIError, ValidationError, SchemaError, TimeoutError
    - cerebrum: CerebrumError hierarchy (cases, inference, models)
    - specialized: All domain-specific exceptions (IDE, cache, plugins, etc.)

## Public Exports

`exceptions` exports 77 public symbols via `__all__`:

`AIProviderError`, `APIDocumentationError`, `APIError`, `ActiveInferenceError`, `ArtifactError`, `AuthenticationError`, `BayesianInferenceError`, `BuildError`, `BulkheadFullError`, `CICDError`, `CacheError`, `CapabilityScanError`, `CaseError`, `CaseNotFoundError`, `CerebrumError`, `CircuitOpenError`, `CodeEditingError`, `CodeExecutionError`, `CodeGenerationError`, `CodomyrmexError`, `CommandExecutionError`, `CompressionError`, `ConfigurationError`, `ContainerError` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../exceptions/](../../../../exceptions/)
