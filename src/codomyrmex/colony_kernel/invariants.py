"""Colony Kernel formal invariant checks.

All functions in this module are deterministic, zero-dependency checks that
verify system-wide invariants. They accept optional inputs; when called with
no arguments they check the invariants against the statically known defaults
embedded in the source code.

These invariants serve three purposes:
1. **Documentation** — they encode what *must* be true for the kernel to be
   correct (and fail fast if someone accidentally changes a constant).
2. **Testing** — they can be imported and called directly in test suites as
   property-based assertions.
3. **Runtime health checks** — they can be called from monitoring pipelines
   to detect configuration drift.

All invariant functions return ``True`` when the invariant holds and
``False`` when it is violated or state observation fails. Ordinary exceptions
(including an unavailable input sequence) fail closed; ``BaseException``
interruptions such as KeyboardInterrupt and SystemExit still propagate.

The canonical thresholds and strength limits are imported from the runtime modules
that enforce them. This prevents a second, stale set of constants from masquerading
as a formal model.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import fields
from typing import TYPE_CHECKING

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.actuation_gate import GATE_SCORE_WEIGHTS
from codomyrmex.colony_kernel.models import (
    _TRUST_DELTA_FAIL,
    _TRUST_DELTA_HUMAN_WEIGHT,
    _TRUST_DELTA_PASS,
    _TRUST_DELTA_REPAIR,
    GateDecision,
    ResourceCost,
)
from codomyrmex.colony_kernel.role_adapter import (
    _ROLE_DISPATCHER_MIN_TRUST,
    _ROLE_GUARD_MIN_TRUST,
    _ROLE_MEMORY_MIN_TRUST,
    _ROLE_REPAIR_MIN_TRUST,
)

if TYPE_CHECKING:
    from codomyrmex.colony_kernel.models import (
        AgentTrustProfile,
        ConsequenceRecord,
        GateResult,
    )

# ---------------------------------------------------------------------------
# Gate-weight invariant
# ---------------------------------------------------------------------------

# Canonical gate score weights from actuation_gate.py (must sum to 1.0).
_GATE_WEIGHTS: tuple[float, ...] = tuple(
    GATE_SCORE_WEIGHTS[name] for name in ("budget", "risk", "trust", "completeness")
)

# Tolerance for floating-point summation errors
_WEIGHT_TOLERANCE: float = 1e-9


def check_gate_weights_sum_to_one(
    weights: Sequence[float] | None = None,
) -> bool:
    """Return True iff the gate score component weights sum to 1.0.

    Args:
        weights: Optional sequence of float weights to validate.  When
            ``None`` the canonical weights from ``actuation_gate.py`` are
            used (budget_ok=0.30, risk_ok=0.30, trust_ok=0.25, completeness=0.15).

    Returns:
        ``True`` if ``abs(sum(weights) - 1.0) < 1e-9``; ``False`` otherwise.

    Example::

        assert check_gate_weights_sum_to_one()  # canonical
        assert check_gate_weights_sum_to_one([0.25, 0.25, 0.25, 0.25])  # custom
        assert not check_gate_weights_sum_to_one([0.30, 0.30, 0.30])  # sum != 1
    """
    if weights is None:
        weights = _GATE_WEIGHTS
    try:
        values = [float(w) for w in weights]
        total = sum(values)
    except Exception:
        return False
    return all(0.0 <= value <= 1.0 for value in values) and (
        abs(total - 1.0) < _WEIGHT_TOLERANCE
    )


# ---------------------------------------------------------------------------
# Trust-score range invariant
# ---------------------------------------------------------------------------


def check_trust_score_in_range(
    profiles: Sequence[AgentTrustProfile] | None = None,
) -> bool:
    """Return True iff every trust score is in [0.0, 1.0].

    Args:
        profiles: Optional sequence of :class:`~codomyrmex.colony_kernel.models.AgentTrustProfile`
            instances to check.  When ``None`` the invariant is trivially True
            (no profiles to violate it).

    Returns:
        ``True`` if all profiles satisfy ``0.0 <= trust_score <= 1.0``.
        ``False`` if any profile's trust score is outside the closed interval.

    Example::

        from codomyrmex.colony_kernel.models import AgentTrustProfile, AgentRole

        p = AgentTrustProfile(agent_id="a", trust_score=0.5)
        assert check_trust_score_in_range([p])

        # A profile with a bad trust score (bypassing __post_init__ wouldn't
        # normally happen, but this test simulates a corrupted state):
        p.trust_score = 1.5  # manually corrupt
        assert not check_trust_score_in_range([p])
    """
    if profiles is None:
        return True
    try:
        for profile in profiles:
            score = float(profile.trust_score)
            if not (0.0 <= score <= 1.0):
                return False
    except Exception:
        return False
    return True


# ---------------------------------------------------------------------------
# Pheromone strength bounds invariant
# ---------------------------------------------------------------------------

# These bounds are enforced by TraceField and PheromoneStore.
_PHEROMONE_MIN_STRENGTH: float = 0.0
_PHEROMONE_MAX_STRENGTH: float = StigmergyConfig().max_strength


def check_pheromone_strength_bounds(
    strengths: Sequence[float] | None = None,
) -> bool:
    """Return True iff every pheromone strength is within the field bounds.

    Args:
        strengths: Optional sequence of float strength values to validate.
            When ``None`` the invariant is trivially True.

    Returns:
        ``True`` if all values satisfy the live ``TraceField`` bounds.

    Example::

        assert check_pheromone_strength_bounds([0.0, 1.5, 9.9])
        assert not check_pheromone_strength_bounds([-0.1])  # below floor
        assert not check_pheromone_strength_bounds([10.1])  # above default ceiling
    """
    if strengths is None:
        return True
    try:
        for s in strengths:
            val = float(s)
            if not (_PHEROMONE_MIN_STRENGTH <= val <= _PHEROMONE_MAX_STRENGTH):
                return False
    except Exception:
        return False
    return True


# ---------------------------------------------------------------------------
# Role-ladder monotonicity invariant
# ---------------------------------------------------------------------------

# Trust thresholds must be monotonically increasing along the promotion ladder.
# They are imported from role_adapter.py so the predicate follows live policy.
_ROLE_LADDER_THRESHOLDS: tuple[float, ...] = (
    _ROLE_REPAIR_MIN_TRUST,
    _ROLE_MEMORY_MIN_TRUST,
    _ROLE_DISPATCHER_MIN_TRUST,
    _ROLE_GUARD_MIN_TRUST,
)


def check_role_ladder_monotonic(
    thresholds: Sequence[float] | None = None,
) -> bool:
    """Return True iff the role-ladder trust thresholds are strictly monotonic.

    Each threshold must be strictly greater than the previous one so that
    promotion is always unambiguous (no two roles share the same threshold).

    Args:
        thresholds: Optional sequence of trust threshold floats in ladder order
            (lowest role first). When ``None`` the canonical thresholds from
            ``role_adapter.py`` are used.

    Returns:
        ``True`` if the sequence is strictly increasing.
        ``False`` if any threshold is <= the previous one (including ties).

    Example::

        assert check_role_ladder_monotonic()  # canonical thresholds
        assert check_role_ladder_monotonic([0.1, 0.3, 0.6, 0.9])
        assert not check_role_ladder_monotonic([0.3, 0.3, 0.5])  # tie
        assert not check_role_ladder_monotonic([0.5, 0.3, 0.8])  # decrease
    """
    if thresholds is None:
        thresholds = _ROLE_LADDER_THRESHOLDS
    try:
        items = list(thresholds)
        floats = [float(t) for t in items]
    except Exception:
        return False
    return all(0.0 <= value <= 1.0 for value in floats) and all(
        floats[i] > floats[i - 1] for i in range(1, len(floats))
    )


# ---------------------------------------------------------------------------
# DecayRate enum values don't conflict with SignalType values
# ---------------------------------------------------------------------------


def check_enum_values_no_conflict() -> bool:
    """Return True iff DecayRate and SignalType enum values are disjoint sets.

    Both enums are used as string tokens in pheromone trace keys and metadata.
    If they shared a value string, a ``SignalType.X.value`` lookup could be
    misinterpreted as a ``DecayRate.X.value`` in logging or serialization.

    Returns:
        ``True`` if the two value sets are disjoint; ``False`` otherwise.

    Example::

        assert check_enum_values_no_conflict()
    """
    from codomyrmex.colony_kernel.models import DecayRate, SignalType

    try:
        decay_values: set[object] = {dr.value for dr in DecayRate}
        signal_values: set[object] = {st.value for st in SignalType}
    except Exception:
        return False
    return decay_values.isdisjoint(signal_values)


# ---------------------------------------------------------------------------
# Gate-decision threshold invariant
# ---------------------------------------------------------------------------

from codomyrmex.colony_kernel.actuation_gate import (
    _GATE_SCORE_EXECUTE,
    _GATE_SCORE_HOLD,
)


def check_gate_thresholds_ordered(
    execute_thresh: float | None = None,
    hold_thresh: float | None = None,
) -> bool:
    """Return True iff 0.0 <= hold_threshold < execute_threshold <= 1.0.

    Ensures the gate decision space is strictly partitioned into [0, hold),
    [hold, execute), and [execute, 1] without overlapping or inverted regions.
    """
    try:
        ex = _GATE_SCORE_EXECUTE if execute_thresh is None else float(execute_thresh)
        hd = _GATE_SCORE_HOLD if hold_thresh is None else float(hold_thresh)
    except Exception:
        return False
    return 0.0 <= hd < ex <= 1.0


def check_budget_monotonic(
    usage: Sequence[ResourceCost] | None = None,
) -> bool:
    """Validate finite, nonnegative cumulative usage within one budget period.

    Each dimension must never decrease between successive snapshots. Period
    resets must start a new sequence; saturating risk dimensions may stay equal.
    This checks accounting consistency, not whether an actual cost was observed.
    """
    if usage is None:
        return True
    previous: dict[str, float] = {}
    previous_calls = 0
    fractions = {"risk_level", "merge_risk", "security_exposure"}
    try:
        for snapshot in usage:
            if not isinstance(snapshot, ResourceCost):
                return False
            calls = snapshot.llm_calls
            if isinstance(calls, bool) or not isinstance(calls, int):
                return False
            if calls < previous_calls:
                return False
            previous_calls = calls
            for dimension in fields(ResourceCost):
                if dimension.name == "llm_calls":
                    continue
                raw = getattr(snapshot, dimension.name)
                value = float(raw)
                if not math.isfinite(value) or value < 0:
                    return False
                if dimension.name in fractions and value > 1:
                    return False
                if value < previous.get(dimension.name, 0.0):
                    return False
                previous[dimension.name] = value
    except Exception:
        return False
    return True


def check_gate_decision_space_closed(
    results: Sequence[GateResult] | None = None,
) -> bool:
    """Check ternary verdict identity and bounded scores on observed results."""
    if results is None:
        return True
    try:
        for result in results:
            if not isinstance(result.decision, GateDecision):
                return False
            if not isinstance(result.budget_approved, bool):
                return False
            if not 0.0 <= float(result.gate_score) <= 1.0:
                return False
            if not 0.0 <= float(result.falsification_severity) <= 1.0:
                return False
            if result.decision == GateDecision.EXECUTE and (
                not result.budget_approved or result.falsification_severity >= 1.0
            ):
                return False
    except Exception:
        return False
    return True


def check_consequence_trust_bounds(
    records: Sequence[ConsequenceRecord] | None = None,
) -> bool:
    """Check feedback and trust deltas against canonical runtime policy bounds.

    These are bounds on records after trust-delta computation. Unprocessed
    records may carry the documented zero sentinel. Actual profile trust is
    checked separately; this does not authenticate caller-reported outcomes.
    """
    if records is None:
        return True
    minimum = (
        min(_TRUST_DELTA_FAIL, _TRUST_DELTA_PASS)
        + min(0.0, _TRUST_DELTA_REPAIR)
        - abs(_TRUST_DELTA_HUMAN_WEIGHT)
    )
    maximum = (
        max(_TRUST_DELTA_FAIL, _TRUST_DELTA_PASS)
        + max(0.0, _TRUST_DELTA_REPAIR)
        + abs(_TRUST_DELTA_HUMAN_WEIGHT)
    )
    try:
        for record in records:
            feedback = float(record.human_feedback)
            delta = float(record.trust_delta)
            if not -1.0 <= feedback <= 1.0:
                return False
            if not minimum <= delta <= maximum:
                return False
    except Exception:
        return False
    return True


# ---------------------------------------------------------------------------
# Composite health check
# ---------------------------------------------------------------------------


def all_invariants_hold(
    profiles: Sequence[AgentTrustProfile] | None = None,
    strengths: Sequence[float] | None = None,
    *,
    budget_usage: Sequence[ResourceCost] | None = None,
    gate_results: Sequence[GateResult] | None = None,
    consequences: Sequence[ConsequenceRecord] | None = None,
) -> dict[str, bool]:
    """Run all invariant checks and return a summary dict.

    Args:
        profiles: Optional agent profiles for the trust-score check.
        strengths: Optional pheromone strengths for the bounds check.
        budget_usage: Cumulative usage snapshots within one budget period.
        gate_results: Observed gate results to check for closed decision space.
        consequences: Consequence records with bounded feedback/trust deltas.

    Returns:
        Dict mapping invariant name → bool.  All values True = healthy.

    Example::

        result = all_invariants_hold()
        assert all(result.values()), f"Invariant failures: {result}"
    """
    return {
        "gate_weights_sum_to_one": check_gate_weights_sum_to_one(),
        "gate_thresholds_ordered": check_gate_thresholds_ordered(),
        "trust_score_in_range": check_trust_score_in_range(profiles),
        "pheromone_strength_bounds": check_pheromone_strength_bounds(strengths),
        "role_ladder_monotonic": check_role_ladder_monotonic(),
        "enum_values_no_conflict": check_enum_values_no_conflict(),
        "budget_monotonic": check_budget_monotonic(budget_usage),
        "gate_decision_space_closed": check_gate_decision_space_closed(gate_results),
        "consequence_trust_bounds": check_consequence_trust_bounds(consequences),
    }


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "all_invariants_hold",
    "check_budget_monotonic",
    "check_consequence_trust_bounds",
    "check_enum_values_no_conflict",
    "check_gate_decision_space_closed",
    "check_gate_thresholds_ordered",
    "check_gate_weights_sum_to_one",
    "check_pheromone_strength_bounds",
    "check_role_ladder_monotonic",
    "check_trust_score_in_range",
]
