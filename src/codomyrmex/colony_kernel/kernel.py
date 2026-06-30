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
        ├── ActuationGate       (actuation_gate.py — trust × pressure → GateDecision)
        ├── ConsequenceMemory   (consequence_memory.py — SQLite consequence log)
        ├── RoleAdapter         (role_adapter.py — infers AgentRole from history)
        ├── PruningDaemon       (pruning_daemon.py — identifies stale modules)
        └── FalsificationWorker (falsification_worker.py — adversarial checks)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.actuation_gate import (
    _GATE_SCORE_EXECUTE,
    _GATE_SCORE_HOLD,
    ActuationGate,
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

    def __post_init__(self) -> None:
        """Resolve *budget* from YAML when the caller left it as ``None``."""
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

        self.pheromone_store = PheromoneStore(config=self._config.pheromone_config)
        self.resource_ledger = ResourceLedger(budget=self._config.budget)
        self.actuation_gate = ActuationGate(pheromone_store=self.pheromone_store)
        self.consequence_memory = ConsequenceMemory(db_path=self._config.db_path)
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

        Does NOT consume budget; ``record_outcome`` calls ``consume`` with
        the actual cost after execution.
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

        # Step 5 — deposit FAILURE pheromone on refusal
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

        return result

    def record_outcome(
        self,
        proposal: ActionProposal,
        outcome: dict[str, Any],
        tests_passed: bool,
        human_feedback: str | None = None,
    ) -> ConsequenceRecord:
        """Record the consequence of an executed action and update pheromones.

        Parameters
        ----------
        proposal:
            The original ActionProposal that was executed.
        outcome:
            Free-form dict describing what actually happened.
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
          pheromone_summary    — top-10 strongest signals
          budget_usage         — current period consumption vs ceiling
          role_distribution    — agent count per role
          recent_consequences  — last 10 consequence records
          pruning_candidates_count — number of stale modules flagged
        """
        return {
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
        """
        self.pheromone_store.tick()
        # ResourceLedger auto-resets on _maybe_reset; force-reset only when
        # an explicit period boundary is crossed.  We check via the public API.
        self.resource_ledger._maybe_reset()


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
