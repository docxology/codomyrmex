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
    # AI
    "AIProviderError",
    "APIDocumentationError",
    "APIError",
    "ActiveInferenceError",
    "ArtifactError",
    "AuthenticationError",
    "BayesianInferenceError",
    "BuildError",
    "BulkheadFullError",
    "CICDError",
    "CacheError",
    "CapabilityScanError",
    "CaseError",
    "CaseNotFoundError",
    # CEREBRUM
    "CerebrumError",
    "CircuitOpenError",
    "CodeEditingError",
    # Execution
    "CodeExecutionError",
    "CodeGenerationError",
    # Base
    "CodomyrmexError",
    "CommandExecutionError",
    "CompressionError",
    # Configuration
    "ConfigurationError",
    "ContainerError",
    "DatabaseError",
    "DependencyError",
    "DeploymentError",
    "DirectoryError",
    "DocumentationError",
    "EncryptionError",
    "EnvironmentError",
    "EventError",
    # I/O
    "FileOperationError",
    # Git
    "GitOperationError",
    "IDEConnectionError",
    "IDEError",
    "InferenceError",
    "InteractiveShellError",
    "InvalidCaseError",
    "LoggingError",
    "MemoryError",
    "ModelContextError",
    "ModelError",
    "Modeling3DError",
    # Network/API/Validation
    "NetworkError",
    "NetworkStructureError",
    # Orchestration
    "OrchestrationError",
    "PatternMatchingError",
    # Specialized
    "PerformanceError",
    "PhysicalManagementError",
    "PlottingError",
    "PluginError",
    "ProjectManagementError",
    "RepositoryError",
    "ResourceError",
    "SandboxError",
    "SchemaError",
    "SecurityAuditError",
    "SerializationError",
    "SessionError",
    "SimulationError",
    "SkillError",
    "SpatialError",
    # Analysis
    "StaticAnalysisError",
    "SynthesisError",
    "SystemDiscoveryError",
    "TaskExecutionError",
    "TemplateError",
    "TerminalError",
    "TimeoutError",
    "TransformationError",
    "ValidationError",
    # Visualization/Docs
    "VisualizationError",
    "WorkflowError",
    "create_error_context",
    "format_exception_chain",
]
