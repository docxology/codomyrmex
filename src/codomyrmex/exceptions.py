from pathlib import Path
from typing import Any, Optional, Union

# from codomyrmex.logging_monitoring import get_logger


"""Codomyrmex Exception Classes

Core functionality module

This module provides exceptions functionality including:
    pass 
- 9 functions: format_exception_chain, create_error_context, __init__...
- 48 classes: CodomyrmexError, ConfigurationError, EnvironmentError...

Usage:
    pass 
    # Example usage here

This module defines all the exception classes used throughout the Codomyrmex
package. It provides a hierarchical structure of exceptions to handle various
error conditions that can occur during code generation, analysis, execution,
and other operations.

Exception Hierarchy:
    All exceptions inherit from CodomyrmexError, which provides:
        pass 
    - Context dictionaries for additional error information
    - Error codes for programmatic handling
    - Serialization to dictionaries
    - Exception chaining support

    CodomyrmexError (base)
    ├── ConfigurationError - Configuration-related errors
    ├── EnvironmentError - Environment setup errors
    ├── DependencyError - Missing or incompatible dependencies
    ├── FileOperationError - File I/O errors
    ├── AIProviderError - AI provider errors
    ├── CodeGenerationError - Code generation failures
    ├── CodeExecutionError - Code execution failures
    ├── StaticAnalysisError - Static analysis errors
    ├── GitOperationError - Git operation errors
    ├── OrchestrationError - Workflow orchestration errors
    ├── VisualizationError - Visualization errors
    └── ... (30+ exception types)

Exception Categories:
    1. Configuration and Setup Errors:
       - ConfigurationError: Configuration issues
       - EnvironmentError: Environment not properly set up
       - DependencyError: Missing or incompatible dependencies

    2. File and I/O Errors:
       - FileOperationError: File operations failed
       - DirectoryError: Directory operations failed

    3. AI and Code Generation Errors:
       - AIProviderError: AI provider operations failed
       - CodeGenerationError: Code generation failed
       - CodeEditingError: Code editing operations failed
       - ModelContextError: MCP operations failed

    4. Analysis Errors:
       - StaticAnalysisError: Static analysis operations failed
       - PatternMatchingError: Pattern matching operations failed
       - SecurityAuditError: Security audit operations failed

    5. Execution Errors:
       - CodeExecutionError: Code execution failed
       - SandboxError: Sandbox operations failed
       - ContainerError: Container operations failed

    6. Build and Synthesis Errors:
       - BuildError: Build operations failed
       - SynthesisError: Code synthesis operations failed

    7. Git and Version Control Errors:
       - GitOperationError: Git operations failed
       - RepositoryError: Repository operations failed

    8. Visualization Errors:
       - VisualizationError: Data visualization operations failed
       - PlottingError: Plotting operations failed

    9. Documentation Errors:
       - DocumentationError: Documentation operations failed
       - APIDocumentationError: API documentation generation failed

    10. Orchestration Errors:
        - OrchestrationError: Orchestration operations failed
        - WorkflowError: Workflow execution failed
        - ProjectManagementError: Project management operations failed
        - TaskExecutionError: Task execution failed

Usage Guidelines:
    All modules should use exceptions from this module:
        pass 

    ```python

    try:
        # Code execution
        result = execute_code(code)
    except CodeExecutionError as e:
        # Handle execution error
        logger.error(f"Execution failed: {e}")
        # Access context
        exit_code = e.context.get("exit_code")
    except CodomyrmexError as e:
        # Handle any Codomyrmex error
        logger.error(f"Error: {e}")
    ```

Error Context:
    All exceptions support context dictionaries for additional information:
        pass 

    ```python

    raise CodeExecutionError(
        "Code execution failed",
        context=create_error_context(
            exit_code=1,
            stdout="...",
            stderr="Error message"
        )
    )
    ```

Exception Utilities:
    - format_exception_chain(): Format exception chain for display
    - create_error_context(): Create context dictionary for exceptions

The exception hierarchy is designed to be specific enough for proper error
handling while remaining consistent across all modules.
"""



