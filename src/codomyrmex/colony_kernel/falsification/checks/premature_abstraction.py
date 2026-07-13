"""Attack-vector check: check premature abstraction."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_premature_abstraction(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan introduces a generic abstraction without demonstrated need."""
    rationale = str(plan.get("rationale", "")).strip()
    scope_str = str(plan.get("scope", "")).strip()
    combined = f"{rationale} {scope_str}"

    abstraction_signals = [
        r"\bgeneric\b",
        r"\breusable?\b",
        r"\bextensible\b",
        r"\bplug-?in\b",
        r"\babstract\s+(base\s+)?class\b",
        r"\binterface\b",
        r"\bframework\b",
        r"\bplatform\b",
    ]
    hits = [p for p in abstraction_signals if re.search(p, combined, re.IGNORECASE)]

    if not hits:
        return None

    # Look for evidence that the abstraction is backed by multiple concrete callers
    evidence_patterns = [
        r"\b\d+\s+(callers?|uses?|consumers?|clients?)\b",
        r"\bthree\s+(or\s+more\s+)?(callers?|uses?)\b",
        r"\bexisting\s+(callers?|consumers?|uses?)\b",
        r"\bproven\b",
        r"\bdemonstrated\b",
    ]
    has_evidence = any(re.search(p, combined, re.IGNORECASE) for p in evidence_patterns)

    if not has_evidence and len(hits) >= 2:
        return FalsificationFinding(
            claim="The abstraction is justified by at least three distinct concrete use-sites.",
            attack_vector=AttackVector.PREMATURE_ABSTRACTION.value,
            severity=FalsificationSeverity.LOW,
            evidence={
                "abstraction_signals": hits,
                "combined_excerpt": combined[:300],
            },
            remediation=(
                "Abstractions earn their complexity by reducing duplication across three or "
                "more concrete use-sites.  Document the existing callers that motivated the "
                "abstraction, or defer the generalisation until the need is demonstrated."
            ),
        )

    return None
