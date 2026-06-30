"""Actuation gate — the +1/0/-1 permission layer for the Colony Kernel.

The gate enters a non-actuating witness state before evaluating any proposal,
inspecting all available signals and trust data before rendering a verdict.

This is the canonical standalone implementation. It supports two call styles:

* **Standalone / test style** — constructor receives a raw TraceField as
  ``pheromone_store`` and an optional resource ledger; ``evaluate`` is called
  with two positional arguments ``(proposal, profile)``.
* **Kernel style** — constructor receives a PheromoneStore; ``evaluate`` is
  called with four positional arguments
  ``(proposal, profile, findings, budget_approved)``.

Both styles produce a ``GateResult`` with the same field contract.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.agentic_memory.stigmergy.field import TraceField
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    FalsificationFinding,
    FalsificationSeverity,
    GateDecision,
    GateResult,
    SignalType,
)

# ---------------------------------------------------------------------------
# Gate thresholds — exported so kernel.py can re-export them for tests
# ---------------------------------------------------------------------------

_GATE_SCORE_EXECUTE = 0.75  # score >= this → EXECUTE
_GATE_SCORE_HOLD = 0.50     # score >= this → HOLD; below → REFUSE

# Risk pheromone thresholds
_HIGH_RISK_THRESHOLD = 6.0  # combined risk pressure ≥ this → risk_ok = 0.0
_MED_RISK_THRESHOLD = 3.0   # combined risk pressure ≥ this → risk_ok = 0.5

# Trust floor — below this (strictly less than) triggers a hard REFUSE
_TRUST_HARD_FLOOR = 0.30

# Completeness penalty per missing field (rollback_plan, evidence, expected_outcome)
_MISSING_FIELD_PENALTY = 0.35

# Consecutive-failure trust penalty applied when recent_failures >= 3
_FAILURE_PENALTY = 0.25

# Falsification severity numeric weights
_FALSIFICATION_WEIGHT: dict[FalsificationSeverity, float] = {
    FalsificationSeverity.LOW: 0.05,
    FalsificationSeverity.MEDIUM: 0.20,
    FalsificationSeverity.HIGH: 0.45,
    FalsificationSeverity.CRITICAL: 1.0,
}


def _sense_pheromone(store: Any, target: str, signal_type: SignalType) -> float:
    """Read pheromone strength at (target, signal_type) from any store type.

    Handles two protocols:
    * **TraceField** — uses the compound key ``"{target}:{signal_type.value}"``.
    * **PheromoneStore** — calls ``store.sense(target, signal_type)`` directly.
    """
    if isinstance(store, TraceField):
        key = f"{target}:{signal_type.value}"
        marker = store.sense(key)
        return marker.strength if marker is not None else 0.0
    # PheromoneStore protocol
    return store.sense(target, signal_type)


class ActuationGate:
    """Multi-factor actuation gate producing a GateResult.

    Gate score formula (0.0–1.0):
        score = (
            budget_ok  * 0.30
            + risk_ok  * 0.30
            + trust_ok * 0.25
            + completeness * 0.15
        )

    Components:
      budget_ok      — 1.0 if resource_ledger.can_afford passes; hard REFUSE if not
      risk_ok        — 1.0 / 0.5 / 0.0 based on RISK pheromone pressure thresholds
      trust_ok       — 0.5 if trust ∈ [0.3, 0.6); 1.0 if trust ≥ 0.6;
                       reduced by _FAILURE_PENALTY when ≥ 3 recent failures
      completeness   — max(0, 1 − missing_count × _MISSING_FIELD_PENALTY)
                       where missing fields are: rollback_plan, evidence, expected_outcome

    Hard overrides (evaluated before scoring):
      1. Budget fail (resource_ledger.can_afford → False) → immediate REFUSE, score=0.0
      2. SANDBOX role → immediate REFUSE, score=0.0
      3. Trust < 0.30 → immediate REFUSE
      4. CRITICAL falsification finding → immediate REFUSE
    """

    def __init__(
        self,
        pheromone_store: Any,
        resource_ledger: Any = None,
        consequence_memory_ref: Any = None,
    ) -> None:
        """Initialise the gate.

        Args:
            pheromone_store: A ``TraceField`` instance (standalone / test usage) or a
                ``PheromoneStore`` instance (kernel usage).  Passing any other type
                raises ``TypeError``.
            resource_ledger: Optional object with a ``can_afford(cost) -> bool`` method.
                When provided, the gate performs an internal budget pre-check inside
                ``evaluate``.  The kernel passes ``None`` here and supplies
                ``budget_approved`` explicitly in the four-argument ``evaluate`` call.
            consequence_memory_ref: Optional object with a
                ``recent_failures(agent_id, window) -> int`` method.  Used to apply a
                trust penalty when the agent has three or more recent failures.
        """
        from codomyrmex.colony_kernel.pheromone_store import PheromoneStore

        if not isinstance(pheromone_store, (TraceField, PheromoneStore)):
            raise TypeError(
                f"pheromone_store must be a TraceField or PheromoneStore instance, "
                f"got {type(pheromone_store).__name__!r}. "
                "Pass a TraceField or PheromoneStore."
            )
        if resource_ledger is not None and not callable(
            getattr(resource_ledger, "can_afford", None)
        ):
            raise TypeError(
                "resource_ledger must have a callable 'can_afford' method, "
                f"but {type(resource_ledger).__name__!r} does not."
            )
        self._pheromone = pheromone_store
        self._ledger = resource_ledger
        self._memory = consequence_memory_ref

    # ------------------------------------------------------------------
    # Witness state (pure read — no side effects)
    # ------------------------------------------------------------------

    def witness_state(self, proposal: ActionProposal) -> dict[str, Any]:
        """Return a read-only diagnostic snapshot of the proposal + pheromone field.

        Does NOT modify any state.  The returned dict contains every field from the
        proposal, the current pheromone readings at the target, and completeness flags.

        Returns:
            Dict with keys: proposal_id, agent_id, agent_type, action_type, target,
            rationale, expected_outcome, rollback_plan, evidence, budget_estimate,
            created_at, pheromone_readings, completeness_flags.
        """
        pheromone_readings = {
            "risk": _sense_pheromone(self._pheromone, proposal.target, SignalType.RISK),
            "failure": _sense_pheromone(
                self._pheromone, proposal.target, SignalType.FAILURE
            ),
            "success": _sense_pheromone(
                self._pheromone, proposal.target, SignalType.SUCCESS
            ),
            "human_priority": _sense_pheromone(
                self._pheromone, proposal.target, SignalType.HUMAN_PRIORITY
            ),
        }
        completeness_flags = {
            "has_rollback_plan": bool(proposal.rollback_plan.strip()),
            "has_evidence": bool(proposal.evidence),
            "has_expected_outcome": bool(proposal.expected_outcome.strip()),
        }
        return {
            "proposal_id": proposal.proposal_id,
            "agent_id": proposal.agent_id,
            "agent_type": proposal.agent_type,
            "action_type": proposal.action_type,
            "target": proposal.target,
            "rationale": proposal.rationale,
            "expected_outcome": proposal.expected_outcome,
            "rollback_plan": proposal.rollback_plan,
            "evidence": proposal.evidence,
            "budget_estimate": proposal.budget_estimate,
            "created_at": proposal.created_at,
            "pheromone_readings": pheromone_readings,
            "completeness_flags": completeness_flags,
        }

    # ------------------------------------------------------------------
    # Primary evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        proposal: ActionProposal,
        profile: AgentTrustProfile,
        findings: list[FalsificationFinding] | None = None,
        budget_approved: bool | None = None,
    ) -> GateResult:
        """Compute the gate decision for *proposal*.

        Supports two calling styles:

        * **Two-argument (standalone)**: ``evaluate(proposal, profile)``
          The gate performs its own budget pre-check via
          ``resource_ledger.can_afford``.  ``findings`` defaults to ``[]``.
          Budget fail returns an immediate REFUSE (gate_score=0.0).
        * **Four-argument (kernel)**: ``evaluate(proposal, profile, findings, budget_approved)``
          The caller supplies pre-computed findings and a budget verdict.
          Budget fail returns HOLD (allows re-queue after period reset).

        Returns:
            GateResult with decision, gate_score, reason, required_evidence,
            budget_approved, and falsification_severity.
        """
        if findings is None:
            findings = []

        # Track whether budget_approved was supplied by the caller (kernel/4-arg style)
        # or computed internally (standalone/2-arg style).
        # The distinction affects the budget-fail decision: HOLD (kernel) vs REFUSE (standalone).
        _caller_supplied_budget = budget_approved is not None

        # --- internal budget check (standalone style) ---
        if budget_approved is None:
            if self._ledger is not None:
                budget_approved = bool(self._ledger.can_afford(proposal.budget_estimate))
            else:
                budget_approved = True

        # --- falsification penalty ---
        falsification_penalty = 0.0
        if findings:
            falsification_penalty = max(
                _FALSIFICATION_WEIGHT.get(f.severity, 0.0) for f in findings
            )

        # ----------------------------------------------------------------
        # Hard override 1 — budget fail
        # Standalone (2-arg) style: REFUSE immediately (gate_score=0.0)
        # Kernel (4-arg) style: HOLD (caller manages requeue)
        # ----------------------------------------------------------------
        if not budget_approved:
            budget_decision = GateDecision.REFUSE if not _caller_supplied_budget else GateDecision.HOLD
            return GateResult(
                decision=budget_decision,
                gate_score=0.0,
                reason=(
                    f"Budget ceiling exceeded for proposal {proposal.proposal_id!r}. "
                    f"budget_estimate={proposal.budget_estimate}. "
                    "Re-queue after budget period resets."
                ),
                required_evidence=["budget_recovered"],
                budget_approved=False,
                falsification_severity=falsification_penalty,
            )

        # ----------------------------------------------------------------
        # Hard override 2 — SANDBOX role
        # ----------------------------------------------------------------
        if profile.role == AgentRole.SANDBOX:
            return GateResult(
                decision=GateDecision.REFUSE,
                gate_score=0.0,
                reason="SANDBOX role: no write-path gate passes",
                required_evidence=[
                    "earn_higher_role_via_trust_growth",
                    "accumulate_accepted_proposals",
                ],
                budget_approved=budget_approved,
                falsification_severity=falsification_penalty,
            )

        # ----------------------------------------------------------------
        # Hard override 3 — trust below hard floor
        # ----------------------------------------------------------------
        if profile.trust_score < _TRUST_HARD_FLOOR:
            return GateResult(
                decision=GateDecision.REFUSE,
                gate_score=0.0,
                reason=(
                    f"Agent trust score {profile.trust_score:.3f} is below the "
                    f"hard floor of {_TRUST_HARD_FLOOR}. Accumulate accepted proposals "
                    "to raise trust before re-submitting."
                ),
                required_evidence=["trust_above_0.30"],
                budget_approved=budget_approved,
                falsification_severity=falsification_penalty,
            )

        # ----------------------------------------------------------------
        # Hard override 4 — CRITICAL falsification finding
        # ----------------------------------------------------------------
        if (
            falsification_penalty
            >= _FALSIFICATION_WEIGHT[FalsificationSeverity.CRITICAL]
        ):
            critical = [f for f in findings if f.severity == FalsificationSeverity.CRITICAL]
            return GateResult(
                decision=GateDecision.REFUSE,
                gate_score=0.0,
                reason=f"CRITICAL falsification finding: {critical[0].claim}",
                required_evidence=[f.remediation for f in critical if f.remediation],
                budget_approved=budget_approved,
                falsification_severity=falsification_penalty,
            )

        # ----------------------------------------------------------------
        # Scoring path
        # ----------------------------------------------------------------
        snapshot = self.witness_state(proposal)
        pheromone_readings = snapshot["pheromone_readings"]
        completeness_flags = snapshot["completeness_flags"]

        # budget_ok
        budget_ok = 1.0  # already cleared the hard override above

        # risk_ok — based on combined RISK pressure at target
        risk_pressure = pheromone_readings["risk"]
        if risk_pressure >= _HIGH_RISK_THRESHOLD:
            risk_ok = 0.0
        elif risk_pressure >= _MED_RISK_THRESHOLD:
            risk_ok = 0.5
        else:
            risk_ok = 1.0

        # trust_ok — tiered 0.5 / 1.0 with optional failure penalty
        if profile.trust_score >= 0.6:
            trust_ok = 1.0
        else:
            trust_ok = 0.5

        # Apply failure penalty if consequence_memory_ref is wired and agent has >= 3 failures
        recent_fail_count = 0
        if self._memory is not None:
            recent_fail_count = self._memory.recent_failures(proposal.agent_id)
        if recent_fail_count >= 3:
            trust_ok = max(0.0, trust_ok - _FAILURE_PENALTY)

        # completeness — count missing fields
        missing_count = sum(
            1
            for flag in (
                completeness_flags["has_rollback_plan"],
                completeness_flags["has_evidence"],
                completeness_flags["has_expected_outcome"],
            )
            if not flag
        )
        completeness = max(0.0, 1.0 - missing_count * _MISSING_FIELD_PENALTY)

        # composite gate score (no falsification multiplier — already handled as hard override)
        gate_score = (
            budget_ok * 0.30
            + risk_ok * 0.30
            + trust_ok * 0.25
            + completeness * 0.15
        )
        gate_score = max(0.0, min(1.0, gate_score))

        # ----------------------------------------------------------------
        # Reason composition — note all issues so callers can diagnose
        # ----------------------------------------------------------------
        issues: list[str] = []
        if risk_ok < 1.0:
            issues.append(
                f"high-risk pheromone pressure at target ({risk_pressure:.2f})"
            )
        if trust_ok < 0.5 or (trust_ok < 1.0 and recent_fail_count >= 3):
            issues.append(
                f"agent trust reduced (score={profile.trust_score:.3f}"
                + (f", recent_failures={recent_fail_count}" if recent_fail_count >= 3 else "")
                + ")"
            )
        if not completeness_flags["has_rollback_plan"]:
            issues.append("missing: rollback_plan")
        if not completeness_flags["has_evidence"]:
            issues.append("missing: evidence")
        if not completeness_flags["has_expected_outcome"]:
            issues.append("missing: expected_outcome")
        if findings:
            issues.append(
                f"falsification findings: {len(findings)} "
                f"(max severity {max(f.severity.value for f in findings)})"
            )

        # ----------------------------------------------------------------
        # Threshold routing
        # ----------------------------------------------------------------
        if gate_score >= _GATE_SCORE_EXECUTE:
            decision = GateDecision.EXECUTE
            if issues:
                reason = (
                    f"gate score {gate_score:.3f} >= execute threshold. "
                    f"Warnings — {'; '.join(issues)}"
                )
            else:
                reason = f"gate score {gate_score:.3f} >= execute threshold"
            required: list[str] = []
        elif gate_score >= _GATE_SCORE_HOLD:
            decision = GateDecision.HOLD
            reason = (
                f"gate score {gate_score:.3f} below execute threshold "
                f"({_GATE_SCORE_EXECUTE}). "
                "Re-evaluate after trust growth or evidence addition."
            )
            if issues:
                reason += f" Reasons: {'; '.join(issues)}"
            required = ["additional_evidence", "trust_improvement"]
        else:
            decision = GateDecision.REFUSE
            reason = (
                f"gate score {gate_score:.3f} is below the REFUSE threshold "
                f"({_GATE_SCORE_HOLD})."
            )
            if issues:
                reason += f" Reasons: {'; '.join(issues)}"
            required = []

        return GateResult(
            decision=decision,
            gate_score=gate_score,
            reason=reason,
            required_evidence=required,
            budget_approved=budget_approved,
            falsification_severity=falsification_penalty,
        )


__all__ = [
    "_GATE_SCORE_EXECUTE",
    "_GATE_SCORE_HOLD",
    "ActuationGate",
]
