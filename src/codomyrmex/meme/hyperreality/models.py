"""Data models for hyperreality and simulation theory."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class SimulationLevel(int, Enum):
    """Baudrillard's succession of phases of the image."""

    REFLECTION = 1  # Reflection of a basic reality
    MASK = 2        # Masks and perverts a basic reality
    ABSENCE = 3     # Masks the absence of a basic reality
    PURE = 4        # No relation to any reality: pure simulacrum


class OntologicalStatus(str, Enum):
    """The status of an object's existence."""
    REAL = "real"
    VIRTUAL = "virtual"
    HYPERREAL = "hyperreal"
    FICTIONAL = "fictional"


@dataclass
class Simulacrum:
    """A copy without an original.

    Attributes:
        id: Unique identifier.
        referent: What it claims to represent (if anything).
        level: Simulation level (1-4).
        fidelity: Visual/Sensory fidelity (0-1).
        autonomy: Independence from creator/referent (0-1).
    """

    referent: str
    level: SimulationLevel
    fidelity: float = 1.0
    autonomy: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class RealityTunnel:
    """A subjective filter through which reality is perceived (Robert Anton Wilson).

    Attributes:
        name: Name of the tunnel (e.g. 'Materialist', 'Conspiratorial').
        filters: List of cognitive filters applied.
        distortion: Degree of distortion from baseline consensus reality (0-1).
    """

    name: str
    filters: list[str] = field(default_factory=list)
    distortion: float = 0.0
    active_simulacra: list[Simulacrum] = field(default_factory=list)
