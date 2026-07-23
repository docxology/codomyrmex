from __future__ import annotations

from codomyrmex.colony_kernel.formal import (
    FormalStatus,
    KernelFormalSnapshot,
    prove_kernel_obligations,
    runtime_obligations,
)


def _snapshot(**overrides):
    values = {
        "weights": {"budget": 0.3, "risk": 0.3, "trust": 0.25, "completeness": 0.15},
        "trust_score": 0.8,
        "pheromone_strength": 2.0,
        "pheromone_max_strength": 10.0,
        "score_low_pressure": 0.85,
        "score_high_pressure": 0.85,
        "risk_component_low": 1.0,
        "risk_component_high": 0.5,
        "score_unrelated_before": 0.85,
        "score_unrelated_after": 0.85,
        "has_execute_verdict": True,
        "has_authorization": True,
        "has_execution_receipt": True,
        "has_outcome_link": True,
        "role_thresholds": (0.2, 0.4, 0.6, 0.8),
    }
    values.update(overrides)
    return KernelFormalSnapshot(**values)


def test_runtime_obligations_are_true_for_reference_snapshot():
    report = runtime_obligations(_snapshot())

    assert all(report.values())


def test_runtime_obligations_expose_unauthorized_outcome():
    report = runtime_obligations(_snapshot(has_execution_receipt=False))

    assert report["authorized_outcome_linkage"] is False


def test_optional_solver_reports_unavailable_without_z3():
    results = prove_kernel_obligations(_snapshot())

    assert results
    assert all(
        result.status in {FormalStatus.UNAVAILABLE, FormalStatus.PROVED}
        for result in results
    )
