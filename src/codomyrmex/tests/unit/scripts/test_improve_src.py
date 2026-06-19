"""Tests for source improvement swarm dry-run manifests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PATH = REPO_ROOT / "scripts" / "agents" / "improve_src.py"


def _load_improve_src_module():
    spec = importlib.util.spec_from_file_location("improve_src", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_build_dry_run_manifest_is_machine_readable() -> None:
    improve_src = _load_improve_src_module()
    tasks = [{"module": "agents", "prompt": "Improve agents safely."}]

    manifest = improve_src.build_dry_run_manifest(tasks, batch_size=2, delay=0.5)

    assert manifest["mode"] == "dry_run"
    assert manifest["classification"] == "dry_run"
    assert manifest["side_effects"] == []
    assert manifest["task_count"] == 1
    assert manifest["tasks"] == tasks


@pytest.mark.unit
def test_build_improvement_tasks_honors_limit() -> None:
    improve_src = _load_improve_src_module()

    tasks = improve_src.build_improvement_tasks(limit=2)

    assert 0 < len(tasks) <= 2
    assert {"module", "prompt"} <= set(tasks[0])
