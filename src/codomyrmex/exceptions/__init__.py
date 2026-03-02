"""Codomyrmex Exception Classes.

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
"""

from __future__ import annotations

# Base
# AI and Code Generation
from .ai import (
    AIProviderError,
    CodeEditingError,
    CodeGenerationError,
    ModelContextError,
)

# Analysis
from .analysis import (
    PatternMatchingError,
    SecurityAuditError,
    StaticAnalysisError,
)
from .base import (
    CodomyrmexError,
    create_error_context,
    format_exception_chain,
)

# CEREBRUM
from .cerebrum import (
    ActiveInferenceError,
    BayesianInferenceError,
    CaseError,
    CaseNotFoundError,
    CerebrumError,
    InferenceError,
    InvalidCaseError,
    ModelError,
    NetworkStructureError,
    TransformationError,
)

# Configuration and Setup
from .config import (
    ConfigurationError,
    DependencyError,
    EnvironmentError,
)

# Execution and Build
from .execution import (
    BuildError,
    CodeExecutionError,
    ContainerError,
    SandboxError,
    SynthesisError,
)

# Git and Version Control
from .git import (
    GitOperationError,
    RepositoryError,
)

# File and I/O
from .io import (
    DirectoryError,
    FileOperationError,
)

# Network, API, Validation
from .network import (
    APIError,
    NetworkError,
    SchemaError,
    TimeoutError,
    ValidationError,
)

# Orchestration
from .orchestration import (
    OrchestrationError,
    ProjectManagementError,
    TaskExecutionError,
    WorkflowError,
)

# Specialized Domain Exceptions
from .specialized import (
    ArtifactError,
    AuthenticationError,
    BulkheadFullError,
    CacheError,
    CapabilityScanError,
    CICDError,
    CircuitOpenError,
    CommandExecutionError,
    CompressionError,
    DatabaseError,
    DeploymentError,
    EncryptionError,
    EventError,
    IDEConnectionError,
    IDEError,
    InteractiveShellError,
    LoggingError,
    MemoryError,
    Modeling3DError,
    PerformanceError,
    PhysicalManagementError,
    PluginError,
    ResourceError,
    SerializationError,
    SessionError,
    SimulationError,
    SkillError,
    SpatialError,
    SystemDiscoveryError,
    TemplateError,
    TerminalError,
)

# Visualization and Documentation
from .viz import (
    APIDocumentationError,
    DocumentationError,
    PlottingError,
    VisualizationError,
)

__all__ = [
    # Base
    "CodomyrmexError",
    "format_exception_chain",
    "create_error_context",
    # Configuration
    "ConfigurationError",
    "EnvironmentError",
    "DependencyError",
    # I/O
    "FileOperationError",
    "DirectoryError",
    # AI
    "AIProviderError",
    "CodeGenerationError",
    "CodeEditingError",
    "ModelContextError",
    # Analysis
    "StaticAnalysisError",
    "PatternMatchingError",
    "SecurityAuditError",
    # Execution
    "CodeExecutionError",
    "SandboxError",
    "ContainerError",
    "BuildError",
    "SynthesisError",
    # Git
    "GitOperationError",
    "RepositoryError",
    # Visualization/Docs
    "VisualizationError",
    "PlottingError",
    "DocumentationError",
    "APIDocumentationError",
    # Orchestration
    "OrchestrationError",
    "WorkflowError",
    "ProjectManagementError",
    "TaskExecutionError",
    # Network/API/Validation
    "NetworkError",
    "APIError",
    "ValidationError",
    "SchemaError",
    "TimeoutError",
    # CEREBRUM
    "CerebrumError",
    "CaseError",
    "BayesianInferenceError",
    "ActiveInferenceError",
    "ModelError",
    "TransformationError",
    "CaseNotFoundError",
    "InvalidCaseError",
    "InferenceError",
    "NetworkStructureError",
    # Specialized
    "PerformanceError",
    "LoggingError",
    "SystemDiscoveryError",
    "CapabilityScanError",
    "Modeling3DError",
    "PhysicalManagementError",
    "SimulationError",
    "TerminalError",
    "InteractiveShellError",
    "DatabaseError",
    "CICDError",
    "DeploymentError",
    "ResourceError",
    "MemoryError",
    "SpatialError",
    "EventError",
    "SkillError",
    "TemplateError",
    "PluginError",
    "AuthenticationError",
    "CircuitOpenError",
    "BulkheadFullError",
    "CompressionError",
    "EncryptionError",
    "IDEError",
    "IDEConnectionError",
    "CommandExecutionError",
    "SessionError",
    "ArtifactError",
    "CacheError",
    "SerializationError",
]
