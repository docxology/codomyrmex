"""Regression tests for the standalone workflow runner."""

from __future__ import annotations

import importlib.util
import shlex
import sys
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT

SCRIPT_PATH = REPO_ROOT / "scripts" / "workflow_execution" / "workflow_runner.py"


def _load_workflow_runner():
    spec = importlib.util.spec_from_file_location("workflow_runner", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_timeout_stops_following_steps(tmp_path: Path) -> None:
    runner = _load_workflow_runner()
    marker = tmp_path / "should_not_run.txt"
    code = f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')"
    write_marker = f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"

    results = runner.run_workflow(
        {
            "steps": [
                {
                    "name": "slow step",
                    "command": f"{shlex.quote(sys.executable)} -c {shlex.quote('import time; time.sleep(0.2)')}",
                    "timeout": 0.01,
                },
                {"name": "must not run", "command": write_marker},
            ]
        }
    )

    assert [result["status"] for result in results] == ["timeout"]
    assert not marker.exists()


@pytest.mark.unit
def test_timeout_can_continue_when_explicitly_configured() -> None:
    runner = _load_workflow_runner()

    results = runner.run_workflow(
        {
            "steps": [
                {
                    "name": "slow step",
                    "command": f"{shlex.quote(sys.executable)} -c {shlex.quote('import time; time.sleep(0.2)')}",
                    "timeout": 0.01,
                    "continue_on_error": True,
                },
                {"name": "after timeout", "command": "printf continued"},
            ]
        }
    )

    assert [result["status"] for result in results] == ["timeout", "success"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("step", "expected_status"),
    [
        (
            {"name": "missing command", "command": "definitely-not-a-command"},
            "failed",
        ),
        ({"name": "future script", "script": "future.py"}, "script_not_implemented"),
        ({"name": "empty step"}, "unimplemented"),
    ],
)
def test_non_success_states_stop_following_steps(
    tmp_path: Path, step: dict, expected_status: str
) -> None:
    runner = _load_workflow_runner()
    marker = tmp_path / "should_not_run.txt"
    code = f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')"
    step_after = {
        "name": "must not run",
        "command": f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}",
    }

    results = runner.run_workflow({"steps": [step, step_after]})

    assert [result["status"] for result in results] == [expected_status]
    assert not marker.exists()
