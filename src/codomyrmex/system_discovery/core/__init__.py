"""Core discovery components for the system_discovery module.

Contains the discovery engine, capability scanner, system context
aggregation logic, dependency analysis, and health checking.
"""

from .capability_scanner import (
    CapabilityScanner,
    ClassCapability,
    FunctionCapability,
    ModuleCapability,
)
from .context import get_system_context
from .dependency_analyzer import DependencyAnalyzer
from .discovery_engine import ModuleCapability as EngineModuleCapability
from .discovery_engine import ModuleInfo, SystemDiscovery
from .health_checker import SystemHealthChecker

__all__ = [
    "SystemDiscovery",
    "ModuleInfo",
    "CapabilityScanner",
    "FunctionCapability",
    "ClassCapability",
    "ModuleCapability",
    "EngineModuleCapability",
    "DependencyAnalyzer",
    "SystemHealthChecker",
    "get_system_context",
]
