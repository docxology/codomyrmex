"""Persona Definition Module.

Defines the core Persona structure and verification levels for the identity system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class VerificationLevel(Enum):
    """Level of identity verification."""

    UNVERIFIED = "unverified"
    ANON = "anonymous_verified"  # Verified via bio-cognitive metrics (Grey)
    VERIFIED_ANON = "verified_anon"  # Anon but persistent reputation (Black)
    KYC = "kyc_verified"  # Full legal identity link (Blue)


@dataclass
class Persona:
    """Represents a distinct identity persona.

    Personas allow for context-specific identities with varying levels of trust
    and privacy.
    """

    id: str
    name: str
    level: VerificationLevel
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    attributes: dict[str, str] = field(default_factory=dict)
    # Crumbs (tracking data) are siloed per persona
    crumbs: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    is_active: bool = True

    def add_attribute(self, key: str, value: str) -> None:
        """Add an attribute to the persona."""
        self.attributes[key] = value

    def add_crumb(self, crumb: str) -> None:
        """Record an interaction crumb."""
        self.crumbs.append(crumb)

    def add_capability(self, capability: str) -> None:
        """Add a capability to this persona."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)

    def has_capability(self, capability: str) -> bool:
        """Check if persona has a specific capability."""
        return capability in self.capabilities

    def to_dict(self) -> dict:
        """Convert persona to a dictionary for export/serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "created_at": self.created_at.isoformat(),
            "attributes": self.attributes.copy(),
            "crumbs_count": len(self.crumbs),
            "capabilities": self.capabilities.copy(),
            "is_active": self.is_active,
        }
