"""Data models for the semiotic submodule."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SignType(str, Enum):
    """Peircean sign trichotomy classification."""

    ICON = "icon"
    INDEX = "index"
    SYMBOL = "symbol"


@dataclass
class Sign:
    """A semiotic sign — the fundamental unit of meaning.

    Attributes:
        signifier: The form which the sign takes (word, sound, image).
        signified: The concept it represents.
        sign_type: Peircean classification (Icon/Index/Symbol).
        cultural_context: The context in which this meaning holds.
        stability: How fixed the signifier-signified relationship is (0-1).
        id: Unique identifier used for graph nodes.
    """

    signifier: str
    signified: str
    sign_type: SignType = SignType.SYMBOL
    cultural_context: str = ""
    stability: float = 0.8
    id: str = field(default="")

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.id:
            h = hashlib.sha256(f"{self.signifier}:{self.signified}".encode())
            self.id = h.hexdigest()[:16]
        self.stability = max(0.0, min(1.0, self.stability))


@dataclass
class SemanticTerritory:
    """A mapped region of semantic space controlled by a specific discourse.

    Attributes:
        domain: The name of the semantic domain (e.g., "economics").
        signs: The key signs that define this territory.
        boundaries: Map of adjacent domains and their semantic distance.
        contested: Whether this territory is currently under semiotic dispute.
    """

    domain: str
    signs: List[Sign] = field(default_factory=list)
    boundaries: Dict[str, float] = field(default_factory=dict)
    contested: bool = False

    @property
    def density(self) -> float:
        """Calculate semantic density (signs per boundary unit)."""
        if not self.boundaries:
            return len(self.signs)
        return len(self.signs) / len(self.boundaries)


@dataclass
class DriftReport:
    """Report on semiotic drift between two corpora or timeframes.

    Attributes:
        shifted_signs: Signs whose signifieds have changed.
        stable_signs: Signs that remained constant.
        new_signs: Signs present in target but not source.
        lost_signs: Signs present in source but not target.
        drift_magnitude: Overall quantitative measure of drift (0-1).
        timestamp: Time of analysis.
    """

    shifted_signs: List[Sign] = field(default_factory=list)
    stable_signs: List[Sign] = field(default_factory=list)
    new_signs: List[Sign] = field(default_factory=list)
    lost_signs: List[Sign] = field(default_factory=list)
    drift_magnitude: float = 0.0
    timestamp: float = field(default_factory=time.time)

    @property
    def stability_ratio(self) -> float:
        """Ratio of stable signs to total shared signs."""
        total_shared = len(self.shifted_signs) + len(self.stable_signs)
        if total_shared == 0:
            return 1.0
        return len(self.stable_signs) / total_shared
