"""Codomyrmex - A Modular, Extensible Coding Workspace

This package provides a comprehensive suite of 30+ specialized modules organized
in a four-layer architecture for AI-assisted software development, code analysis,
testing, documentation generation, and workflow automation.

Package Overview:
    The codomyrmex package serves as the central coordination point for all
    Codomyrmex functionality. It provides modular, self-contained modules with
    clear boundaries and minimal dependencies, enabling independent development
    and testing while maintaining composability.

Module Organization:
    The package is organized into four architectural layers:

    Foundation Layer:
        Core infrastructure modules providing essential services:
        - logging_monitoring: Structured logging with JSON output
        - environment_setup: Environment validation and dependency checking
        - model_context_protocol: MCP tool specifications and protocol handling
        - terminal_interface: Interactive CLI and terminal utilities
        - config_management: Configuration loading, validation, and secrets
        - metrics: Metrics collection and aggregation

    Core Layer:
        Primary functionality modules for code analysis and execution:
        - static_analysis: Code quality analysis and linting
        - coding: Secure code execution and sandboxing
        - data_visualization: Charts, plots, and visualizations
        - pattern_matching: Code pattern recognition and AST analysis
        - git_operations: Git workflow automation
        - security: Security scanning and vulnerability detection
        - llm: LLM infrastructure and model management
        - performance: Performance monitoring and profiling
        - cache, compression, encryption, networking, serialization
        - scrape, documents: Web scraping and document processing

    Service Layer:
        Higher-level services building upon core functionality:
        - build_synthesis: Build automation and code synthesis
        - documentation: Documentation generation tools
        - api: API infrastructure and OpenAPI generation
        - ci_cd_automation: CI/CD pipeline management
        - containerization: Docker and container orchestration
        - database_management: Database operations and migrations
        - logistics: Workflow orchestration and task scheduling
        - auth: Authentication and authorization
        - cloud: Cloud service integrations

    Specialized Layer:
        Advanced features and specialized capabilities:
        - spatial: 3D/4D spatial modeling and visualization
        - cerebrum: Case-based reasoning and Bayesian inference
        - fpf: First Principles Framework integration
        - agents: AI agent integrations (Claude, Codex, Jules, etc.)
        - events: Event system and pub/sub
        - plugin_system: Plugin architecture
        - system_discovery: System introspection and capability mapping
        - physical_management: Physical system simulation
        - module_template: Module creation templates
        - tools, utils, validation, website, templating, skills, ide

Quick Start:
    Basic usage example:

    ```python
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    from codomyrmex.coding import execute_code
    from codomyrmex.static_analysis import analyze_project

    # Initialize logging
    setup_logging()
    logger = get_logger(__name__)

    # Analyze code quality
    analysis = analyze_project("src/")
    logger.info(f"Code quality score: {analysis.get('score', 'N/A')}")

    # Execute code safely
    result = execute_code(code="print('Hello, Codomyrmex!')", language="python")
    logger.info(f"Execution result: {result.get('output', '')}")
    ```

    Using AI agents:

    ```python
    from codomyrmex.agents import AgentRequest
    from codomyrmex.agents.claude import ClaudeClient

    client = ClaudeClient()
    request = AgentRequest(prompt="Generate a Python function")
    response = client.execute(request)
    ```

    Workflow orchestration:

    ```python
    from codomyrmex.logistics.orchestration.project import get_orchestration_engine

    engine = get_orchestration_engine()
    result = engine.execute_workflow("code-analysis", context={"path": "src/"})
    ```

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

Documentation:
    - README.md: User-facing documentation and overview
    - AGENTS.md: Technical documentation and API reference
    - SPEC.md: Functional specification and architecture
    - cli.py: Command-line interface documentation
    - exceptions.py: Exception hierarchy reference

    See individual module README files for specific usage examples.

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
    "config_management",
    "metrics",
    # Core Layer
    "static_analysis",
    "coding",
    "data_visualization",
    "pattern_matching",
    "git_operations",
    "scrape",
    "security",
    "documents",
    "llm",
    "performance",
    "cache",
    "compression",
    "encryption",
    "networking",
    "serialization",
    # Service Layer
    "build_synthesis",
    "documentation",
    "api",
    "ci_cd_automation",
    "containerization",
    "database_management",
    "logistics",
    "cloud",
    "auth",
    # Specialized Layer
    "spatial",
    "physical_management",
    "system_discovery",
    "module_template",
    "cerebrum",
    "fpf",
    "events",
    "plugin_system",
    "tools",
    "utils",
    "validation",
    "website",
    "templating",
    "agents",
    "skills",
    "ide",
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
    """Get the path to a specific module.

    This function returns the filesystem path to a module directory, allowing
    programmatic access to module resources and files.

    Args:
        module_name: Name of the module (e.g., "coding", "llm.ollama").
                     Can be a top-level module or nested module.

    Returns:
        Path to the module directory if found, None otherwise.

    Example:
        >>> from codomyrmex import get_module_path
        >>> path = get_module_path("coding")
        >>> print(path)
        PosixPath('/path/to/src/codomyrmex/coding')

        >>> path = get_module_path("llm.ollama")
        >>> print(path)
        PosixPath('/path/to/src/codomyrmex/llm')
    """
    if module_name in __all__:
        return Path(__file__).parent / module_name
    # Handle nested modules like llm.ollama
    if module_name == "llm.ollama" or module_name.startswith("llm."):
        return Path(__file__).parent / "llm"
    return None


def list_modules() -> list[str]:
    """List all available modules in the package.

    Returns a list of all module names organized by architectural layer.
    Modules are listed in the order: Foundation, Core, Service, Specialized.

    Returns:
        List of module names as strings.

    Example:
        >>> from codomyrmex import list_modules
        >>> modules = list_modules()
        >>> print(f"Total modules: {len(modules)}")
        Total modules: 30+
        >>> print(modules[:5])
        ['logging_monitoring', 'environment_setup', 'model_context_protocol', ...]
    """
    return list(__all__)


def get_version() -> str:
    """Get the current version of Codomyrmex.

    Returns the semantic version string for the package.

    Returns:
        Version string in the format "MAJOR.MINOR.PATCH".

    Example:
        >>> from codomyrmex import get_version
        >>> version = get_version()
        >>> print(version)
        '0.1.0'
    """
    return __version__
