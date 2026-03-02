"""Data models for epistemic state and verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class EvidenceType(StrEnum):
    """Classification of evidence strength."""

    EMPIRICAL = "empirical"  # Direct observation/data
    LOGICAL = "logical"  # Deductive reasoning
    TESTIMONIAL = "testimonial"  # Witness/Expert account
    ANECDOTAL = "anecdotal"  # Weak single instance
    FABRICATED = "fabricated"  # Disinformation


@dataclass
class Evidence:
    """A piece of evidence supporting or refuting a claim.

    Attributes:
        content: Description of evidence.
        source: Origin.
        evidence_type: Type classification.
        weight: Strength (0-1).
        validity: Assessed validity (0-1).
    """

    content: str
    source: str
    evidence_type: EvidenceType
    weight: float = 0.5
    validity: float = 1.0


@dataclass
class Fact:
    """A verified unit of truth.

    Attributes:
        statement: The factual claim.
        verification_method: How it was verified.
        confidence: Confidence level (0-1).
    """

    statement: str
    verification_method: str
    confidence: float = 1.0


@dataclass
class Belief:
    """A held conviction that may or may not be factual.

    Attributes:
        statement: The belief content.
        adherent: Entity holding the belief.
        certainty: Subjective certainty (0-1).
        emotional_investment: Attachment level (0-1).
    """

    statement: str
    adherent: str
    certainty: float = 0.5
    emotional_investment: float = 0.5
    supporting_evidence: list[Evidence] = field(default_factory=list)


@dataclass
class EpistemicState:
    """The aggregate epistemic status of a system or agent.

    Attributes:
        facts: Known facts.
        beliefs: Held beliefs.
        entropy: Measure of confusion/uncertainty.
    """

    facts: list[Fact] = field(default_factory=list)
    beliefs: list[Belief] = field(default_factory=list)
    entropy: float = 0.0
