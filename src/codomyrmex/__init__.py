"""Codomyrmex - A Modular, Extensible Coding Workspace.

This package provides a comprehensive suite of specialized modules organized in a 
four-layer architecture for AI-assisted software development, code analysis, 
testing, documentation generation, and workflow automation.
"""

__version__ = "0.1.0"

import os
import pkgutil
from pathlib import Path
from typing import List

def get_version() -> str:
    """Get the package version."""
    return __version__

def get_module_path() -> Path:
    """Get the absolute path to the package directory."""
    return Path(__file__).parent

def list_modules() -> List[str]:
    """List all available submodules in the package."""
    return [name for _, name, _ in pkgutil.iter_modules([str(get_module_path())])]

# Explicitly export major submodules for easier access
# Use lazy imports to avoid requiring all optional dependencies
_submodules = [
    "agents",
    "api",
    "auth",
    "build_synthesis",
    "cache",
    "cerebrum",
    "ci_cd_automation",
    "cli",
    "cloud",
    "coding",
    "compression",
    "config_management",
    "containerization",
    "data_visualization",
    "database_management",
    "documentation",
    "documents",
    "encryption",
    "environment_setup",
    "events",
    "examples",
    "exceptions",
    "fpf",
    "git_operations",
    "ide",
    "llm",
    "logging_monitoring",
    "logistics",
    "metrics",
    "model_context_protocol",
    "module_template",
    "networking",
    "orchestrator",
    "pattern_matching",
    "performance",
    "physical_management",
    "plugin_system",
    "scrape",
    "security",
    "serialization",
    "skills",
    "spatial",
    "static_analysis",
    "system_discovery",
    "templating",
    "terminal_interface",
    "tests",
    "tools",
    "utils",
    "validation",
    "website",
]

# Import submodules lazily with error handling
def __getattr__(name):
    """Lazy import submodules on first access."""
    if name in _submodules:
        import importlib
        try:
            module = importlib.import_module(f".{name}", __package__)
            globals()[name] = module
            return module
        except ImportError as e:
            raise ImportError(f"Failed to import {name}: {e}. You may need to install optional dependencies.")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# For backwards compatibility, still try to import core modules that don't have optional deps
# These are the "always available" modules
try:
    from . import exceptions
    from . import utils
except ImportError:
    pass

__all__ = [
    "agents",
    "api",
    "auth",
    "build_synthesis",
    "cache",
    "cerebrum",
    "ci_cd_automation",
    "cli",
    "cloud",
    "coding",
    "compression",
    "config_management",
    "containerization",
    "data_visualization",
    "database_management",
    "documentation",
    "documents",
    "encryption",
    "environment_setup",
    "events",
    "examples",
    "exceptions",
    "fpf",
    "git_operations",
    "ide",
    "llm",
    "logging_monitoring",
    "logistics",
    "metrics",
    "model_context_protocol",
    "module_template",
    "networking",
    "orchestrator",
    "pattern_matching",
    "performance",
    "physical_management",
    "plugin_system",
    "scrape",
    "security",
    "serialization",
    "skills",
    "spatial",
    "static_analysis",
    "system_discovery",
    "templating",
    "terminal_interface",
    "tests",
    "tools",
    "utils",
    "validation",
    "website",
    "get_version",
    "get_module_path",
    "list_modules",
]
