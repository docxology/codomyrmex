"""Linguistic pattern definitions and detection."""

from __future__ import annotations

from typing import List, Dict

from codomyrmex.meme.neurolinguistic.models import LinguisticPattern, PatternType


def milton_model_patterns() -> List[LinguisticPattern]:
    """Return a library of Milton Model (hypnotic) patterns."""
    return [
        LinguisticPattern(
            name="Mind Read",
            pattern_type=PatternType.HYPNOTIC,
            template="You may fit a pattern like...",
            description="Claiming to know the internal state of another."
        ),
        LinguisticPattern(
            name="Lost Performative",
            pattern_type=PatternType.HYPNOTIC,
            template="It is known that...",
            description="Value judgment where the performer is omitted."
        ),
        LinguisticPattern(
            name="Cause-Effect",
            pattern_type=PatternType.HYPNOTIC,
            template="Reading this makes you relax...",
            description="Implied causality between unrelated events."
        ),
    ]


def meta_model_patterns() -> List[LinguisticPattern]:
    """Return a library of Meta Model (clarifying) patterns."""
    return [
        LinguisticPattern(
            name="Universal Quantifier Challenge",
            pattern_type=PatternType.CLARIFYING,
            template="Always? Never? Every time?",
            description="Challenging absolutes like 'always' or 'never'."
        ),
        LinguisticPattern(
            name="Specify Verb",
            pattern_type=PatternType.CLARIFYING,
            template="How specifically did X happen?",
            description="Asking for specific details of an action."
        ),
    ]


def detect_patterns(text: str) -> List[LinguisticPattern]:
    """Detect linguistic patterns in text.

    (Placeholder for regex/LLM based detection).
    """
    detected = []
    # Simple keyword heuristic for demo
    if "always" in text.lower() or "never" in text.lower():
        detected.append(
            LinguisticPattern(
                name="Universal Quantifier",
                pattern_type=PatternType.DECEPTIVE,
                description="Use of absolutes."
            )
        )
    return detected
