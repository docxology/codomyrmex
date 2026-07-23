from __future__ import annotations

import threading

import pytest

from codomyrmex.colony_kernel.models import (
    ColonySignal,
    DecayRate,
    SignalSource,
    SignalType,
)
from codomyrmex.colony_kernel.research import (
    GenerativeModelSpec,
    KernelObservation,
    KernelProbabilisticAdapter,
    PersistentPheromoneStore,
    brier_score,
    expected_calibration_error,
    generate_synthetic_cases,
    log_loss,
    paired_bootstrap_delta,
    reliability_bins,
    run_paired_benchmark,
    selective_risk,
    split_leakage_report,
)


def test_offline_benchmark_is_paired_and_reproducible():
    first = run_paired_benchmark(repo_root=".", seed=7)
    second = run_paired_benchmark(repo_root=".", seed=7)

    assert first.metrics == second.metrics
    assert first.artifact_hash == second.artifact_hash
    assert len(first.traces) == 2 * len(generate_synthetic_cases())
    assert first.metrics["trace_completeness"] == 1.0


def test_calibration_metrics_are_deterministic_and_valid():
    labels = [True, False, True, False]
    probabilities = [0.9, 0.2, 0.7, 0.4]

    assert log_loss(labels, probabilities) > 0.0
    assert 0.0 <= brier_score(labels, probabilities) <= 1.0
    assert 0.0 <= expected_calibration_error(labels, probabilities, bins=2) <= 1.0
    assert reliability_bins(labels, probabilities, bins=2)
    assert selective_risk(labels, probabilities, 0.5)["coverage"] == 0.5
    result = paired_bootstrap_delta([0.0, 1.0], [1.0, 0.0], seed=3, samples=100)
    assert result["estimate"] == 0.0


def test_probability_metrics_reject_out_of_range_values():
    with pytest.raises(ValueError, match="probabilities"):
        brier_score([True], [1.1])


def test_task_case_schema_rejects_unlisted_or_empty_actions():
    from codomyrmex.colony_kernel.research.schemas import TaskCase

    with pytest.raises(ValueError, match="allowed_actions"):
        TaskCase("bad-action", "threat", "target", "delete", ("read",), (), True)
    with pytest.raises(ValueError, match="non-empty"):
        TaskCase("empty-actions", "threat", "target", "read", (), (), True)


def test_split_leakage_report_is_conservative():
    cases = list(generate_synthetic_cases())
    assert split_leakage_report(cases[:2], [cases[2]])["status"] == "clean"
    overlap = split_leakage_report(cases[:1], [cases[0]])
    assert overlap["status"] == "overlap"
    assert overlap["task_id_overlap"] == [cases[0].task_id]


def test_persistent_signal_store_survives_restart_and_serializes_writes(tmp_path):
    db = tmp_path / "signals.sqlite"
    store = PersistentPheromoneStore(db)
    signal = ColonySignal(
        location="target.py",
        signal_type=SignalType.FAILURE,
        strength=2.0,
        decay_rate=DecayRate.FAST,
        source=SignalSource.TEST,
    )

    def deposit() -> None:
        store.deposit_signal(signal)

    threads = [threading.Thread(target=deposit) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert store.sense("target.py", SignalType.FAILURE) == pytest.approx(8.0)
    store.close()

    restarted = PersistentPheromoneStore(db)
    assert restarted.sense("target.py", SignalType.FAILURE) == pytest.approx(8.0)
    restarted.evaporate()
    assert restarted.sense("target.py", SignalType.FAILURE) == pytest.approx(7.7)
    restarted.close()


def test_probabilistic_adapter_declares_model_and_keeps_boundary_explicit():
    spec = GenerativeModelSpec(
        states=("safe", "unsafe"),
        observations=("execute", "refuse"),
        actions=("inspect", "change"),
        priors={"safe": 0.5, "unsafe": 0.5},
        likelihood={
            "safe": {"execute": 0.9, "refuse": 0.1},
            "unsafe": {"execute": 0.2, "refuse": 0.8},
        },
        transitions={
            "inspect": {"safe": {"safe": 1.0}, "unsafe": {"unsafe": 1.0}},
            "change": {"safe": {"safe": 1.0}, "unsafe": {"unsafe": 1.0}},
        },
        preferences={"safe": 1.0, "unsafe": -1.0},
    )
    adapter = KernelProbabilisticAdapter(spec)

    posterior = adapter.posterior("refuse")
    observation = adapter.observation_from_kernel(
        KernelObservation("target.py", 3.0, "hold")
    )

    assert posterior["unsafe"] > posterior["safe"]
    assert observation["claim_boundary"].startswith("adapter observation")


def test_persistent_store_exposes_transaction_boundaries_for_crash_injection(tmp_path):
    boundaries: list[str] = []

    def fail_before_insert(boundary: str) -> None:
        boundaries.append(boundary)
        if boundary == "before_insert":
            raise RuntimeError("injected crash")

    db = tmp_path / "crash.sqlite"
    store = PersistentPheromoneStore(db, failure_injector=fail_before_insert)
    signal = ColonySignal(
        location="isolated.py",
        signal_type=SignalType.RISK,
        strength=1.0,
        decay_rate=DecayRate.NORMAL,
        source=SignalSource.TEST,
    )
    with pytest.raises(RuntimeError, match="injected crash"):
        store.deposit_signal(signal)
    assert store.sense("isolated.py", SignalType.RISK) == 0.0
    store.close()

    restarted = PersistentPheromoneStore(db)
    assert restarted.sense("isolated.py", SignalType.RISK) == 0.0
    restarted.close()
    assert boundaries == ["before_begin", "before_delete", "before_insert"]


def test_persistent_store_serializes_independent_adapter_snapshots(tmp_path):
    db = tmp_path / "multi-writer.sqlite"
    first = PersistentPheromoneStore(db)
    second = PersistentPheromoneStore(db)
    first.deposit_signal(
        ColonySignal(
            location="first.py",
            signal_type=SignalType.FAILURE,
            strength=1.0,
            decay_rate=DecayRate.NORMAL,
            source=SignalSource.TEST,
        )
    )
    second.deposit_signal(
        ColonySignal(
            location="second.py",
            signal_type=SignalType.FAILURE,
            strength=1.0,
            decay_rate=DecayRate.NORMAL,
            source=SignalSource.TEST,
        )
    )
    first.refresh()
    assert first.sense("first.py", SignalType.FAILURE) == pytest.approx(1.0)
    assert first.sense("second.py", SignalType.FAILURE) == pytest.approx(1.0)
    first.close()
    second.close()
