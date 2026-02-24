"""Relation strength scoring with temporal decay.

Computes weighted relationship scores between entities based on
interaction frequency, recency, and interaction type weights.
Supports configurable decay functions for aging interactions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DecayFunction(Enum):
    """Supported temporal decay strategies."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    STEP = "step"
    NONE = "none"


@dataclass
class Interaction:
    """A single interaction between two entities.

    Attributes:
        source: ID of the initiating entity.
        target: ID of the receiving entity.
        interaction_type: Category of interaction (e.g. "message", "meeting").
        timestamp: Unix timestamp of the interaction.
        weight: Base weight of this interaction (default 1.0).
        metadata: Optional extra data about the interaction.
    """

    source: str
    target: str
    interaction_type: str
    timestamp: float
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StrengthConfig:
    """Configuration for the strength scorer.

    Attributes:
        decay_function: Which decay curve to apply.
        half_life: For exponential decay, the time (seconds) at which
            an interaction's weight drops to 50%.
        max_age: For linear/step decay, interactions older than this
            (seconds) are discarded.
        type_weights: Mapping of interaction_type -> multiplier.
            Unknown types get a multiplier of 1.0.
        min_score: Scores below this threshold are clamped to 0.
    """

    decay_function: DecayFunction = DecayFunction.EXPONENTIAL
    half_life: float = 86400.0 * 30  # 30 days
    max_age: float = 86400.0 * 365  # 1 year
    type_weights: dict[str, float] = field(default_factory=dict)
    min_score: float = 0.0


@dataclass
class StrengthScore:
    """Result of scoring the relationship between two entities.

    Attributes:
        source: Entity A.
        target: Entity B.
        raw_score: Sum of decay-weighted interaction values.
        normalized_score: Raw score normalized to [0, 1] relative to
            the strongest relationship in the scorer.
        interaction_count: Number of interactions considered.
        latest_interaction: Timestamp of the most recent interaction.
    """

    source: str
    target: str
    raw_score: float
    normalized_score: float
    interaction_count: int
    latest_interaction: float


class RelationStrengthScorer:
    """Scores relationship strength using interaction history and decay.

    The scorer accumulates interactions and computes pairwise strength
    scores by applying temporal decay and type-based weighting.

    Example::

        scorer = RelationStrengthScorer(config=StrengthConfig(
            decay_function=DecayFunction.EXPONENTIAL,
            half_life=86400 * 7,
            type_weights={"meeting": 3.0, "email": 1.0},
        ))
        scorer.add_interaction(Interaction("a", "b", "meeting", time.time()))
        score = scorer.score("a", "b", now=time.time())
    """

    def __init__(self, config: StrengthConfig | None = None) -> None:
        """Execute   Init   operations natively."""
        self._config = config or StrengthConfig()
        self._interactions: list[Interaction] = []

    @property
    def config(self) -> StrengthConfig:
        """Current scoring configuration."""
        return self._config

    @property
    def interaction_count(self) -> int:
        """Total number of recorded interactions."""
        return len(self._interactions)

    def add_interaction(self, interaction: Interaction) -> None:
        """Record an interaction."""
        self._interactions.append(interaction)

    def add_interactions(self, interactions: list[Interaction]) -> None:
        """Record multiple interactions at once."""
        self._interactions.extend(interactions)

    def _decay_weight(self, age: float) -> float:
        """Apply the configured decay function to an interaction's age.

        Args:
            age: Time elapsed since the interaction (seconds).

        Returns:
            Multiplier in [0, 1].
        """
        cfg = self._config

        if age < 0:
            return 1.0

        if cfg.decay_function == DecayFunction.NONE:
            return 1.0

        if cfg.decay_function == DecayFunction.EXPONENTIAL:
            if cfg.half_life <= 0:
                return 0.0
            return math.pow(0.5, age / cfg.half_life)

        if cfg.decay_function == DecayFunction.LINEAR:
            if cfg.max_age <= 0:
                return 0.0
            return max(0.0, 1.0 - age / cfg.max_age)

        if cfg.decay_function == DecayFunction.STEP:
            return 1.0 if age <= cfg.max_age else 0.0

        return 1.0

    def _pair_key(self, a: str, b: str) -> tuple[str, str]:
        """Canonical undirected pair key."""
        return (min(a, b), max(a, b))

    def score(self, source: str, target: str, now: float) -> StrengthScore:
        """Compute the strength score between two entities.

        Args:
            source: First entity ID.
            target: Second entity ID.
            now: Current timestamp for decay calculation.

        Returns:
            A StrengthScore with raw and normalized values.
        """
        key = self._pair_key(source, target)
        cfg = self._config

        raw_score = 0.0
        count = 0
        latest = 0.0

        for ix in self._interactions:
            ix_key = self._pair_key(ix.source, ix.target)
            if ix_key != key:
                continue

            age = now - ix.timestamp
            decay = self._decay_weight(age)
            type_mult = cfg.type_weights.get(ix.interaction_type, 1.0)
            raw_score += ix.weight * decay * type_mult
            count += 1
            latest = max(latest, ix.timestamp)

        if raw_score < cfg.min_score:
            raw_score = 0.0

        return StrengthScore(
            source=source,
            target=target,
            raw_score=raw_score,
            normalized_score=0.0,  # filled by score_all
            interaction_count=count,
            latest_interaction=latest,
        )

    def score_all(self, now: float) -> list[StrengthScore]:
        """Score all observed entity pairs.

        Scores are normalized so the strongest pair has
        ``normalized_score == 1.0``.

        Args:
            now: Current timestamp for decay calculation.

        Returns:
            List of StrengthScore objects, sorted by raw_score descending.
        """
        pairs: set[tuple[str, str]] = set()
        for ix in self._interactions:
            pairs.add(self._pair_key(ix.source, ix.target))

        scores = [self.score(a, b, now) for a, b in pairs]

        max_raw = max((s.raw_score for s in scores), default=0.0)
        if max_raw > 0:
            for s in scores:
                s.normalized_score = s.raw_score / max_raw

        scores.sort(key=lambda s: s.raw_score, reverse=True)
        return scores

    def top_relations(self, entity: str, now: float, n: int = 5) -> list[StrengthScore]:
        """Return the top-N strongest relations for a given entity.

        Args:
            entity: The entity ID to query.
            now: Current timestamp for decay.
            n: Maximum number of results.

        Returns:
            List of StrengthScore objects sorted descending by raw_score.
        """
        partners: set[str] = set()
        for ix in self._interactions:
            if ix.source == entity:
                partners.add(ix.target)
            elif ix.target == entity:
                partners.add(ix.source)

        scores = [self.score(entity, p, now) for p in partners]
        scores.sort(key=lambda s: s.raw_score, reverse=True)
        return scores[:n]

    def clear(self) -> None:
        """Remove all recorded interactions."""
        self._interactions.clear()
