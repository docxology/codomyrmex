"""Regression tests for the deterministic Colony Kernel replay artifact."""

from __future__ import annotations

import json

import pytest

from codomyrmex.colony_kernel.replay import run_paired_locality_replay


def test_replay_is_repeatable_and_preserves_locality() -> None:
    record = run_paired_locality_replay(
        agent_trust=0.50,
        recovery_ticks=20,
        seed=0,
    )

    assert all(record["assertions"].values())
    assert record["runs"]["first"] == record["runs"]["repeat"]
    assert record["semantic_digest"]
    assert record["record_sha256"]


def test_replay_serialization_is_stable() -> None:
    first = run_paired_locality_replay(agent_trust=0.50, recovery_ticks=20, seed=7)
    second = run_paired_locality_replay(agent_trust=0.50, recovery_ticks=20, seed=7)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


@pytest.mark.parametrize(
    ("agent_trust", "recovery_ticks"),
    [(-0.01, 20), (1.01, 20), (0.50, -1)],
)
def test_replay_rejects_invalid_protocol_inputs(
    agent_trust: float, recovery_ticks: int
) -> None:
    with pytest.raises(ValueError):
        run_paired_locality_replay(
            agent_trust=agent_trust,
            recovery_ticks=recovery_ticks,
        )
