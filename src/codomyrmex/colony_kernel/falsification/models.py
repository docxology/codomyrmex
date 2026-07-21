"""Falsification types and severity helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.colony_kernel.models import FalsificationFinding, FalsificationSeverity


class AttackVector(Enum):
    """Categories of adversarial attacks applied by FalsificationWorker.

    Each value is used as the ``attack_vector`` string on FalsificationFinding.
    """

    DEPENDENCY_RISK = "dependency_risk"
    SECURITY_RISK = "security_risk"
    CIRCULAR_ARCHITECTURE = "circular_architecture"
    FALSE_METRIC = "false_metric"
    OVER_BROAD_MODULE = "over_broad_module"
    HIDDEN_MAINTENANCE_COST = "hidden_maintenance_cost"
    NO_ROLLBACK = "no_rollback"
    NO_TEST_VALUE = "no_test_value"
    SCOPE_CREEP = "scope_creep"
    PREMATURE_ABSTRACTION = "premature_abstraction"


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------


@dataclass
class FalsificationReport:
    """Aggregated result of running all heuristic checks against a plan.

    ``verdict`` is one of ``"PASS"``, ``"CONDITIONAL"``, or ``"FAIL"``:

    - ``PASS``:        zero findings with severity >= HIGH (numeric >= 3)
    - ``CONDITIONAL``: 1–2 findings, none exceeds MEDIUM (numeric <= 2), no HIGH/CRITICAL
    - ``FAIL``:        any finding reaches HIGH or CRITICAL severity (numeric >= 3)

    ``required_changes`` lists concrete remediation steps derived from the
    findings' ``remediation`` fields.
    """

    plan_summary: str
    findings: list[FalsificationFinding]
    verdict: str  # "PASS" | "CONDITIONAL" | "FAIL"
    required_changes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

_SEVERITY_RANK: dict[FalsificationSeverity, int] = {
    FalsificationSeverity.LOW: 1,
    FalsificationSeverity.MEDIUM: 2,
    FalsificationSeverity.HIGH: 3,
    FalsificationSeverity.CRITICAL: 4,
}


def _rank(sev: FalsificationSeverity) -> int:
    """Return numeric rank for a severity (1=LOW … 4=CRITICAL)."""
    return _SEVERITY_RANK[sev]


__all__ = ["_SEVERITY_RANK", "AttackVector", "FalsificationReport", "_rank"]
