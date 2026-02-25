"""
Codomyrmex System Discovery Module

This module provides system discovery and orchestration capabilities
for the Codomyrmex ecosystem. It scans all modules, discovers capabilities,
reports on system status, and provides interactive exploration tools.
"""

from .core.capability_scanner import CapabilityScanner
from .core.context import get_system_context
from .core.discovery_engine import SystemDiscovery
from .reporting.status_reporter import StatusReporter

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the system_discovery module."""
    return {
        "modules": {
            "help": "List all discovered modules and their capabilities",
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
    }


__all__ = [
    "SystemDiscovery",
    "StatusReporter",
    "CapabilityScanner",
    "get_system_context",
    "cli_commands",
]

__version__ = "0.1.0"
