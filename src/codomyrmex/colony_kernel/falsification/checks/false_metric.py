"""Attack-vector check: check false metric."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_false_metric(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan's expected_outcome is non-falsifiable (cannot be proven false)."""
    outcome = str(plan.get("expected_outcome", "")).strip()
    if not outcome:
        return FalsificationFinding(
            claim="The plan states a falsifiable expected outcome.",
            attack_vector=AttackVector.FALSE_METRIC.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={"expected_outcome": "<absent>"},
            remediation=(
                "Add an `expected_outcome` that can be objectively verified or falsified, "
                "e.g. 'all unit tests pass', 'API response time < 200ms under load test'."
            ),
        )

    # Detect tautological / unfalsifiable language
    unfalsifiable_patterns = [
        r"^(it\s+)?(will\s+)?work(s)?\s*$",
        r"\bimprove[sd]?\b.*\boverall\b",
        r"\bbetter\b.*\bsystem\b",
        r"\bno\s+issues\b",
        r"\bsmoothly\b",
        r"\bseamlessly\b",
        r"\bstable\b",
    ]
    hits = [
        p for p in unfalsifiable_patterns if re.search(p, outcome, re.IGNORECASE)
    ]
    if len(hits) >= 2:
        return FalsificationFinding(
            claim="The expected outcome is concrete and falsifiable.",
            attack_vector=AttackVector.FALSE_METRIC.value,
            severity=FalsificationSeverity.LOW,
            evidence={"expected_outcome": outcome[:200], "vague_patterns": hits},
            remediation=(
                "Replace vague outcome language with a concrete, testable assertion.  "
                "Outcomes like 'works smoothly' cannot be verified by an automated gate."
            ),
        )

    return None
