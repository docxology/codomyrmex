"""Colony Kernel shared contract — value objects and enums for all subsystems.

All Colony Kernel modules import from here. No cross-module imports between
subsystems; the dependency graph is a star with models.py at the centre.

No external dependencies beyond stdlib.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Signal taxonomy
# ---------------------------------------------------------------------------


class SignalType(Enum):
    """Pheromone signal classification.

    Maps to ecological function:
    - FAILURE: trail avoidance (this path broke something)
    - SUCCESS: trail amplification (this path worked)
    - RISK: caution marker (tread carefully near this location)
    - NEED: resource request (this location requires attention)
    - DEPENDENCY: usage trace (this module is actively imported / called)
    - HUMAN_PRIORITY: operator-injected signal (highest trust weight)
    """

    FAILURE = "failure"
    SUCCESS = "success"
    RISK = "risk"
    NEED = "need"
    DEPENDENCY = "dependency"
    HUMAN_PRIORITY = "human_priority"


class DecayRate(Enum):
    """Per-signal evaporation multiplier applied on each tick.

    The base evaporation_per_tick from StigmergyConfig is multiplied by
    this factor. FAST signals disappear quickly (urgent, transient events);
    SLOW signals persist (long-term structural markers).
    """

    FAST = 3.0  # 0.3/tick at default base rate — urgent/transient
    NORMAL = 1.0  # 0.1/tick at default base rate
    SLOW = 0.2  # 0.02/tick at default base rate — structural/persistent


class SignalSource(Enum):
    """Who deposited this signal.

    Used by the gate to apply trust multipliers: HUMAN signals receive a 2×
    weight boost; TEST signals are the most objective evidence; AGENT signals
    are weighted by the depositing agent's trust score.
    """

    TEST = "test"  # CI/test runner outcome
    HUMAN = "human"  # Operator-injected
    AGENT = "agent"  # Autonomous agent action
    SECURITY = "security"  # Security scanner / SAST result
    RUNTIME = "runtime"  # Live execution telemetry


# ---------------------------------------------------------------------------
# Pheromone signal
# ---------------------------------------------------------------------------


@dataclass
class ColonySignal:
    """An enriched stigmergic trace with colony semantics.

    ``location`` is the target of the signal — typically a dotted module path
    (e.g. ``codomyrmex.git_operations.core``) or a file path. Compound keys
    in the backing TraceField are formed as ``f"{location}:{signal_type.value}"``.
    """

    location: str
    signal_type: SignalType
    strength: float
    decay_rate: DecayRate = DecayRate.NORMAL
    source: SignalSource = SignalSource.AGENT
    evidence: dict[str, Any] = field(default_factory=dict)
    last_reinforced: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.location:
            raise ValueError("ColonySignal.location must be non-empty")
        if self.strength < 0.0:
            raise ValueError("ColonySignal.strength must be non-negative")


# ---------------------------------------------------------------------------
# Resource budget
# ---------------------------------------------------------------------------


@dataclass
class ResourceCost:
    """Multi-dimensional cost estimate or actual cost of an action.

    All fields default to zero so callers only set what they track.
    The gate checks each dimension independently against per-agent budgets.

    risk_level, merge_risk, security_exposure are 0.0–1.0 fractions.
    """

    llm_calls: int = 0
    runtime_seconds: float = 0.0
    risk_level: float = 0.0
    human_attention_minutes: float = 0.0
    merge_risk: float = 0.0
    doc_debt: float = 0.0
    security_exposure: float = 0.0

    def __post_init__(self) -> None:
        for frac_field in ("risk_level", "merge_risk", "security_exposure"):
            v = getattr(self, frac_field)
            if not 0.0 <= v <= 1.0:
                raise ValueError(
                    f"ResourceCost.{frac_field} must be in [0.0, 1.0]; got {v}"
                )
        if self.llm_calls < 0:
            raise ValueError("ResourceCost.llm_calls must be non-negative")
        if self.runtime_seconds < 0.0:
            raise ValueError("ResourceCost.runtime_seconds must be non-negative")
        if self.human_attention_minutes < 0.0:
            raise ValueError(
                "ResourceCost.human_attention_minutes must be non-negative"
            )
        if self.doc_debt < 0.0:
            raise ValueError("ResourceCost.doc_debt must be non-negative")

    def __add__(self, other: ResourceCost) -> ResourceCost:
        return ResourceCost(
            llm_calls=self.llm_calls + other.llm_calls,
            runtime_seconds=self.runtime_seconds + other.runtime_seconds,
            risk_level=min(1.0, self.risk_level + other.risk_level),
            human_attention_minutes=self.human_attention_minutes
            + other.human_attention_minutes,
            merge_risk=min(1.0, self.merge_risk + other.merge_risk),
            doc_debt=self.doc_debt + other.doc_debt,
            security_exposure=min(
                1.0, self.security_exposure + other.security_exposure
            ),
        )


# ---------------------------------------------------------------------------
# Action proposal
# ---------------------------------------------------------------------------


@dataclass
class ActionProposal:
    """The atomic unit submitted to the actuation gate.

    ``proposal_id`` is auto-assigned if not provided.
    ``evidence`` is free-form context that falsification_worker and the gate
    may inspect (e.g. test IDs, PR URLs, error messages).
    """

    agent_id: str
    agent_type: str
    action_type: str  # e.g. "patch_file", "run_tests", "archive_module"
    target: str  # dotted module path or file path
    rationale: str
    expected_outcome: str
    budget_estimate: ResourceCost = field(default_factory=ResourceCost)
    rollback_plan: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        for required in (
            "agent_id",
            "agent_type",
            "action_type",
            "target",
            "rationale",
            "expected_outcome",
        ):
            if not getattr(self, required):
                raise ValueError(f"ActionProposal.{required} must be non-empty")


# ---------------------------------------------------------------------------
# Gate decision
# ---------------------------------------------------------------------------


class GateDecision(Enum):
    """Actuation gate verdict.

    EXECUTE: proceed immediately.
    HOLD: requeue for re-evaluation (budget recovery, trust growth, human review).
    REFUSE: rejected; deposits a FAILURE signal at agent location.
    """

    EXECUTE = "execute"
    HOLD = "hold"
    REFUSE = "refuse"


@dataclass
class GateResult:
    """Full gate verdict including score, reasoning, and approval status."""

    decision: GateDecision
    gate_score: float  # 0.0–1.0 composite score
    reason: str
    required_evidence: list[str] = field(default_factory=list)  # for HOLD
    budget_approved: bool = True
    falsification_severity: float = 0.0  # 0.0 = clean, 1.0 = do not execute


# ---------------------------------------------------------------------------
# Consequence record
# ---------------------------------------------------------------------------


@dataclass
class ConsequenceRecord:
    """Full record of a proposal's lifecycle: proposal → action → result.

    ``trust_delta`` is the net trust change computed from this outcome.
    Callers may pre-set it; if left at 0.0 the consequence_memory module
    computes it from ``tests_passed``, ``repair_needed``, and ``human_feedback``.

    ``human_feedback`` is -1.0 (bad) to +1.0 (good); 0.0 means no feedback yet.
    ``action_taken`` is a short description of what actually happened.
    """

    proposal: ActionProposal
    action_taken: str
    actual_outcome: str
    tests_passed: bool
    human_feedback: float = 0.0  # -1.0 .. +1.0
    repair_needed: bool = False
    trust_delta: float = 0.0
    recorded_at: float = field(default_factory=time.time)
    consequence_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not -1.0 <= self.human_feedback <= 1.0:
            raise ValueError("ConsequenceRecord.human_feedback must be in [-1.0, 1.0]")


# ---------------------------------------------------------------------------
# Agent role
# ---------------------------------------------------------------------------


class AgentRole(Enum):
    """Emergent role assignment based on consequence history.

    Roles are inferred by RoleAdapter — never hard-assigned at startup.
    Each role carries implicit permission constraints enforced by the gate.

    SANDBOX:     read-only; no write-path gate passes
    REPAIR_ANT:  patch, test-fix, doc-update
    MEMORY_ANT:  archive, index, summarise
    DISPATCHER:  delegate, coordinate, route
    GUARD_ANT:   security review, gate audit, archive authority
    """

    SANDBOX = "sandbox"
    REPAIR_ANT = "repair_ant"
    MEMORY_ANT = "memory_ant"
    DISPATCHER = "dispatcher"
    GUARD_ANT = "guard_ant"


@dataclass
class AgentTrustProfile:
    """Per-agent trust state updated by ConsequenceMemory after every outcome.

    ``trust_score`` is clamped to [0.0, 1.0].
    ``consequence_history`` holds the IDs of recent ConsequenceRecords in
    chronological order (most recent last).
    """

    agent_id: str
    role: AgentRole = AgentRole.SANDBOX
    trust_score: float = 0.1
    total_proposals: int = 0
    accepted_proposals: int = 0
    consequence_history: list[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not 0.0 <= self.trust_score <= 1.0:
            raise ValueError(
                f"AgentTrustProfile.trust_score must be in [0.0, 1.0]; got {self.trust_score}"
            )

    def apply_delta(self, delta: float) -> None:
        """Apply a trust delta, clamping the result to [0.0, 1.0]."""
        self.trust_score = max(0.0, min(1.0, self.trust_score + delta))
        self.last_updated = time.time()


# ---------------------------------------------------------------------------
# Pruning candidate
# ---------------------------------------------------------------------------


@dataclass
class PruningCandidate:
    """A module or symbol flagged as stale by PruningDaemon.

    ``confidence`` is 0.0–1.0; callers should only archive candidates with
    confidence ≥ 0.7.
    ``duplicate_of`` is the dotted path of the surviving equivalent, if known.
    ``reason`` is a human-readable explanation.
    """

    module_path: str
    last_used: float  # Unix timestamp; 0.0 if never used
    call_count: int
    duplicate_of: str | None
    reason: str
    confidence: float  # 0.0–1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"PruningCandidate.confidence must be in [0.0, 1.0]; got {self.confidence}"
            )


# ---------------------------------------------------------------------------
# Falsification finding
# ---------------------------------------------------------------------------


class FalsificationSeverity(Enum):
    """Severity classification for falsification findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FalsificationFinding:
    """A single adversarial finding from FalsificationWorker.

    ``claim`` is the specific assumption being attacked.
    ``attack_vector`` is the category of attack (see FalsificationWorker docstring).
    ``evidence`` is supporting data for the finding.
    ``remediation`` is a concrete suggestion to address the finding.
    """

    claim: str
    attack_vector: str
    severity: FalsificationSeverity
    evidence: dict[str, Any] = field(default_factory=dict)
    remediation: str = ""

    def __post_init__(self) -> None:
        if not self.claim:
            raise ValueError("FalsificationFinding.claim must be non-empty")
        if not self.attack_vector:
            raise ValueError("FalsificationFinding.attack_vector must be non-empty")


