"""
Codomyrmex System Discovery Module

This module provides system discovery and orchestration capabilities
for the Codomyrmex ecosystem. It scans all modules, discovers capabilities,
reports on system status, and provides interactive exploration tools.
"""

import contextlib

from .core.capability_scanner import CapabilityScanner
from .core.context import get_system_context
from .core.discovery_engine import SystemDiscovery
from .health.health_checker import HealthChecker
from .module_catalog import ModuleCatalog, ModuleCatalogEntry, build_module_catalog
from .reporting.status_reporter import StatusReporter
from .structure_audit import (
    ModuleStructureAudit,
    StructureIssue,
    audit_module_structure,
)

# Shared schemas for cross-module interop
with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus


def cli_commands():
    """Return CLI commands for the system_discovery module."""
    return {
        "modules": {
            "help": "list all discovered modules and their capabilities",
            "handler": lambda **kwargs: print(
                f"System context: {type(get_system_context()).__name__}\n"
                f"Discovery engine: {SystemDiscovery.__name__}\n"
                f"Capability scanner: {CapabilityScanner.__name__}\n"
                f"Status reporter: {StatusReporter.__name__}"
            ),
        },
        "health": {
            "help": "Show system health status across all modules",
            "handler": lambda **kwargs: print(
                "System Health Check:\n"
                "  Discovery engine: available\n"
                "  Capability scanner: available\n"
                "  Status reporter: available\n"
                "  System context: available"
            ),
        },
        "catalog": {
            "help": "Show top-level source module catalog counts and parity gaps",
            "handler": lambda **kwargs: _print_module_catalog(),
        },
        "structure": {
            "help": "Run the read-only source module structure audit",
            "handler": lambda **kwargs: print(audit_module_structure().to_markdown()),
        },
    }


def _print_module_catalog() -> None:
    """Print a concise top-level source module catalog summary."""
    catalog = build_module_catalog()
    print(
        "\n".join(
            [
                f"Runtime modules: {catalog.runtime_module_count}",
                f"Support surfaces: {catalog.support_surface_count}",
                f"Docs module directories: {catalog.docs_module_count}",
                f"API specification gaps: {len(catalog.api_spec_missing)}",
                f"MCP specification gaps: {len(catalog.mcp_tool_modules_missing_specs)}",
                f"Docs module gaps: {len(catalog.docs_module_missing)}",
                "Orphaned docs modules: "
                f"{len(catalog.docs_modules_without_source_entries)}",
                f"py.typed gaps: {len(catalog.py_typed_missing)}",
            ]
        )
    )


__all__ = [
    "CapabilityScanner",
    "HealthChecker",
    "ModuleCatalog",
    "ModuleCatalogEntry",
    "ModuleStructureAudit",
    "StatusReporter",
    "StructureIssue",
    "SystemDiscovery",
    "audit_module_structure",
    "build_module_catalog",
    "cli_commands",
    "get_system_context",
]

__version__ = "0.1.0"
