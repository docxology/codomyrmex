"""Attack-vector check: check over broad module."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_over_broad_module(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan proposes a module that tries to do too many things."""
    rationale = str(plan.get("rationale", "")).strip()
    scope_str = str(plan.get("scope", "")).strip()
    combined = f"{rationale} {scope_str}"

    # Signal: rationale lists many heterogeneous responsibilities
    responsibility_indicators = re.findall(
        r"\b(handles?|manages?|coordinates?|orchestrates?|provides?|implements?|supports?|wraps?)\b",
        combined,
        re.IGNORECASE,
    )
    if len(responsibility_indicators) >= 5:
        return FalsificationFinding(
            claim="The proposed module has a single, well-bounded responsibility.",
            attack_vector=AttackVector.OVER_BROAD_MODULE.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={
                "responsibility_verb_count": len(responsibility_indicators),
                "verbs_found": list({v.lower() for v in responsibility_indicators[:8]}),
            },
            remediation=(
                f"The rationale uses {len(responsibility_indicators)} responsibility verbs, "
                "suggesting a module that does too many things.  Apply the Single Responsibility "
                "Principle: split into focused sub-modules or reduce the stated scope."
            ),
        )

    # Signal: target path contains more than 4 dotted segments (deep nesting)
    target = str(plan.get("target", ""))
    if target.count(".") >= 5:
        return FalsificationFinding(
            claim="The module target path is not excessively deep.",
            attack_vector=AttackVector.OVER_BROAD_MODULE.value,
            severity=FalsificationSeverity.LOW,
            evidence={"target": target, "depth": target.count(".")},
            remediation=(
                f"`{target}` is {target.count('.') + 1} levels deep.  "
                "Deep nesting often signals accumulated responsibilities.  "
                "Consider flattening the hierarchy or extracting a top-level module."
            ),
        )

    return None
