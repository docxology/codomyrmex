"""Colony Kernel — integration class wiring all Colony Control Plane subsystems.

The kernel owns the lifecycle of every subsystem and exposes the high-level
propose_action / record_outcome / colony_status / tick API that callers use
without needing to know which subsystem handles each concern.

Subsystem implementations live in their canonical standalone modules:
    pheromone_store.py, resource_ledger.py, actuation_gate.py,
    consequence_memory.py, role_adapter.py, pruning_daemon.py,
    falsification_worker.py

This module imports and re-exports all subsystem classes so existing callers
can continue to use ``from codomyrmex.colony_kernel.kernel import X``.

Dependency graph:
    ColonyKernelConfig
    └── ColonyKernel
        ├── PheromoneStore      (pheromone_store.py — wraps TraceField, ColonySignal)
        ├── ResourceLedger      (resource_ledger.py — tracks consumed vs budgeted)
        ├── ActuationGate       (actuation_gate.py — additive score + hard overrides)
        ├── ConsequenceMemory   (consequence_memory.py — SQLite consequence log)
        ├── RoleAdapter         (role_adapter.py — infers AgentRole from history)
        ├── PruningDaemon       (pruning_daemon.py — identifies stale modules)
        └── FalsificationWorker (falsification_worker.py — adversarial checks)
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.actuation_gate import (
    _GATE_SCORE_EXECUTE,
    _GATE_SCORE_HOLD,
    ActuationGate,
)
from codomyrmex.colony_kernel.attestation import (
    AttestationLedger,
    HMACSigner,
    LedgerEvent,
    LedgerValidationResult,
)
from codomyrmex.colony_kernel.consequence_memory import ConsequenceMemory
from codomyrmex.colony_kernel.falsification_worker import FalsificationWorker
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentRole,
    AgentTrustProfile,
    ColonySignal,
    ConsequenceRecord,
    DecayRate,
    FalsificationFinding,
    FalsificationSeverity,
    GateDecision,
    GateResult,
    PruningCandidate,
    ResourceCost,
    SignalSource,
    SignalType,
    compute_trust_delta,
    make_trace_key,
)
from codomyrmex.colony_kernel.pheromone_store import PheromoneStore
from codomyrmex.colony_kernel.pruning_daemon import PruningDaemon

# ---------------------------------------------------------------------------
# Subsystem imports — canonical implementations in standalone modules
# ---------------------------------------------------------------------------
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget, ResourceLedger
from codomyrmex.colony_kernel.role_adapter import RoleAdapter

# ---------------------------------------------------------------------------
# ColonyKernelConfig
# ---------------------------------------------------------------------------


@dataclass
class ColonyKernelConfig:
    """Configuration for a ColonyKernel instance.

    ``db_path`` is the SQLite file path for ConsequenceMemory persistence.
    Pass ``db_path=":memory:"`` for ephemeral / test usage.
    ``repo_root`` is an informational path used by PruningDaemon to resolve
    module paths; it does not need to point at a real directory.

    ``budget`` defaults to ``None``; when ``None``, ``__post_init__`` tries
    to load the budget from ``config/colony_kernel/kernel.yaml`` via
    ``config_loader.default_budget_from_yaml()``.  If the YAML file is absent
    or the import fails for any reason, it falls back to ``ResourceBudget()``.
    Pass an explicit ``ResourceBudget`` instance to skip YAML loading entirely.
    """

    db_path: str = ":memory:"
    repo_root: str = "."
    budget: ResourceBudget | None = field(default=None)
    pheromone_config: StigmergyConfig = field(default_factory=StigmergyConfig)
    attestation_mode: str = "disabled"
    attestation_db_path: str = ":memory:"
    attestation_secret_key: bytes | str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Resolve *budget* from YAML when the caller left it as ``None``."""
        if self.attestation_mode not in {"disabled", "optional", "required"}:
            raise ValueError(
                "attestation_mode must be one of disabled, optional, or required"
            )
        if self.budget is None:
            try:
                from codomyrmex.colony_kernel.config_loader import (
                    default_budget_from_yaml,
                )

                self.budget = default_budget_from_yaml()
            except Exception:
                # Never let config loading crash the kernel.
                self.budget = ResourceBudget()


# ---------------------------------------------------------------------------
# PheromoneStore
# ---------------------------------------------------------------------------