# ---------------------------------------------------------------------------
# Shared compound-key factory
# ---------------------------------------------------------------------------


def make_trace_key(location: str, signal_type: SignalType) -> str:
    """Return the canonical compound key for a pheromone trace.

    Convention (SPEC §1): ``"{location}:{signal_type.value}"``.
    Location comes first so that prefix-based queries over a location path
    remain efficient and consistent across all subsystems.

    This is the single authoritative implementation; all modules that build
    pheromone trace keys MUST call this function instead of formatting the
    key inline.

    Args:
        location: Dotted module path or file path (e.g.
            ``"codomyrmex.git_operations.core"``).
        signal_type: The :class:`SignalType` for this trace.

    Returns:
        A non-empty string of the form ``"{location}:{signal_type.value}"``.

    Raises:
        ValueError: If *location* is empty.
    """
    if not location:
        raise ValueError("make_trace_key: location must be non-empty")
    return f"{location}:{signal_type.value}"


# ---------------------------------------------------------------------------
# Canonical trust-delta computation
# ---------------------------------------------------------------------------

# Constants match SPEC.md §Trust Scoring Algorithm exactly.
_TRUST_DELTA_PASS: float = +0.04
_TRUST_DELTA_FAIL: float = -0.08
_TRUST_DELTA_REPAIR: float = -0.05
_TRUST_DELTA_HUMAN_WEIGHT: float = 0.03


def compute_trust_delta(record: ConsequenceRecord) -> float:
    """Compute the canonical trust delta for a consequence record.

    This is the single authoritative implementation (SPEC §Trust Scoring
    Algorithm). All subsystems that need to compute a trust delta — including
    :class:`ConsequenceMemory`, :class:`RoleAdapter`, and
    :mod:`mcp_tools` — MUST call this function instead of implementing the
    formula inline.

    Formula::

        delta  = +0.04  if record.tests_passed  else  -0.08
        delta += -0.05  if record.repair_needed
        delta +=  record.human_feedback * 0.03   # human_feedback ∈ [-1, +1]

    The result is **not** clamped here; ``AgentTrustProfile.apply_delta``
    handles clamping to [0.0, 1.0].

    Args:
        record: A fully populated :class:`ConsequenceRecord`.

    Returns:
        A float representing the change to apply to the agent's trust score.
    """
    delta: float = _TRUST_DELTA_PASS if record.tests_passed else _TRUST_DELTA_FAIL
    if record.repair_needed:
        delta += _TRUST_DELTA_REPAIR
    delta += record.human_feedback * _TRUST_DELTA_HUMAN_WEIGHT
    return delta
