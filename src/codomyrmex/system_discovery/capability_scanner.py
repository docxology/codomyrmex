# DEPRECATED(v0.2.0): Shim module. Import from system_discovery.core.capability_scanner instead. Will be removed in v0.3.0.
"""Backward-compatible re-export from system_discovery.core.capability_scanner."""
from .core.capability_scanner import *  # noqa: F401,F403
from .core.capability_scanner import (
    CapabilityScanner,
    ClassCapability,
    FunctionCapability,
    ModuleCapability,
)
