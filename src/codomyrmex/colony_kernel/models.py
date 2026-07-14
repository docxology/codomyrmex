"""Colony Kernel shared contract — value objects and enums for all subsystems.

All Colony Kernel modules import from here. No cross-module imports between
subsystems; integration and explicit subsystem references are owned by the kernel.

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
    - FAILURE: trail avoidance (this path produced a caller-reported adverse
      outcome)
    - POLICY_REJECTION: audit trail for a proposal rejected by policy; this is
      deliberately not an observed execution failure
    - SUCCESS: trail amplification (this path worked)
    - RISK: caution marker (tread carefully near this location)
    - NEED: resource request (this location requires attention)
    - DEPENDENCY: usage trace (this module is actively imported / called)
    - HUMAN_PRIORITY: operator-injected signal (highest trust weight)
    """

    FAILURE = "failure"
    POLICY_REJECTION = "policy_rejection"
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

    def __str__(self) -> str:
        return (
            f"ColonySignal({self.signal_type.value}@{self.location!r} "
            f"strength={self.strength:.3f} source={self.source.value})"
        )

    def __repr__(self) -> str:
        return (
            f"ColonySignal(location={self.location!r}, "
            f"signal_type={self.signal_type!r}, strength={self.strength!r}, "
            f"decay_rate={self.decay_rate!r}, source={self.source!r})"
        )


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
    REFUSE: rejected by policy; deposits a POLICY_REJECTION audit signal.
    """

    EXECUTE = "execute"
    HOLD = "hold"
    REFUSE = "refuse"


class AuthorizationStatus(Enum):
    """Lifecycle state of an execution authorization."""

    ISSUED = "issued"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REVOKED = "revoked"
    REJECTED = "rejected"


@dataclass
class GateResult:
    """Full gate verdict including score, reasoning, and approval status."""

    decision: GateDecision
    gate_score: float  # 0.0–1.0 composite score
    reason: str
    required_evidence: list[str] = field(default_factory=list)  # for HOLD
    budget_approved: bool = True
    falsification_severity: float = 0.0  # 0.0 = clean, 1.0 = do not execute
    authorization: ExecutionAuthorization | None = None

    def __str__(self) -> str:
        return (
            f"GateResult({self.decision.value} score={self.gate_score:.3f} "
            f"budget_ok={self.budget_approved})"
        )

    def __repr__(self) -> str:
        return (
            f"GateResult(decision={self.decision!r}, gate_score={self.gate_score!r}, "
            f"reason={self.reason!r}, budget_approved={self.budget_approved!r}, "
            f"falsification_severity={self.falsification_severity!r})"
        )


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
    evidence_grade: str = "caller_reported_unattested"
    recorded_at: float = field(default_factory=time.time)
    consequence_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not -1.0 <= self.human_feedback <= 1.0:
            raise ValueError("ConsequenceRecord.human_feedback must be in [-1.0, 1.0]")
        if self.evidence_grade not in {
            "caller_reported_unattested",
            "attested_execution",
            "supervised_evaluator",
        }:
            raise ValueError(
                "ConsequenceRecord.evidence_grade must be one of "
                "'caller_reported_unattested', 'attested_execution', "
                "or 'supervised_evaluator'"
            )


@dataclass(frozen=True)
class ExecutionAuthorization:
    """Signed, scope-bound capability issued only for an EXECUTE decision."""

    authorization_id: str
    proposal_id: str
    agent_id: str
    action_type: str
    target: str
    scope_digest: str
    issued_at: float
    expires_at: float
    nonce: str
    issuer_key_id: str
    signature: str
    status: AuthorizationStatus = AuthorizationStatus.ISSUED


@dataclass(frozen=True)
class ExecutionReceipt:
    """Executor-signed evidence that a capability was consumed and run."""

    authorization_id: str
    proposal_id: str
    executor_id: str
    action_digest: str
    result_digest: str
    started_at: float
    completed_at: float
    exit_code: int
    status: str
    executor_key_id: str
    signature: str


@dataclass(frozen=True)
class OutcomeEvidence:
    """Evidence supplied when converting an execution receipt into an outcome."""

    authorization_id: str
    receipt: ExecutionReceipt
    evidence_grade: str = "attested_execution"

    def __post_init__(self) -> None:
        if self.evidence_grade != "attested_execution":
            raise ValueError(
                "OutcomeEvidence.evidence_grade must be 'attested_execution'"
            )


@dataclass(frozen=True)
class SupervisedEvaluatorEvidence:
    """Signed read-only evaluator input used for supervised bootstrap checks."""

    agent_id: str
    proposal_id: str
    evaluator_id: str
    evaluator_key_id: str
    assessment_digest: str
    signature: str
    read_only: bool = True

    def __post_init__(self) -> None:
        if not self.read_only:
            raise ValueError("supervised evaluator evidence must be read-only")


# ---------------------------------------------------------------------------
# Agent role
# ---------------------------------------------------------------------------


class AgentRole(Enum):
    """Emergent role assignment based on consequence history.

    Roles are inferred by RoleAdapter rather than hard-assigned at startup.
    The gate hard-refuses SANDBOX profiles. Other roles are descriptive labels;
    the current implementation does not enforce an action-by-role permission matrix.
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