class CodomyrmexError(Exception):
    """Base exception class for all Codomyrmex-related errors.

    This is the root exception class that all other Codomyrmex exceptions
    inherit from. It provides a consistent interface and additional context
    information for error handling.

    Attributes:
        message (str): The error message
        context (Dict[str, Any]): Additional context information about the error
        error_code (str): A unique error code for this exception type
    """

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        error_code: Optional[str] = None,
        **kwargs: Any,
    ):

        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.context.update(kwargs)
        self.error_code = error_code or self.__class__.__name__

    def __str__(self) -> str:
        """Return a string representation of the error."""
        base_msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        return base_msg

    def to_dict(self) -> dict[str, Any]:
        """Convert the exception to a dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


# Configuration and Setup Errors
class ConfigurationError(CodomyrmexError):
    """Raised when there's an issue with configuration settings."""

    pass


class EnvironmentError(CodomyrmexError):
    """Raised when the environment is not properly set up."""

    pass


class DependencyError(CodomyrmexError):
    """Raised when a required dependency is missing or incompatible."""

    pass


# File and I/O Errors
class FileOperationError(CodomyrmexError):
    """Raised when file operations fail."""

    def __init__(
        self, message: str, file_path: Optional[Union[str, Path]] = None, **kwargs: Any
    ) -> None:

        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = str(file_path)


class DirectoryError(CodomyrmexError):
    """Raised when directory operations fail."""

    pass


# AI and Code Generation Errors
class AIProviderError(CodomyrmexError):
    """Raised when AI provider operations fail."""

    pass


class CodeGenerationError(CodomyrmexError):
    """Raised when code generation fails."""

    pass


class CodeEditingError(CodomyrmexError):
    """Raised when code editing operations fail."""

    pass


class ModelContextError(CodomyrmexError):
    """Raised when model context protocol operations fail."""

    pass


# Analysis Errors
class StaticAnalysisError(CodomyrmexError):
    """Raised when static analysis operations fail."""

    pass


class PatternMatchingError(CodomyrmexError):
    """Raised when pattern matching operations fail."""

    pass


class SecurityAuditError(CodomyrmexError):
    """Raised when security audit operations fail."""

    pass


# Execution Errors
class CodeExecutionError(CodomyrmexError):
    """Raised when code execution fails."""

    def __init__(
        self,
        message: str,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        **kwargs: Any,
    ) -> None:

        super().__init__(message, **kwargs)
        if exit_code is not None:
            self.context["exit_code"] = exit_code
        if stdout:
            self.context["stdout"] = stdout
        if stderr:
            self.context["stderr"] = stderr


class SandboxError(CodomyrmexError):
    """Raised when sandbox operations fail."""

    pass


class ContainerError(CodomyrmexError):
    """Raised when container operations fail."""

    pass


# Build and Synthesis Errors
class BuildError(CodomyrmexError):
    """Raised when build operations fail."""

    pass


class SynthesisError(CodomyrmexError):
    """Raised when code synthesis operations fail."""

    pass


# Git and Version Control Errors
class GitOperationError(CodomyrmexError):
    """Raised when git operations fail."""

    def __init__(
        self,
        message: str,
        git_command: Optional[str] = None,
        repository_path: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ) -> None:

        super().__init__(message, **kwargs)
        if git_command:
            self.context["git_command"] = git_command
        if repository_path:
            self.context["repository_path"] = str(repository_path)


class RepositoryError(CodomyrmexError):
    """Raised when repository operations fail."""

    pass


# Visualization Errors
class VisualizationError(CodomyrmexError):
    """Raised when data visualization operations fail."""

    pass


class PlottingError(CodomyrmexError):
    """Raised when plotting operations fail."""

    pass


# Documentation Errors
class DocumentationError(CodomyrmexError):
    """Raised when documentation operations fail."""

    pass


class APIDocumentationError(CodomyrmexError):
    """Raised when API documentation generation fails."""

    pass


