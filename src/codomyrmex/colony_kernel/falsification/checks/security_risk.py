"""Attack-vector check: check security risk."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_security_risk(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan touches security-sensitive paths without explicit review annotation."""
    combined = " ".join(
        [
            str(plan.get("target", "")),
            str(plan.get("rationale", "")),
            str(plan.get("scope", "")),
        ]
    )

    sensitive_patterns = [
        r"\bauth(entication|orization|token)?\b",
        r"\bpassword\b",
        r"\bcredential\b",
        r"\bsecret\b",
        r"\bencrypt\b",
        r"\bprivilege(d)?\b",
        r"\bsudo\b",
        r"\broot\b",
        r"\bpermission\b",
        r"\baccess\s+control\b",
        r"\bsanitiz\b",
        r"\binjection\b",
    ]
    hits = [p for p in sensitive_patterns if re.search(p, combined, re.IGNORECASE)]

    if not hits:
        return None

    # Check whether the plan acknowledges the security surface
    security_ack_patterns = [
        r"\bsecurity\s+review\b",
        r"\bsecurity\s+audit\b",
        r"\bsast\b",
        r"\bguard_ant\b",
        r"\bthreat\s+model\b",
    ]
    has_ack = any(
        re.search(p, combined, re.IGNORECASE) for p in security_ack_patterns
    )

    if not has_ack:
        return FalsificationFinding(
            claim="Security-sensitive changes are accompanied by an explicit security review.",
            attack_vector=AttackVector.SECURITY_RISK.value,
            severity=FalsificationSeverity.HIGH,
            evidence={"sensitive_terms_found": hits[:5]},
            remediation=(
                "The plan touches security-sensitive surface area but does not mention "
                "a security review or GUARD_ANT sign-off.  Add a security review step "
                "before execution and annotate the proposal with 'security_review: required'."
            ),
        )

    return None
