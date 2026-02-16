"""Core discovery components for the system_discovery module.

Contains the discovery engine, capability scanner, and system context
aggregation logic.
"""

from .capability_scanner import (
    CapabilityScanner,
    ClassCapability,
    FunctionCapability,
    ModuleCapability,
)
from .context import get_system_context
from .discovery_engine import ModuleCapability as EngineModuleCapability
from .discovery_engine import ModuleInfo, SystemDiscovery

__all__ = [
    "SystemDiscovery",
    "ModuleInfo",
    "CapabilityScanner",
    "FunctionCapability",
    "ClassCapability",
    "ModuleCapability",
    "EngineModuleCapability",
    "get_system_context",
]
