"""Codomyrmex - A Modular, Extensible Coding Workspace

This package provides tools and modules for AI-assisted
software development, code analysis, testing, and documentation. It offers
orchestration capabilities, project management, and
seamless integration with modern development workflows.

Key Features:
- AI-powered code generation and editing
- Static analysis and quality checking
- Data visualization and plotting
- Secure code execution in sandboxed environments
- Git operations and repository management
- Project orchestration and workflow automation
- 3D modeling and visualization capabilities
- Physical system simulation and management
- Modular architecture for extensibility

Authors:
    Codomyrmex Contributors

License:
    MIT License (see LICENSE file for details)
"""

__version__ = "0.1.0"
__author__ = "Codomyrmex Contributors"
__email__ = "codomyrmex@example.com"
__license__ = "MIT"

# All available modules in the package
__all__ = [
    # Core modules
    "ai_code_editing",
    "api_documentation",
    "build_synthesis",
    "ci_cd_automation",
    "cli",
    "code_execution_sandbox",
    "code_review",
    "config_management",
    "containerization",
    "data_visualization",
    "database_management",
    "documentation",
    "environment_setup",
    "git_operations",
    "language_models",
    "logging_monitoring",
    "model_context_protocol",
    "module_template",
    "ollama_integration",
    "pattern_matching",
    "performance",
    "project_orchestration",
    "security",
    "documents",
    "static_analysis",
    "system_discovery",
    "terminal_interface",
    "tools",
    # Specialized modules
    "events",
    "api_standardization",
    "plugin_system",
    "template",
    "modeling_3d",
    "physical_management",
    "cerebrum",
]

# Import core exceptions and utilities for easier access
from pathlib import Path
from typing import Any, Optional

from .exceptions import (
    AIProviderError,
    CodeExecutionError,
    CodeGenerationError,
    CodomyrmexError,
    ConfigurationError,
    DependencyError,
    EnvironmentError,
    FileOperationError,
    GitOperationError,
    OrchestrationError,
    StaticAnalysisError,
    VisualizationError,
    create_error_context,
    format_exception_chain,
)


def get_module_path(module_name: str) -> Optional[Path]:
    """Get the path to a specific module."""
    if module_name in __all__:
        return Path(__file__).parent / module_name
    return None


def list_modules() -> list[str]:
    """List all available modules in the package."""
    return list(__all__)


def get_version() -> str:
    """Get the current version of Codomyrmex."""
    return __version__
