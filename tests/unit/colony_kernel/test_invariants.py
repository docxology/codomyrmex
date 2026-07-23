"""Regression tests for the executable Colony Kernel invariant predicates."""

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.actuation_gate import GATE_SCORE_WEIGHTS
from codomyrmex.colony_kernel.invariants import (
    all_invariants_hold,
    check_enum_values_no_conflict,
    check_gate_weights_sum_to_one,
    check_pheromone_strength_bounds,
    check_role_ladder_monotonic,
    check_trust_score_in_range,
)
from codomyrmex.colony_kernel.models import AgentTrustProfile


def test_invariant_predicates_read_live_runtime_constants() -> None:
    """The formal checks must follow the policies that execute at runtime."""
    assert check_gate_weights_sum_to_one(list(GATE_SCORE_WEIGHTS.values()))
    assert check_pheromone_strength_bounds([0.0, StigmergyConfig().max_strength])
    assert check_role_ladder_monotonic()


def test_invariant_predicates_reject_boundary_violations() -> None:
    profile = AgentTrustProfile(agent_id="agent", trust_score=0.5)
    profile.trust_score = 1.01

    assert not check_trust_score_in_range([profile])
    assert not check_pheromone_strength_bounds([-0.001])
    assert not check_pheromone_strength_bounds([StigmergyConfig().max_strength + 1])
    assert not check_role_ladder_monotonic([0.2, 0.2])
    assert not check_gate_weights_sum_to_one([0.25, 0.25, 0.25])


def test_composite_invariant_report_is_true_for_live_defaults() -> None:
    report = all_invariants_hold(
        profiles=[AgentTrustProfile(agent_id="agent", trust_score=0.5)],
        strengths=[0.0, 1.0],
    )

    assert report == {
        "gate_weights_sum_to_one": True,
        "trust_score_in_range": True,
        "pheromone_strength_bounds": True,
        "role_ladder_monotonic": True,
        "enum_values_no_conflict": True,
    }
    assert check_enum_values_no_conflict()