# One numeric severity policy is shared by falsification, gate diagnostics,
# MCP recommendations, and manuscript provenance.  Keeping the ordering here
# prevents enum-label ordering (for example, alphabetical ``max``) from
# changing a safety decision.
_SEVERITY_RANK: dict[FalsificationSeverity, int] = {
    FalsificationSeverity.LOW: 1,
    FalsificationSeverity.MEDIUM: 2,
    FalsificationSeverity.HIGH: 3,
    FalsificationSeverity.CRITICAL: 4,
}

_SEVERITY_WEIGHT: dict[FalsificationSeverity, float] = {
    FalsificationSeverity.LOW: 0.05,
    FalsificationSeverity.MEDIUM: 0.20,
    FalsificationSeverity.HIGH: 0.45,
    FalsificationSeverity.CRITICAL: 1.0,
}


def severity_rank(severity: FalsificationSeverity) -> int:
    """Return the canonical numeric rank for a falsification severity."""
    return _SEVERITY_RANK[severity]


def maximum_severity(
    findings: list[FalsificationFinding],
) -> FalsificationSeverity | None:
    """Return the strongest finding by numeric rank, or ``None`` if empty."""
    if not findings:
        return None
    return max(findings, key=lambda finding: severity_rank(finding.severity)).severity


def severity_weight(severity: FalsificationSeverity) -> float:
    """Return the canonical advisory weight for *severity*."""
    return _SEVERITY_WEIGHT[severity]


def recommendation_for_severity(
    severity: FalsificationSeverity | None,
) -> str:
    """Map the strongest severity to the bounded advisory recommendation.

    CRITICAL findings refuse, HIGH findings hold, and lower-severity findings
    remain ordinary advisory scoring rather than being promoted by averaging.
    """
    if severity is FalsificationSeverity.CRITICAL:
        return "refuse"
    if severity is FalsificationSeverity.HIGH:
        return "hold"
    return "execute"


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

    def __str__(self) -> str:
        return (
            f"FalsificationFinding({self.severity.value}: {self.claim[:60]}...)"
            if len(self.claim) > 60
            else f"FalsificationFinding({self.severity.value}: {self.claim})"
        )

    def __repr__(self) -> str:
        return (
            f"FalsificationFinding(severity={self.severity!r}, "
            f"attack_vector={self.attack_vector!r}, claim={self.claim!r})"
        )


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


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "_SEVERITY_RANK",
    "_SEVERITY_WEIGHT",
    "ActionProposal",
    "AgentRole",
    "AgentTrustProfile",
    "AuthorizationStatus",
    "ColonySignal",
    "ConsequenceRecord",
    "DecayRate",
    "ExecutionAuthorization",
    "ExecutionReceipt",
    "FalsificationFinding",
    "FalsificationSeverity",
    "GateDecision",
    "GateResult",
    "OutcomeEvidence",
    "PruningCandidate",
    "ResourceCost",
    "SignalSource",
    "SignalType",
    "SupervisedEvaluatorEvidence",
    "compute_trust_delta",
    "make_trace_key",
    "maximum_severity",
    "recommendation_for_severity",
    "severity_rank",
    "severity_weight",
]
