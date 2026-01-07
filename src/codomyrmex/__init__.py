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
    # Foundation Layer
    "logging_monitoring",
    "environment_setup",
    "model_context_protocol",
    "terminal_interface",
    # Core Layer
    "static_analysis",
    "code",
    "data_visualization",
    "pattern_matching",
    "git_operations",
    "scrape",
    "security",
    "documents",
    "llm",
    "performance",
    # Service Layer
    "build_synthesis",
    "documentation",
    "api",
    "ci_cd_automation",
    "containerization",
    "database_management",
    "config_management",
    "logistics",
    # Specialized Layer
    "spatial",
    "physical_management",
    "system_discovery",
    "module_template",
    "template",
    "events",
    "plugin_system",
    "utils",
    "validation",
    "website",
    "cerebrum",
    "agents",
    # Infrastructure
    "tests",
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
    # Handle nested modules like llm.ollama
    if module_name == "llm.ollama" or module_name.startswith("llm."):
        return Path(__file__).parent / "llm"
    return None


def list_modules() -> list[str]:
    """List all available modules in the package."""
    return list(__all__)


def get_version() -> str:
    """Get the current version of Codomyrmex."""
    return __version__
