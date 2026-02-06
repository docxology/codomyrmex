"""Persona Definition Module.

Defines the core Persona structure and verification levels for the identity system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VerificationLevel(Enum):
    """Level of identity verification."""
    UNVERIFIED = "unverified"
    ANON = "anonymous_verified"       # Verified via bio-cognitive metrics
    VERIFIED_ANON = "verified_anon"   # Anon but persistent reputation
    KYC = "kyc_verified"              # Full legal identity link

@dataclass
class Persona:
    """Represents a distinct identity persona."""
    id: str
    name: str
    level: VerificationLevel
    created_at: datetime = field(default_factory=datetime.now)
    attributes: dict[str, str] = field(default_factory=dict)
    # Crumbs (tracking data) are siloed per persona
    crumbs: list[str] = field(default_factory=list)

    def add_attribute(self, key: str, value: str) -> None:
        """Add an attribute to the persona."""
        self.attributes[key] = value

    def add_crumb(self, crumb: str) -> None:
        """Record an interaction crumb."""
        self.crumbs.append(crumb)
