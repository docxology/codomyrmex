"""Codomyrmex Source Code Package

This package serves as the root namespace for all Codomyrmex source code components,
providing unified access to the main codomyrmex package and template system.

The Codomyrmex project is a modular, extensible coding workspace that integrates
cutting-edge tools for AI-assisted development, code analysis, testing, and documentation.

Key Components:
- codomyrmex/: Main package with all core modules and functionality
- template/: Project templates and boilerplate code for rapid development

For detailed documentation, see:
- README.md: Source code structure and navigation
- codomyrmex/README.md: Main package documentation
- template/README.md: Template system documentation

Authors:
    Codomyrmex Contributors

License:
    MIT License (see LICENSE file for details)
"""

__version__ = "0.1.0"
__author__ = "Codomyrmex Contributors"
__email__ = "codomyrmex@example.com"
__license__ = "MIT"

# Import main package for easy access
from codomyrmex import (
    get_module_path,
    list_modules,
)

# Re-export key functionality from main package
from codomyrmex import (
    get_version as get_codomyrmex_version,
)

# Re-export common exceptions for convenience
from codomyrmex.exceptions import (
    CodeExecutionError,
    CodeGenerationError,
    CodomyrmexError,
    ConfigurationError,
    EnvironmentError,
    StaticAnalysisError,
)

from . import codomyrmex, template


def get_source_version() -> str:
    """Get the current version of the Codomyrmex source package."""
    return __version__


def get_main_package_info() -> dict:
    """Get information about the main codomyrmex package."""
    return {
        "name": "codomyrmex",
        "version": codomyrmex.__version__,
        "modules": codomyrmex.list_modules(),
        "description": "Core Codomyrmex functionality and modules"
    }


def get_template_info() -> dict:
    """Get information about the template system."""
    return {
        "name": "template",
        "description": "Project templates and boilerplate code",
        "components": ["AGENTS.md", "AGENTS_ROOT_TEMPLATE.md", "AGENTS_TEMPLATE.md", "README.md"]
    }


__all__ = [
    # Main components
    "codomyrmex",
    "template",
    # Re-exported functions
    "get_codomyrmex_version",
    "list_modules",
    "get_module_path",
    "get_source_version",
    "get_main_package_info",
    "get_template_info",
    # Common exceptions
    "CodomyrmexError",
    "CodeExecutionError",
    "CodeGenerationError",
    "ConfigurationError",
    "EnvironmentError",
    "StaticAnalysisError",
]
