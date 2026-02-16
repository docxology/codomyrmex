"""Codomyrmex - A Modular, Extensible Coding Workspace.

This package provides a comprehensive suite of specialized modules organized in a
four-layer architecture for AI-assisted software development, code analysis,
testing, documentation generation, and workflow automation.
"""

__version__ = "0.1.1"

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

def list_modules() -> list[str]:
    """List all available submodules in the package."""
    return [name for _, name, _ in pkgutil.iter_modules([str(get_module_path())])]

# Explicitly export major submodules for easier access
# Use lazy imports to avoid requiring all optional dependencies
_submodules = [
    "accessibility",
    "agentic_memory",
    "agents",
    "api",
    "audio",
    "auth",
    "bio_simulation",
    "build_synthesis",
    "cache",
    "cerebrum",
    "chaos_engineering",
    "ci_cd_automation",
    "cli",
    "cloud",
    "coding",
    "collaboration",
    "compression",
    "concurrency",
    "config_management",
    "containerization",
    "cost_management",
    "dark",
    "data_lineage",
    "data_visualization",
    "database_management",
    "defense",
    "dependency_injection",
    "deployment",
    "documentation",
    "documents",
    "edge_computing",
    "education",
    "embodiment",
    "encryption",
    "environment_setup",
    "events",
    "evolutionary_ai",
    "examples",
    "exceptions",
    "feature_flags",
    "feature_store",
    "finance",
    "fpf",
    "git_operations",
    "governance",
    "graph_rag",
    "i18n",
    "ide",
    "identity",
    "inference_optimization",
    "llm",
    "logging_monitoring",
    "logistics",
    "maintenance",
    "market",
    "metrics",
    "migration",
    "model_context_protocol",
    "model_evaluation",
    "model_ops",
    "model_registry",
    "module_template",
    "multimodal",
    "meme",
    "networking",
    "notification",
    "observability_dashboard",
    "orchestrator",
    "pattern_matching",
    "performance",
    "physical_management",
    "plugin_system",
    "privacy",
    "prompt_engineering",
    "prompt_testing",
    "quantum",
    "rate_limiting",
    "relations",
    "schemas",
    "scheduler",
    "scrape",
    "search",
    "security",
    "serialization",
    "service_mesh",
    "skills",
    "smart_contracts",
    "spatial",
    "static_analysis",
    "streaming",
    "system_discovery",
    "telemetry",
    "templating",
    "terminal_interface",
    "testing",
    "tests",
    "tool_use",
    "utils",
    "validation",
    "vector_store",
    "video",
    "visualization",
    "wallet",
    "website",
    "workflow_testing",
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
    from . import exceptions, utils
except ImportError:
    pass

__all__ = [
    "accessibility",
    "agentic_memory",
    "agents",
    "api",
    "audio",
    "auth",
    "bio_simulation",
    "build_synthesis",
    "cache",
    "cerebrum",
    "chaos_engineering",
    "ci_cd_automation",
    "cli",
    "cloud",
    "coding",
    "collaboration",
    "compression",
    "concurrency",
    "config_management",
    "containerization",
    "cost_management",
    "dark",
    "data_lineage",
    "data_visualization",
    "database_management",
    "defense",
    "dependency_injection",
    "deployment",
    "documentation",
    "documents",
    "edge_computing",
    "education",
    "embodiment",
    "encryption",
    "environment_setup",
    "events",
    "evolutionary_ai",
    "examples",
    "exceptions",
    "feature_flags",
    "feature_store",
    "finance",
    "fpf",
    "git_operations",
    "governance",
    "graph_rag",
    "i18n",
    "ide",
    "identity",
    "inference_optimization",
    "llm",
    "logging_monitoring",
    "logistics",
    "maintenance",
    "market",
    "meme",
    "metrics",
    "migration",
    "model_context_protocol",
    "model_evaluation",
    "model_ops",
    "model_registry",
    "module_template",
    "multimodal",
    "networking",
    "notification",
    "observability_dashboard",
    "orchestrator",
    "pattern_matching",
    "performance",
    "physical_management",
    "plugin_system",
    "privacy",
    "prompt_engineering",
    "prompt_testing",
    "quantum",
    "rate_limiting",
    "relations",
    "scheduler",
    "schemas",
    "scrape",
    "search",
    "security",
    "serialization",
    "service_mesh",
    "skills",
    "smart_contracts",
    "spatial",
    "static_analysis",
    "streaming",
    "system_discovery",
    "telemetry",
    "templating",
    "terminal_interface",
    "testing",
    "tests",
    "tool_use",
    "utils",
    "validation",
    "vector_store",
    "video",
    "visualization",
    "wallet",
    "website",
    "workflow_testing",
    "get_version",
    "get_module_path",
    "list_modules",
]
