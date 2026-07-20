"""Attack-vector check: check hidden maintenance cost."""

from __future__ import annotations

import re
from typing import Any

from codomyrmex.colony_kernel.falsification.models import AttackVector
from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


def check_hidden_maintenance_cost(plan: dict[str, Any]) -> FalsificationFinding | None:
    action_type = str(plan.get("action_type", "")).strip().lower()
    target = str(plan.get("target", "")).strip().lower()
    rationale = str(plan.get("rationale", "")).strip()
    scope_str = str(plan.get("scope", "")).strip()
    combined = f"{action_type} {target} {rationale} {scope_str}"

    durable_change_patterns = [
        r"\b(create|add|introduce|migrate|refactor|replace)\b",
        r"\b(module|service|framework|platform|pipeline|integration)\b",
        r"\bnew\s+(api|schema|storage|dependency|subsystem)\b",
    ]
    durable_signals = [
        pattern
        for pattern in durable_change_patterns
        if re.search(pattern, combined, re.IGNORECASE)
    ]
    if len(durable_signals) < 2:
        return None

    maintenance_fields = (
        "maintenance_plan",
        "owner",
        "ownership",
        "deprecation_plan",
        "runbook",
    )
    acknowledged = any(str(plan.get(field, "")).strip() for field in maintenance_fields)
    if acknowledged:
        return None

    return FalsificationFinding(
        claim="The plan accounts for long-term ownership and maintenance burden.",
        attack_vector=AttackVector.HIDDEN_MAINTENANCE_COST.value,
        severity=FalsificationSeverity.MEDIUM,
        evidence={
            "durable_change_signals": durable_signals,
            "maintenance_fields_checked": list(maintenance_fields),
        },
        remediation=(
            "Add an owner, maintenance_plan, runbook, or deprecation_plan that explains "
            "who will operate the durable change and how future upkeep will be handled."
        ),
    )
