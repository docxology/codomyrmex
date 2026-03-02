"""Data models for narrative structures."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Archetype(StrEnum):
    """Jungian/Campbellian character archetypes."""

    HERO = "hero"
    SHADOW = "shadow"
    MENTOR = "mentor"
    TRICKSTER = "trickster"
    HERALD = "herald"
    THRESHOLD_GUARDIAN = "threshold_guardian"
    SHAPESHIFTER = "shapeshifter"
    ALLY = "ally"


@dataclass
class NarrativeTemplate:
    """A reusable template for narrative generation.

    Attributes:
        name: Template name (e.g. 'Hero's Journey').
        stages: Ordered list of narrative stages.
        roles: Required archetypal roles.
    """

    name: str
    stages: list[str]
    roles: list[Archetype]


@dataclass
class NarrativeArc:
    """The structural progression of a narrative.

    Attributes:
        name: Arc name (e.g. 'Tragedy', 'Rags to Riches').
        tension_curve: List of floats representing dramatic tension over time (0-1).
        emotional_valence: List of floats representing emotional state (-1 to 1).
    """

    name: str
    tension_curve: list[float] = field(default_factory=list)
    emotional_valence: list[float] = field(default_factory=list)


@dataclass
class Narrative:
    """A computational representation of a story.

    Attributes:
        title: Title or identifier.
        theme: Central thematic statement.
        arc: The structural arc used.
        characters: Map of character names to archetypes.
        cultural_resonance: Estimated resonance score (0-1).
        content_segments: The actual text/content chunks.
        id: Unique identifier.
    """

    title: str
    theme: str
    arc: NarrativeArc
    characters: dict[str, Archetype] = field(default_factory=dict)
    cultural_resonance: float = 0.5
    content_segments: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default="")
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid.uuid4())
