"""Data models for neurolinguistic programming and analysis."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class PatternType(str, Enum):
    """Classification of linguistic patterns."""

    HYPNOTIC = "hypnotic"  # Milton Model
    CLARIFYING = "clarifying"  # Meta Model
    PERSUASIVE = "persuasive"  # Cialdini/rhetoric
    DECEPTIVE = "deceptive"  # Fallacies/sophistry


@dataclass
class CognitiveFrame:
    """A cognitive frame (Lakoff) defining context and meaning.

    Attributes:
        name: Name of the frame (e.g. 'Tax Relief').
        keywords: Words that evoke this frame.
        roles: Semantic roles implied (e.g. 'Victim', 'Villain').
        logic: Underlying logic/implication.
    """

    name: str
    keywords: list[str] = field(default_factory=list)
    roles: dict[str, str] = field(default_factory=dict)
    logic: str = ""
    strength: float = 0.5


@dataclass
class LinguisticPattern:
    """A detected or generated linguistic pattern.

    Attributes:
        name: Pattern name (e.g. 'Double Bind').
        pattern_type: Classification.
        template: Generation template.
        description: Usage description.
    """

    name: str
    pattern_type: PatternType
    template: str = ""
    description: str = ""


@dataclass
class PersuasionAttempt:
    """Record of a persuasive communication attempt.

    Attributes:
        target: Audience/individual.
        technique: Method used.
        content: The actual message.
        success_prob: Estimated probability of success.
    """

    target: str
    technique: str
    content: str
    success_prob: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class BiasInstance:
    """A detected instance of cognitive bias.

    Attributes:
        bias_name: Name of the bias (e.g. 'Confirmation Bias').
        trigger: What triggered it.
        impact_score: Estimated impact (0-1).
    """

    bias_name: str
    trigger: str
    impact_score: float = 0.5
