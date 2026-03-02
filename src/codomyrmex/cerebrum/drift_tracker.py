"""Concept drift tracker for code and documentation.

Detects changes in terminology and concepts between versions of
a codebase by leveraging the ``SemioticAnalyzer`` for sign-level
drift measurement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class DriftEvent:
    """A single concept drift event.

    Attributes:
        term: The drifting concept/term.
        old_context: Previous usage context.
        new_context: New usage context.
        drift_score: Magnitude of change (0-1).
        category: Type of drift (``shifted``, ``new``, ``lost``).
    """

    term: str
    old_context: str = ""
    new_context: str = ""
    drift_score: float = 0.0
    category: str = "shifted"

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "term": self.term,
            "old_context": self.old_context,
            "new_context": self.new_context,
            "drift_score": self.drift_score,
            "category": self.category,
        }


@dataclass
class DriftSnapshot:
    """Overall drift analysis between two versions.

    Attributes:
        events: Individual drift events.
        magnitude: Overall drift magnitude (0-1).
        version_a: Source version label.
        version_b: Target version label.
    """

    events: list[DriftEvent] = field(default_factory=list)
    magnitude: float = 0.0
    version_a: str = ""
    version_b: str = ""

    @property
    def shifted_count(self) -> int:
        """shifted Count ."""
        return sum(1 for e in self.events if e.category == "shifted")

    @property
    def new_count(self) -> int:
        """new Count ."""
        return sum(1 for e in self.events if e.category == "new")

    @property
    def lost_count(self) -> int:
        """lost Count ."""
        return sum(1 for e in self.events if e.category == "lost")

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "events": [e.to_dict() for e in self.events],
            "magnitude": self.magnitude,
            "version_a": self.version_a,
            "version_b": self.version_b,
            "shifted": self.shifted_count,
            "new": self.new_count,
            "lost": self.lost_count,
        }


class ConceptDriftTracker:
    """Track concept drift across code versions.

    Compares terminology and concepts between two sets of
    text (e.g. docstrings, comments, variable names) to detect
    meaning shifts, new concepts, and abandoned concepts.

    Usage::

        tracker = ConceptDriftTracker()
        snapshot = tracker.compare(
            ["old code comments..."],
            ["new code comments..."],
        )
        print(f"Drift: {snapshot.magnitude:.1%}")
    """

    def __init__(
        self,
        shift_threshold: float = 0.3,
    ) -> None:
        """Initialize the tracker.

        Args:
            shift_threshold: Jaccard similarity below this = drift.
        """
        self._shift_threshold = shift_threshold

    def compare(
        self,
        corpus_a: list[str],
        corpus_b: list[str],
        version_a: str = "v1",
        version_b: str = "v2",
    ) -> DriftSnapshot:
        """Compare two corpora and detect concept drift.

        Args:
            corpus_a: Baseline texts.
            corpus_b: Comparison texts.
            version_a: Label for baseline.
            version_b: Label for comparison.

        Returns:
            ``DriftSnapshot`` with drift events and magnitude.
        """
        # Extract term frequencies from each corpus
        terms_a = self._extract_terms(corpus_a)
        terms_b = self._extract_terms(corpus_b)

        keys_a = set(terms_a.keys())
        keys_b = set(terms_b.keys())
        shared = keys_a & keys_b

        events: list[DriftEvent] = []

        # Shifted: same term, different context
        for term in shared:
            ctx_a = set(terms_a[term])
            ctx_b = set(terms_b[term])
            intersection = len(ctx_a & ctx_b)
            union = len(ctx_a | ctx_b)
            jaccard = intersection / union if union > 0 else 1.0

            if jaccard < self._shift_threshold:
                events.append(DriftEvent(
                    term=term,
                    old_context=" ".join(sorted(ctx_a)[:5]),
                    new_context=" ".join(sorted(ctx_b)[:5]),
                    drift_score=1.0 - jaccard,
                    category="shifted",
                ))

        # New concepts
        for term in keys_b - keys_a:
            events.append(DriftEvent(
                term=term,
                new_context=" ".join(sorted(terms_b[term])[:5]),
                drift_score=1.0,
                category="new",
            ))

        # Lost concepts
        for term in keys_a - keys_b:
            events.append(DriftEvent(
                term=term,
                old_context=" ".join(sorted(terms_a[term])[:5]),
                drift_score=1.0,
                category="lost",
            ))

        total_concepts = len(keys_a | keys_b)
        magnitude = len(events) / total_concepts if total_concepts > 0 else 0.0

        snapshot = DriftSnapshot(
            events=events,
            magnitude=min(magnitude, 1.0),
            version_a=version_a,
            version_b=version_b,
        )

        logger.info(
            "Drift analysis complete",
            extra={
                "magnitude": round(snapshot.magnitude, 3),
                "shifted": snapshot.shifted_count,
                "new": snapshot.new_count,
                "lost": snapshot.lost_count,
            },
        )

        return snapshot

    @staticmethod
    def _extract_terms(corpus: list[str]) -> dict[str, list[str]]:
        """Extract terms and their contexts from a corpus."""
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on",
                      "at", "to", "for", "of", "and", "or", "but", "not", "with",
                      "from", "by", "as", "it", "this", "that", "def", "class",
                      "self", "return", "import", "none", "true", "false"}
        terms: dict[str, list[str]] = {}

        for text in corpus:
            words = [w.strip(".,!?;:\"'()[]{}#").lower()
                     for w in text.split()]
            clean = [w for w in words if len(w) > 2 and w not in stop_words]

            for i, word in enumerate(clean):
                if word not in terms:
                    terms[word] = []
                # Context: surrounding words
                start = max(0, i - 2)
                end = min(len(clean), i + 3)
                ctx = clean[start:end]
                terms[word].extend(ctx)

        return terms


__all__ = [
    "ConceptDriftTracker",
    "DriftEvent",
    "DriftSnapshot",
]
