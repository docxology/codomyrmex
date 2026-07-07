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
``False`` when it is violated, never raising.

Zero dependencies beyond the colony_kernel package itself.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codomyrmex.colony_kernel.models import AgentTrustProfile, DecayRate

# ---------------------------------------------------------------------------
# Gate-weight invariant
# ---------------------------------------------------------------------------

# Canonical gate score weights from actuation_gate.py (must sum to 1.0)
_GATE_WEIGHTS: tuple[float, float, float, float] = (
    0.30,  # budget_ok
    0.30,  # risk_ok
    0.25,  # trust_ok
    0.15,  # completeness
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
        total = sum(float(w) for w in weights)
    except (TypeError, ValueError):
        return False
    return abs(total - 1.0) < _WEIGHT_TOLERANCE


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
    for profile in profiles:
        try:
            score = float(profile.trust_score)
        except (TypeError, AttributeError, ValueError):
            return False
        if not (0.0 <= score <= 1.0):
            return False
    return True


# ---------------------------------------------------------------------------
# Pheromone strength bounds invariant
# ---------------------------------------------------------------------------

# These mirror the bounds from models.py (ColonySignal.__post_init__) and
# pheromone_store.py (_MAX_DEPOSIT_STRENGTH).
_PHEROMONE_MIN_STRENGTH: float = 0.0
_PHEROMONE_MAX_STRENGTH: float = 1_000_000.0  # matches _MAX_DEPOSIT_STRENGTH


def check_pheromone_strength_bounds(
    strengths: Sequence[float] | None = None,
) -> bool:
    """Return True iff every pheromone strength is in [0.0, 1e6].

    Args:
        strengths: Optional sequence of float strength values to validate.
            When ``None`` the invariant is trivially True.

    Returns:
        ``True`` if all values satisfy
        ``_PHEROMONE_MIN_STRENGTH <= s <= _PHEROMONE_MAX_STRENGTH``.

    Example::

        assert check_pheromone_strength_bounds([0.0, 1.5, 999.9])
        assert not check_pheromone_strength_bounds([-0.1])  # below floor
        assert not check_pheromone_strength_bounds([1_000_001.0])  # above ceiling
    """
    if strengths is None:
        return True
    for s in strengths:
        try:
            val = float(s)
        except (TypeError, ValueError):
            return False
        if not (_PHEROMONE_MIN_STRENGTH <= val <= _PHEROMONE_MAX_STRENGTH):
            return False
    return True


# ---------------------------------------------------------------------------
# Role-ladder monotonicity invariant
# ---------------------------------------------------------------------------

# Trust thresholds must be monotonically increasing along the promotion ladder.
# Matches role_adapter.py constants exactly.
_ROLE_LADDER_THRESHOLDS: tuple[float, ...] = (
    0.20,  # REPAIR_ANT
    0.35,  # MEMORY_ANT
    0.50,  # DISPATCHER
    0.70,  # GUARD_ANT
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
    items = list(thresholds)
    if not items:
        return True
    try:
        floats = [float(t) for t in items]
    except (TypeError, ValueError):
        return False
    return all(floats[i] > floats[i - 1] for i in range(1, len(floats)))


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
# Composite health check
# ---------------------------------------------------------------------------


def all_invariants_hold(
    profiles: Sequence[AgentTrustProfile] | None = None,
    strengths: Sequence[float] | None = None,
) -> dict[str, bool]:
    """Run all invariant checks and return a summary dict.

    Args:
        profiles: Optional agent profiles for the trust-score check.
        strengths: Optional pheromone strengths for the bounds check.

    Returns:
        Dict mapping invariant name → bool.  All values True = healthy.

    Example::

        result = all_invariants_hold()
        assert all(result.values()), f"Invariant failures: {result}"
    """
    return {
        "gate_weights_sum_to_one": check_gate_weights_sum_to_one(),
        "trust_score_in_range": check_trust_score_in_range(profiles),
        "pheromone_strength_bounds": check_pheromone_strength_bounds(strengths),
        "role_ladder_monotonic": check_role_ladder_monotonic(),
        "enum_values_no_conflict": check_enum_values_no_conflict(),
    }


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "all_invariants_hold",
    "check_enum_values_no_conflict",
    "check_gate_weights_sum_to_one",
    "check_pheromone_strength_bounds",
    "check_role_ladder_monotonic",
    "check_trust_score_in_range",
]
