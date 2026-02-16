"""Backward-compatible re-export from system_discovery.core.capability_scanner."""
from .core.capability_scanner import *  # noqa: F401,F403
from .core.capability_scanner import (
    CapabilityScanner,
    ClassCapability,
    FunctionCapability,
    ModuleCapability,
)
