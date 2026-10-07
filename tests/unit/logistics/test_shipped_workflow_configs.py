"""The workflow files shipped in ``config/workflows`` load and run.

Every file must follow the workflow file format, and every step must name a
real ``codomyrmex.<module>.<action>``. ``tests/error_test_workflow.json`` is the
one intentional exception: its action does not exist, so the workflow fails at
dispatch. Each workflow is also run for real, from an otherwise empty project
directory so the analysis steps have little to read.

Zero-mock policy: the real TaskOrchestrator dispatches the real actions.
"""

from __future__ import annotations

import json

import pytest
from tests.support.repo_paths import REPO_ROOT

from codomyrmex.exceptions import TaskExecutionError
from codomyrmex.logistics.orchestration.project.resource_manager import (
    ResourceManager,
)
from codomyrmex.logistics.orchestration.project.task_orchestrator import (
    TaskOrchestrator,
    resolve_module_action,
)
from codomyrmex.logistics.orchestration.project.workflow_manager import (
    WorkflowManager,
    WorkflowStatus,
)

pytestmark = pytest.mark.unit

WORKFLOWS_DIR = REPO_ROOT / "config" / "workflows"
WORKFLOW_FILES = sorted(WORKFLOWS_DIR.glob("*/*.json"))
ERROR_FIXTURE = WORKFLOWS_DIR / "tests" / "error_test_workflow.json"
MISSING_ACTION = "nonexistent_action_for_error_tests"


def file_id(path) -> str:
    return path.relative_to(WORKFLOWS_DIR).as_posix()


@pytest.fixture(scope="module")
def orchestrator():
    orch = TaskOrchestrator(max_workers=4, resource_manager=ResourceManager())
    yield orch
    orch.stop_execution()


def load(path, tmp_path, orchestrator) -> tuple[WorkflowManager, str]:
    """Load the directory containing ``path``; return the manager and its name."""
    manager = WorkflowManager(
        persistence_dir=tmp_path / "persist",
        config_dir=path.parent,
        task_orchestrator=orchestrator,
    )
    names = [name for name, file in manager.workflow_files.items() if file == path]
    assert names, f"{file_id(path)} was not loaded (see the logged reason)"
    return manager, names[0]


def test_every_subdirectory_has_workflows():
    assert {path.parent.name for path in WORKFLOW_FILES} == {
        "examples",
        "production",
        "tests",
    }


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=file_id)
def test_steps_name_real_actions(path, tmp_path, orchestrator):
    manager, name = load(path, tmp_path, orchestrator)
    steps = manager.get_workflow(name)
    assert steps

    for step in steps:
        assert "{{" not in json.dumps(step.parameters), (
            f"{step.name}: {{{{...}}}} substitution is not supported"
        )
        if path == ERROR_FIXTURE:
            with pytest.raises(TaskExecutionError, match=MISSING_ACTION):
                resolve_module_action(step.module, step.action)
        else:
            assert callable(resolve_module_action(step.module, step.action))


@pytest.mark.slow
@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=file_id)
def test_workflow_runs(path, tmp_path, orchestrator, monkeypatch):
    manager, name = load(path, tmp_path, orchestrator)
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "README.md").write_text("# Demo\n\n## Overview\n\nText.\n")
    monkeypatch.chdir(project_dir)

    execution = manager.execute_workflow(name)

    if path == ERROR_FIXTURE:
        assert execution.status is WorkflowStatus.FAILED
        assert MISSING_ACTION in (execution.error or "")
    else:
        assert execution.status is WorkflowStatus.COMPLETED, execution.error
        assert all(
            result["status"] == "completed"
            for result in execution.step_results.values()
        )
    assert sorted(p.name for p in project_dir.iterdir() if p.name != ".ruff_cache") == [
        "README.md"
    ]


def test_error_fixture_says_it_fails_on_purpose():
    description = json.loads(ERROR_FIXTURE.read_text(encoding="utf-8"))["description"]
    assert "on purpose" in description
    assert MISSING_ACTION in description
