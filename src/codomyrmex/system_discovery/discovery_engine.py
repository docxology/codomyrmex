# DEPRECATED(v0.2.0): Shim module. Import from system_discovery.core.discovery_engine instead. Will be removed in v0.3.0.
"""Backward-compatible re-export from system_discovery.core.discovery_engine."""
from .core.discovery_engine import *  # noqa: F401,F403
from .core.discovery_engine import ModuleCapability, ModuleInfo, SystemDiscovery
