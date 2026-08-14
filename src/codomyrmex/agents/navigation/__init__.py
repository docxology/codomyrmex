"""Read-only navigation and operability catalog for agent consumers."""

from .catalog import (
    CapabilityCatalog,
    CapabilityKind,
    CapabilityRecord,
    build_capability_catalog,
)

__all__ = [
    "CapabilityCatalog",
    "CapabilityKind",
    "CapabilityRecord",
    "build_capability_catalog",
]
