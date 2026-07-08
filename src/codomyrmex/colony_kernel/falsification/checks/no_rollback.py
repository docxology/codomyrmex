"""Attack-vector check: check no rollback."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_no_rollback(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan has no credible rollback path.

    Returns a HIGH finding if ``rollback_plan`` is absent, empty, or
    contains only placeholder language.
    """
    rollback = plan.get("rollback_plan", "")
    if not isinstance(rollback, str):
        rollback = str(rollback)
    rollback = rollback.strip()

    placeholder_patterns = [
        r"^\s*$",
        r"^(n/?a|none|tbd|todo|unknown|not\s+applicable)\.?$",
        r"^will\s+(revert|undo)\s+manually$",
    ]
    is_missing = not rollback or any(
        re.fullmatch(p, rollback, re.IGNORECASE) for p in placeholder_patterns
    )

    if is_missing:
        return FalsificationFinding(
            claim="The plan provides a credible rollback procedure.",
            attack_vector=AttackVector.NO_ROLLBACK.value,
            severity=FalsificationSeverity.HIGH,
            evidence={"rollback_plan": rollback or "<absent>"},
            remediation=(
                "Provide a concrete rollback plan: the exact git revert command, "
                "database migration down-script, or feature-flag toggle that restores "
                "the previous state without manual intervention."
            ),
        )

    # Soft check: rollback present but suspiciously short (< 20 chars)
    if len(rollback) < 20:
        return FalsificationFinding(
            claim="The rollback plan is sufficiently detailed.",
            attack_vector=AttackVector.NO_ROLLBACK.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={"rollback_plan": rollback, "length": len(rollback)},
            remediation=(
                "Expand the rollback plan to include the specific command or procedure "
                "and the expected post-rollback state."
            ),
        )

    return None
