"""
Codomyrmex System Discovery Module

This module provides comprehensive system discovery and orchestration capabilities
for the Codomyrmex ecosystem. It scans all modules, discovers capabilities,
reports on system status, and provides interactive exploration tools.
"""

from .discovery_engine import SystemDiscovery
from .status_reporter import StatusReporter
from .capability_scanner import CapabilityScanner

__all__ = [
    'SystemDiscovery',
    'StatusReporter', 
    'CapabilityScanner'
]

__version__ = "0.1.0"