# Orchestration and Project Management Errors
class OrchestrationError(CodomyrmexError):
    """Raised when orchestration operations fail."""

    pass


class WorkflowError(CodomyrmexError):
    """Raised when workflow execution fails."""

    pass


class ProjectManagementError(CodomyrmexError):
    """Raised when project management operations fail."""

    pass


class TaskExecutionError(CodomyrmexError):
    """Raised when task execution fails."""

    pass


# Performance and Monitoring Errors
class PerformanceError(CodomyrmexError):
    """Raised when performance monitoring operations fail."""

    pass


class LoggingError(CodomyrmexError):
    """Raised when logging operations fail."""

    pass


# System Discovery Errors
class SystemDiscoveryError(CodomyrmexError):
    """Raised when system discovery operations fail."""

    pass


class CapabilityScanError(CodomyrmexError):
    """Raised when capability scanning fails."""

    pass


# 3D Modeling and Physical Management Errors
class Modeling3DError(CodomyrmexError):
    """Raised when 3D modeling operations fail."""

    pass


class PhysicalManagementError(CodomyrmexError):
    """Raised when physical management operations fail."""

    pass


class SimulationError(CodomyrmexError):
    """Raised when simulation operations fail."""

    pass


# Terminal and Interface Errors
class TerminalError(CodomyrmexError):
    """Raised when terminal interface operations fail."""

    pass


class InteractiveShellError(CodomyrmexError):
    """Raised when interactive shell operations fail."""

    pass


# Database Errors
class DatabaseError(CodomyrmexError):
    """Raised when database operations fail."""

    pass


# CI/CD Errors
class CICDError(CodomyrmexError):
    """Raised when CI/CD operations fail."""

    pass


class DeploymentError(CodomyrmexError):
    """Raised when deployment operations fail."""

    pass


# Validation Errors
class ValidationError(CodomyrmexError):
    """Raised when data validation fails."""

    pass


class SchemaError(CodomyrmexError):
    """Raised when schema validation fails."""

    pass


# Network and API Errors
class NetworkError(CodomyrmexError):
    """Raised when network operations fail."""

    pass


class APIError(CodomyrmexError):
    """Raised when API operations fail."""

    pass


# Timeout Errors
class TimeoutError(CodomyrmexError):
    """Raised when operations timeout."""

    def __init__(
        self, message: str, timeout_seconds: Optional[float] = None, **kwargs: Any
    ) -> None:

        super().__init__(message, **kwargs)
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds


# Resource Errors
class ResourceError(CodomyrmexError):
    """Raised when resource operations fail."""

    pass


class MemoryError(CodomyrmexError):
    """Raised when memory-related errors occur."""

    pass


# Spatial Errors
class SpatialError(CodomyrmexError):
    """Raised when spatial operations fail."""
    pass


# Cerebrum Errors
class CerebrumError(CodomyrmexError):
    """Raised when cognitive processing fails."""
    pass


# Event Errors
class EventError(CodomyrmexError):
    """Raised when event processing fails."""
    pass


# Skill Errors
class SkillError(CodomyrmexError):
    """Raised when skill execution fails."""
    pass


# Template Errors
class TemplateError(CodomyrmexError):
    """Raised when template operations fail."""

    pass


# Utility functions for exception handling
def format_exception_chain(exception: Exception) -> str:
    """Format an exception chain for display.

    Args:
        exception: The exception to format

    Returns:
        A formatted string representation of the exception chain
    """
    lines = []
    current: Optional[BaseException] = exception

    while current:
        if isinstance(current, CodomyrmexError):
            lines.append(str(current))
        else:
            lines.append(f"[{current.__class__.__name__}] {str(current)}")
        current = current.__cause__ or current.__context__

    return "\n".join(lines)


def create_error_context(**kwargs: Any) -> dict[str, Any]:
    """Create a context dictionary for exception handling.

    Args:
        **kwargs: Context key-value pairs

    Returns:
        A dictionary suitable for use as exception context
    """
    return {k: v for k, v in kwargs.items() if v is not None}
