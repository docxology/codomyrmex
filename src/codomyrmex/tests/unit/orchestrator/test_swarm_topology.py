"""Unit tests for SwarmTopology: Fan-Out, Fan-In, Pipeline, Broadcast.

Zero-mock: uses pure Python callables (no subprocess, no network).
"""

from __future__ import annotations

import pytest

from codomyrmex.orchestrator.swarm_topology import (
    SwarmTopology,
    TaskResult,
    TaskSpec,
    TopologyMode,
)


# ── helpers ─────────────────────────────────────────────────────────────────


def double(x: int) -> int:
    return x * 2


def fail_always() -> None:
    msg = "intentional failure"
    raise RuntimeError(msg)


def pipeline_add_ten(n: int) -> int:
    return n + 10


def broadcast_echo(*, broadcast_message: dict, **_kw: object) -> dict:
    return {"received": broadcast_message}


# ── TaskSpec / TaskResult basics ─────────────────────────────────────────────


def test_task_result_success_flag() -> None:
    ok = TaskResult(task_id="t1", output=42)
    assert ok.success
    err = TaskResult(task_id="t2", output=None, error="boom")
    assert not err.success


# ── fan_out ─────────────────────────────────────────────────────────────────


def test_fan_out_executes_all_tasks() -> None:
    topo = SwarmTopology()
    tasks = [TaskSpec(task_id=f"t{i}", fn=double, args=[i]) for i in range(4)]
    results = topo.fan_out(tasks)
    assert len(results) == 4


def test_fan_out_results_in_submission_order() -> None:
    topo = SwarmTopology()
    tasks = [TaskSpec(task_id=f"t{i}", fn=double, args=[i]) for i in range(5)]
    results = topo.fan_out(tasks)
    for i, r in enumerate(results):
        assert r.task_id == f"t{i}"
        assert r.output == i * 2


def test_fan_out_captures_exceptions() -> None:
    topo = SwarmTopology()
    tasks = [
        TaskSpec(task_id="ok", fn=double, args=[3]),
        TaskSpec(task_id="fail", fn=fail_always),
    ]
    results = topo.fan_out(tasks)
    ok_r = next(r for r in results if r.task_id == "ok")
    err_r = next(r for r in results if r.task_id == "fail")
    assert ok_r.success
    assert not err_r.success
    assert "intentional" in err_r.error


# ── fan_in ───────────────────────────────────────────────────────────────────


def test_fan_in_aggregates_counts() -> None:
    topo = SwarmTopology()
    raw = [
        TaskResult(task_id="a", output={"x": 1}),
        TaskResult(task_id="b", output={"y": 2}),
        TaskResult(task_id="c", output=None, error="bad"),
    ]
    result = topo.fan_in(raw)
    assert result["success_count"] == 2
    assert result["error_count"] == 1


def test_fan_in_merges_dict_outputs() -> None:
    topo = SwarmTopology()
    raw = [
        TaskResult(task_id="a", output={"alpha": 1}),
        TaskResult(task_id="b", output={"beta": 2}),
    ]
    result = topo.fan_in(raw)
    assert result["merged_outputs"] == {"alpha": 1, "beta": 2}


# ── pipeline ──────────────────────────────────────────────────────────────────


def test_pipeline_chains_output() -> None:
    topo = SwarmTopology()
    tasks = [
        TaskSpec(task_id="start", fn=pipeline_add_ten, args=[5]),
        TaskSpec(task_id="second", fn=pipeline_add_ten, args=[]),
        TaskSpec(task_id="third", fn=pipeline_add_ten, args=[]),
    ]
    results = topo.pipeline(tasks)
    # 5 + 10 = 15, 15 + 10 = 25, 25 + 10 = 35
    assert results[0].output == 15
    assert results[1].output == 25
    assert results[2].output == 35


# ── broadcast ────────────────────────────────────────────────────────────────


def test_broadcast_injects_message() -> None:
    topo = SwarmTopology()
    msg = {"cmd": "stop"}
    tasks = [TaskSpec(task_id=f"agent_{i}", fn=broadcast_echo) for i in range(3)]
    results = topo.broadcast(msg, tasks)
    for r in results:
        assert r.success
        assert r.output["received"]["cmd"] == "stop"


# ── run() dispatcher ─────────────────────────────────────────────────────────


@pytest.mark.parametrize("mode", [m.value for m in TopologyMode])
def test_run_accepts_all_topology_modes(mode: str) -> None:
    topo = SwarmTopology()
    tasks = [TaskSpec(task_id="t", fn=double, args=[1])]
    result = topo.run(
        mode,
        tasks,
        broadcast_message={"hello": "world"},
    )
    assert "results" in result or "success_count" in result


def test_run_invalid_mode_raises_value_error() -> None:
    topo = SwarmTopology()
    with pytest.raises(ValueError, match="'bad_mode'"):
        topo.run("bad_mode", [])
