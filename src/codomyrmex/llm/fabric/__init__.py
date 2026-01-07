"""
Codomyrmex Fabric Integration Module

This module provides integration with Fabric AI framework,
enabling pattern-based AI workflows and orchestration within
the Codomyrmex ecosystem.
"""

from .fabric_config_manager import FabricConfigManager
from .fabric_manager import FabricManager
from .fabric_orchestrator import FabricOrchestrator

__all__ = [
    'FabricManager',
    'FabricOrchestrator',
    'FabricConfigManager'
]

__version__ = '1.0.0'