class ColonyKernel:
    """Top-level integration class: wires all Colony Control Plane subsystems.

    Instantiate once per process. All subsystem state is owned by the kernel;
    callers interact only through the public API methods.

    Lifecycle:
        kernel = ColonyKernel()           # all subsystems ready
        result = kernel.propose_action(p) # falsify → gate → budget check
        record = kernel.record_outcome(p, outcome, tests_passed)
        status = kernel.colony_status()   # dashboard snapshot
        kernel.tick()                     # evaporate pheromones / reset period
    """

    def __init__(self, config: ColonyKernelConfig | None = None) -> None:
        """Initialise all subsystems from *config* (uses sensible defaults if None)."""
        self._config = config or ColonyKernelConfig()
        self._tick_count: int = 0
        self._attestation_proposals: dict[str, LedgerEvent] = {}
        self._attestation_verdicts: dict[str, LedgerEvent] = {}
        self._attestation_authorizations: dict[str, LedgerEvent] = {}
        self._attestation_executions: dict[str, LedgerEvent] = {}
        self._attestation_run_id = f"kernel-{uuid.uuid4().hex}"

        self.attestation_ledger: AttestationLedger | None = None
        if self._config.attestation_mode != "disabled":
            signer = (
                HMACSigner(self._config.attestation_secret_key, key_id="kernel")
                if self._config.attestation_secret_key is not None
                else None
            )
            self.attestation_ledger = AttestationLedger(
                self._config.attestation_db_path,
                signer=signer,
            )

        self.pheromone_store = PheromoneStore(config=self._config.pheromone_config)
        self.resource_ledger = ResourceLedger(budget=self._config.budget)
        self.consequence_memory = ConsequenceMemory(db_path=self._config.db_path)
        self.actuation_gate = ActuationGate(
            pheromone_store=self.pheromone_store,
            consequence_memory_ref=self.consequence_memory,
        )
        self.role_adapter = RoleAdapter()
        self.pruning_daemon = PruningDaemon(
            pheromone_store=self.pheromone_store,
            repo_root=self._config.repo_root,
        )
        self.falsification_worker = FalsificationWorker(
            pheromone_store=self.pheromone_store
        )

    # ------------------------------------------------------------------
    # Core pipeline
    # ------------------------------------------------------------------

    def propose_action(self, proposal: ActionProposal) -> GateResult:
        """Full pipeline: falsification → budget check → gate → GateResult.

        Steps:
        1. Run FalsificationWorker to collect adversarial findings.
        2. Check ResourceLedger budget against the proposal's estimate.
        3. Load (or lazily create) the agent's trust profile; refresh role.
        4. Evaluate ActuationGate with findings, budget status, and profile.
        5. On REFUSE: deposit a FAILURE pheromone at the agent's target so
           the signal decays into future evaluations.

        Does NOT consume budget. A later, caller-initiated ``record_outcome``
        call consumes a supplied valid cost mapping or falls back to the
        proposal estimate. The kernel does not attest that execution occurred.
        """
        # Step 1 — falsification
        findings = self.falsification_worker.analyze(proposal)

        # Step 2 — budget pre-check (non-consuming)
        budget_approved, _reason = self.resource_ledger.check_budget(
            proposal.budget_estimate
        )

        # Step 3 — profile + role refresh (increment proposal counter)
        profile = self.consequence_memory.get_profile(proposal.agent_id)
        profile.total_proposals += 1
        self.consequence_memory.save_profile(profile)
        self.role_adapter.update(profile)

        # Step 4 — gate evaluation
        result = self.actuation_gate.evaluate(
            proposal=proposal,
            profile=profile,
            findings=findings,
            budget_approved=budget_approved,
        )

        if self.attestation_ledger is not None:
            proposal_id = proposal.proposal_id
            proposal_event = self.attestation_ledger.record_proposal(
                self._attestation_run_id,
                proposal.agent_id,
                _dataclass_to_dict(proposal),
            )
            verdict_event = self.attestation_ledger.record_gate_verdict(
                self._attestation_run_id,
                proposal.agent_id,
                proposal_event,
                result.decision.value,
                _dataclass_to_dict(result),
            )
            self._attestation_proposals[proposal_id] = proposal_event
            self._attestation_verdicts[proposal_id] = verdict_event

        # Step 5 — deposit signals based on outcome
        if result.decision == GateDecision.REFUSE:
            signal = ColonySignal(
                location=proposal.target,
                signal_type=SignalType.FAILURE,
                strength=1.0 + result.falsification_severity * 3.0,
                decay_rate=DecayRate.NORMAL,
                source=SignalSource.AGENT,
                evidence={
                    "proposal_id": proposal.proposal_id,
                    "reason": result.reason,
                },
            )
            self.pheromone_store.deposit(signal, trust_factor=profile.trust_score)

        # Deposit RISK signal when falsification findings exist at MEDIUM+, so
        # the gate's risk_pressure reading reflects live adversarial concern
        # at the target location — even if the proposal passed the gate.
        elif findings:
            risk_findings = [
                f
                for f in findings
                if f.severity.value in ("medium", "high", "critical")
            ]
            if risk_findings:
                risk_strength = min(3.0, len(risk_findings) * 0.8)
                risk_signal = ColonySignal(
                    location=proposal.target,
                    signal_type=SignalType.RISK,
                    strength=risk_strength,
                    decay_rate=DecayRate.FAST,
                    source=SignalSource.AGENT,
                    evidence={
                        "proposal_id": proposal.proposal_id,
                        "finding_count": len(risk_findings),
                        "max_severity": max(f.severity.value for f in risk_findings),
                    },
                )
                self.pheromone_store.deposit(
                    risk_signal, trust_factor=profile.trust_score
                )

        return result

    def record_outcome(
        self,
        proposal: ActionProposal,
        outcome: dict[str, Any],
        tests_passed: bool,
        human_feedback: str | None = None,
    ) -> ConsequenceRecord:
        """Record a caller-reported consequence and update pheromones.

        Parameters
        ----------
        proposal:
            The ActionProposal associated with the report. This method does not
            verify a prior EXECUTE verdict or that execution occurred.
        outcome:
            Free-form caller report describing what happened.
        tests_passed:
            Whether post-action tests passed.
        human_feedback:
            Optional operator feedback string; parsed to a float in [-1, 1]:
            "good" / "approve" / "yes" / "+" → +1.0
            "bad" / "reject" / "no" / "-" → -1.0
            A numeric string (e.g. "0.5") → parsed directly.
            None or unrecognised → 0.0

        Pheromone updates:
          - tests_passed=True  → reinforce SUCCESS at target
          - tests_passed=False → deposit FAILURE at target (FAST decay)
        """
        if (
            self._config.attestation_mode == "required"
            and proposal.proposal_id not in self._attestation_executions
        ):
            raise ValueError(
                "attestation_mode='required' needs an authorized execution receipt "
                "before recording an outcome"
            )

        # Parse human_feedback string to float
        hf_float = _parse_human_feedback(human_feedback)

        # Build actual_outcome string
        actual_outcome = outcome.get("summary", str(outcome))
        repair_needed = bool(outcome.get("repair_needed", False))
        action_taken = outcome.get("action_taken", proposal.action_type)

        record = ConsequenceRecord(
            proposal=proposal,
            action_taken=action_taken,
            actual_outcome=actual_outcome,
            tests_passed=tests_passed,
            human_feedback=hf_float,
            repair_needed=repair_needed,
        )
        # trust_delta left at 0.0 → ConsequenceMemory.record computes it
        record = self.consequence_memory.record(record)

        # Consume budget with proposal's estimate as a proxy for actual cost
        # (callers may pass actual_cost in outcome["cost"] if available)
        actual_cost_dict = outcome.get("cost", {})
        if actual_cost_dict and isinstance(actual_cost_dict, dict):
            try:
                actual_cost = ResourceCost(**actual_cost_dict)
            except (TypeError, ValueError):
                actual_cost = proposal.budget_estimate
        else:
            actual_cost = proposal.budget_estimate
        self.resource_ledger.consume(actual_cost)

        # Pheromone update
        if tests_passed:
            self.pheromone_store.reinforce(proposal.target, SignalType.SUCCESS)
        else:
            fail_signal = ColonySignal(
                location=proposal.target,
                signal_type=SignalType.FAILURE,
                strength=2.0,
                decay_rate=DecayRate.FAST,
                source=SignalSource.TEST,
                evidence={
                    "proposal_id": proposal.proposal_id,
                    "action_type": proposal.action_type,
                    "actual_outcome": actual_outcome,
                },
            )
            self.pheromone_store.deposit(fail_signal)

        # Also deposit a SUCCESS trace on the target when outcome is clean
        if tests_passed and not repair_needed:
            success_signal = ColonySignal(
                location=proposal.target,
                signal_type=SignalType.SUCCESS,
                strength=1.5,
                decay_rate=DecayRate.SLOW,
                source=SignalSource.TEST,
                evidence={"proposal_id": proposal.proposal_id},
            )
            self.pheromone_store.deposit(success_signal)

        # Update agent DEPENDENCY pheromone to track module usage
        dep_signal = ColonySignal(
            location=proposal.target,
            signal_type=SignalType.DEPENDENCY,
            strength=0.5,
            decay_rate=DecayRate.SLOW,
            source=SignalSource.RUNTIME,
            evidence={"agent_id": proposal.agent_id},
        )
        self.pheromone_store.deposit(dep_signal)

        # Refresh role based on updated trust and persist if it changed
        updated_profile = self.consequence_memory.get_profile(proposal.agent_id)
        role_changed = self.role_adapter.update(updated_profile)
        if role_changed:
            self.consequence_memory.save_profile(updated_profile)

        return record

    # ------------------------------------------------------------------
    # Optional authenticated execution path
    # ------------------------------------------------------------------

    def authorize_execution(self, proposal_id: str, actor_id: str) -> LedgerEvent:
        """Authorize one proposal after an attested EXECUTE verdict."""
        if self.attestation_ledger is None:
            raise ValueError("attestation is disabled for this kernel")
        verdict = self._attestation_verdicts.get(proposal_id)
        if verdict is None:
            raise ValueError(
                f"no attested gate verdict exists for proposal {proposal_id}"
            )
        authorization = self.attestation_ledger.authorize_execution(
            verdict.run_id, actor_id, verdict
        )
        self._attestation_authorizations[proposal_id] = authorization
        return authorization

    def record_execution_receipt(
        self,
        proposal_id: str,
        receipt: dict[str, Any],
        actor_id: str = "executor",
    ) -> LedgerEvent:
        """Record an execution receipt linked to a prior authorization."""
        if self.attestation_ledger is None:
            raise ValueError("attestation is disabled for this kernel")
        authorization = self._attestation_authorizations.get(proposal_id)
        if authorization is None:
            raise ValueError(f"proposal {proposal_id} has no execution authorization")
        execution = self.attestation_ledger.record_execution(
            authorization.run_id, actor_id, authorization, receipt
        )
        self._attestation_executions[proposal_id] = execution
        return execution

    def record_attested_outcome(
        self,
        proposal: ActionProposal,
        outcome: dict[str, Any],
        tests_passed: bool,
        human_feedback: str | None = None,
        actor_id: str = "observer",
    ) -> ConsequenceRecord:
        """Record an outcome only after linking it to an execution receipt."""
        if self.attestation_ledger is None:
            raise ValueError("attestation is disabled for this kernel")
        execution = self._attestation_executions.get(proposal.proposal_id)
        if execution is None:
            raise ValueError(
                f"proposal {proposal.proposal_id} has no execution receipt"
            )
        self.attestation_ledger.record_outcome(
            execution.run_id, actor_id, execution, outcome
        )
        return self.record_outcome(
            proposal,
            outcome,
            tests_passed,
            human_feedback=human_feedback,
        )

    def attestation_status(
        self, run_id: str | None = None
    ) -> LedgerValidationResult | None:
        """Return the ledger validation result for the current run, if enabled."""
        if self.attestation_ledger is None:
            return None
        if run_id is None:
            run_id = self._attestation_run_id
        return self.attestation_ledger.validate(run_id)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def agent_profile(self, agent_id: str) -> AgentTrustProfile:
        """Return the current AgentTrustProfile for *agent_id*.

        Creates a SANDBOX default profile if the agent is unknown.
        """
        return self.consequence_memory.get_profile(agent_id)

    def colony_status(self) -> dict[str, Any]:
        """Return a dashboard snapshot of the colony's current state.

        Keys:
          tick_count               — number of ticks elapsed since kernel init
          pheromone_summary        — top-10 strongest signals
          budget_usage             — current period consumption vs ceiling
          role_distribution        — agent count per role
          recent_consequences      — last 10 consequence records
          pruning_candidates_count — number of stale modules flagged
        """
        return {
            "tick_count": self._tick_count,
            "pheromone_summary": {
                "total_signals": len(self.pheromone_store.top_signals(k=200)),
                "top_signals": self.pheromone_store.top_signals(k=10),
            },
            "budget_usage": self.resource_ledger.usage_summary(),
            "role_distribution": self.consequence_memory.role_distribution(),
            "recent_consequences": self.consequence_memory.recent_consequences(
                limit=10
            ),
            "pruning_candidates_count": self.pruning_daemon._last_scan_count,
        }

    # ------------------------------------------------------------------
    # Pruning
    # ------------------------------------------------------------------

    def pruning_report(
        self, module_registry: dict[str, dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Run the PruningDaemon and return its report.

        Args:
            module_registry: Optional dict mapping dotted module paths to dicts
                with keys ``last_used`` (float), ``call_count`` (int),
                ``duplicate_of`` (str | None).  When ``None``, the method
                derives a minimal registry from the pheromone field's
                DEPENDENCY signals (each traced location becomes an entry).

        Returns:
            A dict with:
            - ``candidates``: list of serialised ``PruningCandidate`` dicts
            - ``total_candidates``: int count
            - ``generated_at``: float Unix timestamp
        """
        if module_registry is None:
            # Derive registry from pheromone field: every location with a
            # DEPENDENCY signal is considered "used" at the signal's
            # last_reinforced timestamp.
            module_registry = {}
            for marker in self.pheromone_store._field.top_k(k=10_000):
                if ":dependency" in marker.key:
                    location = marker.key.rsplit(":", 1)[0]
                    module_registry[location] = {
                        "last_used": marker.updated_at,
                        "call_count": 1,
                        "duplicate_of": None,
                    }
        candidates = self.pruning_daemon.scan(module_registry)
        return {
            "candidates": [_dataclass_to_dict(c) for c in candidates],
            "total_candidates": len(candidates),
            "generated_at": time.time(),
        }

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(self) -> None:
        """Advance one colony clock tick.

        - Evaporates all pheromone traces (removes those at floor strength).
        - Resets resource ledger period if the budget period has elapsed.
        - Increments the internal tick counter (queryable via colony_status).
        """
        self.pheromone_store.tick()
        # ResourceLedger auto-resets on _maybe_reset; force-reset only when
        # an explicit period boundary is crossed.  We check via the public API.
        self.resource_ledger._maybe_reset()
        self._tick_count += 1

    def calm_down(self, reason: str = "emergency_brake") -> dict[str, Any]:
        """Emergency brake — reset the colony to a quiescent state.

        Intended for use in a crisis (runaway agent loop, budget overflow,
        or unexpected cascading failures).  Callers should pass a descriptive
        *reason* string so the reset is logged.

        Effects:
          - Clears all pheromone signals from the store.
          - Resets the resource ledger's accumulated spend.
          - Resets the tick counter to 0.

        Does NOT clear consequence memory (historical records are preserved
        for post-mortem analysis) nor does it reset agent trust scores.

        Args:
            reason: Human-readable explanation for the emergency reset.  Not
                    used computationally; surfaced in the returned status dict.

        Returns:
            dict with keys ``reset_reason`` (str), ``tick_count_before`` (int),
            ``signals_cleared`` (int).
        """
        _logger = logging.getLogger(__name__)

        tick_before = self._tick_count
        # Count signals before clearing
        signals_cleared = len(self.pheromone_store)

        # Clear the pheromone field by evaporating everything to zero
        # We drain by setting all strengths to floor — tick enough times
        # (up to 1000) or directly zero out markers.
        for key in list(self.pheromone_store._field._markers.keys()):
            del self.pheromone_store._field._markers[key]
        self.pheromone_store._key_evaporation.clear()

        # Reset the ledger period
        self.resource_ledger.reset_period()

        # Reset tick counter
        self._tick_count = 0

        _logger.warning(
            "colony_kernel.calm_down triggered: reason=%r, tick_count_before=%d, "
            "signals_cleared=%d",
            reason,
            tick_before,
            signals_cleared,
        )

        return {
            "reset_reason": reason,
            "tick_count_before": tick_before,
            "signals_cleared": signals_cleared,
        }


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _dataclass_to_dict(obj: Any) -> Any:
    """Recursively convert dataclass instances (and nested structures) to dicts."""
    import dataclasses

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {
            f.name: _dataclass_to_dict(getattr(obj, f.name))
            for f in dataclasses.fields(obj)
        }
    if isinstance(obj, list):
        return [_dataclass_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    if hasattr(obj, "value"):  # Enum
        return obj.value
    return obj


def _parse_human_feedback(raw: str | None) -> float:
    """Convert a free-text operator feedback string to a float in [-1.0, 1.0].

    Recognised positive tokens: "good", "approve", "yes", "+"
    Recognised negative tokens: "bad", "reject", "no", "-"
    Numeric strings are clamped to [-1.0, 1.0].
    Everything else returns 0.0.
    """
    if raw is None:
        return 0.0
    normalised = raw.strip().lower()
    if normalised in {"good", "approve", "yes", "+"}:
        return 1.0
    if normalised in {"bad", "reject", "no", "-"}:
        return -1.0
    try:
        value = float(normalised)
        return max(-1.0, min(1.0, value))
    except ValueError:
        return 0.0


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    # Subsystem classes (exported so tests and advanced callers can type-hint them)
    "ActuationGate",
    "ColonyKernel",
    "ColonyKernelConfig",
    "ConsequenceMemory",
    "FalsificationWorker",
    "PheromoneStore",
    "PruningDaemon",
    "ResourceBudget",
    "ResourceLedger",
    "RoleAdapter",
]
