"""Codomyrmex Source Code Package

This package serves as the root namespace for all Codomyrmex source code components,
providing unified access to the main codomyrmex package and template system.

Package Structure:
    The src/ directory contains:
    - codomyrmex/: Main Python package with 89 specialized modules
    - __init__.py: Package initialization and re-exports

    The codomyrmex package is organized in a four-layer architecture:
    - Foundation Layer: Core infrastructure (logging, environment, MCP, terminal, config, metrics)
    - Core Layer: Primary functionality (coding, analysis, visualization, git, security, LLM)
    - Service Layer: Higher-level services (build, docs, API, CI/CD, containers, databases, orchestration)
    - Specialized Layer: Advanced features (spatial, cerebrum, FPF, agents, events, plugins)

Quick Start:
    Import and use the codomyrmex package:

    ```python
    from codomyrmex import get_module_path, list_modules, get_version
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    from codomyrmex.coding import execute_code

    # Initialize logging
    setup_logging()
    logger = get_logger(__name__)

    # List available modules
    modules = list_modules()
    logger.info(f"Available modules: {len(modules)}")

    # Execute code
    result = execute_code(code="print('Hello')", language="python")
    ```

Key Components:
    - codomyrmex: Main package with all functional modules
    - codomyrmex.module_template: Project templates and boilerplate code
    - codomyrmex.cli: Command-line interface
    - codomyrmex.exceptions: Unified exception hierarchy

Documentation:
    - README.md: Source code structure and navigation
    - AGENTS.md: Technical documentation
    - SPEC.md: Functional specification
    - codomyrmex/README.md: Main package documentation
    - codomyrmex/AGENTS.md: Package technical specifications
    - codomyrmex/SPEC.md: Package functional specification

The Codomyrmex project is a modular, extensible coding workspace that integrates
cutting-edge tools for AI-assisted development, code analysis, testing, and documentation.

Authors:
    Codomyrmex Contributors

License:
    MIT License (see LICENSE file for details)
"""

__version__ = "1.0.0"
__author__ = "Codomyrmex Contributors"
__email__ = "codomyrmex@example.com"
__license__ = "MIT"

# Import main package for easy access (guarded for environments where
# the package is not pip-installed, e.g. pytest discovery with PYTHONPATH)
try:
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

    from . import codomyrmex
except (ImportError, ModuleNotFoundError):
    get_module_path = None
    list_modules = None
    get_codomyrmex_version = None
    CodeExecutionError = None
    CodeGenerationError = None
    CodomyrmexError = None
    ConfigurationError = None
    EnvironmentError = None
    StaticAnalysisError = None
    codomyrmex = None


def get_source_version() -> str:
    """Get the current version of the Codomyrmex source package.

    Returns:
        Version string (e.g., "0.1.0").

    Example:
        >>> from src import get_source_version
        >>> version = get_source_version()
        >>> print(version)
        '0.1.0'
    """
    return __version__


def get_main_package_info() -> dict:
    """Get information about the main codomyrmex package.

    Returns:
        Dictionary with package information including name, version, modules, and description.

    Example:
        >>> from src import get_main_package_info
        >>> info = get_main_package_info()
        >>> print(f"Package: {info['name']}, Version: {info['version']}")
        Package: codomyrmex, Version: 0.1.0
    """
    return {
        "name": "codomyrmex",
        "version": codomyrmex.__version__,
        "modules": codomyrmex.list_modules(),
        "description": "Core Codomyrmex functionality and modules"
    }


def get_template_info() -> dict:
    """Get information about the template system.

    Returns:
        Dictionary with template system information including name, description, location, and components.

    Example:
        >>> from src import get_template_info
        >>> info = get_template_info()
        >>> print(f"Template: {info['name']}, Location: {info['location']}")
        Template: module_template, Location: codomyrmex/module_template/
    """
    return {
        "name": "module_template",
        "description": "Project templates and boilerplate code",
        "location": "codomyrmex/module_template/",
        "components": ["AGENTS.md", "README.md", "SPEC.md", "docs/"]
    }


__all__ = [
    # Main components
    "codomyrmex",
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
