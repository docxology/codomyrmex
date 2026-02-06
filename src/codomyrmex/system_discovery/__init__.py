"""
Codomyrmex System Discovery Module

This module provides system discovery and orchestration capabilities
for the Codomyrmex ecosystem. It scans all modules, discovers capabilities,
reports on system status, and provides interactive exploration tools.
"""

from .capability_scanner import CapabilityScanner
from .context import get_system_context
from .discovery_engine import SystemDiscovery
from .status_reporter import StatusReporter

__all__ = ["SystemDiscovery", "StatusReporter", "CapabilityScanner", "get_system_context"]

__version__ = "0.1.0"
