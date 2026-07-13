"""Attack-vector check: check dependency risk."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_dependency_risk(plan: dict[str, Any]) -> FalsificationFinding | None:
    """Attack: plan introduces unvetted external dependencies."""
    deps = plan.get("dependencies", [])
    if isinstance(deps, str):
        dep_list = [d.strip() for d in re.split(r"[,\n;]", deps) if d.strip()]
    elif isinstance(deps, (list, tuple)):
        dep_list = [str(d).strip() for d in deps if str(d).strip()]
    else:
        dep_list = []

    # Flag dependencies that look like external packages (contain no dotted project prefix)
    # and are not stdlib — heuristic: no '/' in name, has '-' or is all-lowercase short
    risky = []
    for dep in dep_list:
        # Skip dotted internal module paths
        if "." in dep and not dep.startswith("http"):
            continue
        # External package heuristic: lowercase, optional hyphens, no path separators
        if re.fullmatch(r"[a-z][a-z0-9\-_]*", dep) and len(dep) <= 40:
            risky.append(dep)

    if len(risky) >= 3:
        return FalsificationFinding(
            claim="The plan does not introduce an unvetted external dependency footprint.",
            attack_vector=AttackVector.DEPENDENCY_RISK.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={"suspicious_external_deps": risky[:10]},
            remediation=(
                f"The plan lists {len(risky)} apparent external packages ({', '.join(risky[:3])}, …). "
                "Justify each addition: is it already vendored, does it have a security audit, "
                "and is a lighter stdlib alternative available?"
            ),
        )

    return None
