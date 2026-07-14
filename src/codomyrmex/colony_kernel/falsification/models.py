"""Falsification types and severity helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypedDict

from codomyrmex.colony_kernel.models import (
    _SEVERITY_RANK,
    FalsificationFinding,
    FalsificationSeverity,
)


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


class FalsificationPlan(TypedDict):
    """Normalized input contract consumed by every falsification check."""

    agent_id: str
    action_type: str
    target: str
    rationale: str
    expected_outcome: str
    rollback_plan: str
    tests: Any
    metrics: Any
    scope: Any
    dependencies: Any
    evidence: dict[str, Any]
    budget_estimate: dict[str, Any]
    repo_root: str


# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

def _rank(sev: FalsificationSeverity) -> int:
    """Return numeric rank for a severity (1=LOW … 4=CRITICAL)."""
    return _SEVERITY_RANK[sev]

__all__ = [
    "_SEVERITY_RANK",
    "AttackVector",
    "FalsificationPlan",
    "FalsificationReport",
    "_rank",
]
