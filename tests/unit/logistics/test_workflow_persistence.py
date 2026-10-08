"""Tests for saving and loading WorkflowManager definitions.

``create_workflow(..., persist=True)`` / ``save_workflow`` write a workflow to
``config_dir`` in the format ``_load_workflows_from_config`` reads, so a manager
created later (for example by another CLI process) sees it. Invalid workflows
are rejected before anything is written, and files that do not follow the
format are skipped when loading.

Zero-mock policy: real files under ``tmp_path``, steps run real registered
functions on a real TaskOrchestrator.
"""

from __future__ import annotations

import json
import logging

import pytest

from codomyrmex.logistics.orchestration.project.resource_manager import (
    ResourceManager,
)
from codomyrmex.logistics.orchestration.project.task_orchestrator import (
    TaskOrchestrator,
)
from codomyrmex.logistics.orchestration.project.workflow_manager import (
    WorkflowManager,
    WorkflowStatus,
    WorkflowStep,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def orchestrator():
    orch = TaskOrchestrator(max_workers=2, resource_manager=ResourceManager())
    orch.register_action("test", "echo", lambda **kwargs: kwargs)
    yield orch
    orch.stop_execution()


@pytest.fixture
def config_dir(tmp_path):
    return tmp_path / "workflows"


def make_manager(tmp_path, config_dir, orchestrator) -> WorkflowManager:
    return WorkflowManager(
        persistence_dir=tmp_path / "persist",
        config_dir=config_dir,
        task_orchestrator=orchestrator,
    )


def sample_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            name="second",
            module="test",
            action="echo",
            parameters={"label": "second", "nested": {"items": [1, 2.5, None]}},
            dependencies=["first"],
            required=False,
            timeout=12.5,
            retry_count=2,
        ),
        WorkflowStep(name="first", module="test", action="echo"),
    ]


def json_files(directory) -> list[str]:
    return sorted(path.name for path in directory.iterdir())


class TestSaveFormat:
    def test_create_without_persist_writes_nothing(
        self, tmp_path, config_dir, orchestrator
    ):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        manager.create_workflow("memory_only", sample_steps())

        assert json_files(config_dir) == []
        assert "memory_only" not in manager.workflow_files
        assert make_manager(tmp_path, config_dir, orchestrator).list_workflows() == []

    def test_persist_writes_loader_format(self, tmp_path, config_dir, orchestrator):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        assert manager.create_workflow("pipeline", sample_steps(), persist=True)

        path = config_dir / "pipeline.json"
        assert manager.workflow_files["pipeline"] == path
        assert json_files(config_dir) == ["pipeline.json"]
        assert json.loads(path.read_text(encoding="utf-8")) == {
            "name": "pipeline",
            "steps": [
                {
                    "name": "second",
                    "module": "test",
                    "action": "echo",
                    "parameters": {
                        "label": "second",
                        "nested": {"items": [1, 2.5, None]},
                    },
                    "dependencies": ["first"],
                    "timeout": 12.5,
                    "max_retries": 2,
                    "required": False,
                },
                {
                    "name": "first",
                    "module": "test",
                    "action": "echo",
                    "parameters": {},
                    "dependencies": [],
                    "timeout": None,
                    "max_retries": 0,
                    "required": True,
                },
            ],
        }

    def test_new_manager_loads_identical_steps(
        self, tmp_path, config_dir, orchestrator
    ):
        make_manager(tmp_path, config_dir, orchestrator).create_workflow(
            "pipeline", sample_steps(), persist=True
        )

        reloaded = make_manager(tmp_path, config_dir, orchestrator)

        assert reloaded.list_workflows() == ["pipeline"]
        assert reloaded.get_workflow("pipeline") == sample_steps()
        assert reloaded.workflow_files["pipeline"] == config_dir / "pipeline.json"

    def test_persisted_workflow_runs_in_new_manager(
        self, tmp_path, config_dir, orchestrator
    ):
        make_manager(tmp_path, config_dir, orchestrator).create_workflow(
            "pipeline", sample_steps(), persist=True
        )

        execution = make_manager(tmp_path, config_dir, orchestrator).execute_workflow(
            "pipeline"
        )

        assert execution.status is WorkflowStatus.COMPLETED
        assert execution.step_results["second"]["result"] == {
            "label": "second",
            "nested": {"items": [1, 2.5, None]},
        }

    def test_overwrite_with_persist_replaces_file(
        self, tmp_path, config_dir, orchestrator
    ):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        manager.create_workflow("wf", sample_steps(), persist=True)
        replacement = [WorkflowStep(name="only", module="test", action="echo")]
        manager.create_workflow("wf", replacement, persist=True)

        assert (
            make_manager(tmp_path, config_dir, orchestrator).get_workflow("wf")
            == replacement
        )
        assert json_files(config_dir) == ["wf.json"]

    def test_loaded_workflow_is_saved_back_to_its_file(
        self, tmp_path, config_dir, orchestrator
    ):
        config_dir.mkdir()
        source = config_dir / "differently-named.json"
        source.write_text(
            json.dumps(
                {
                    "name": "custom name",
                    "description": "extra keys are ignored",
                    "steps": [{"name": "a", "module": "test", "action": "echo"}],
                }
            ),
            encoding="utf-8",
        )
        manager = make_manager(tmp_path, config_dir, orchestrator)
        assert manager.workflow_files["custom name"] == source

        manager.workflows["custom name"].append(
            WorkflowStep(name="b", module="test", action="echo", dependencies=["a"])
        )
        assert manager.save_workflow("custom name") == source

        assert json_files(config_dir) == ["differently-named.json"]
        reloaded = make_manager(tmp_path, config_dir, orchestrator)
        assert [step.name for step in reloaded.workflows["custom name"]] == [
            "a",
            "b",
        ]


class TestSaveRejectsInvalidWorkflows:
    def test_unknown_workflow(self, tmp_path, config_dir, orchestrator):
        with pytest.raises(KeyError, match="not registered"):
            make_manager(tmp_path, config_dir, orchestrator).save_workflow("nope")

    @pytest.mark.parametrize("name", ["../escape", "a/b", "with space", ".hidden"])
    def test_name_unusable_as_file_name(self, tmp_path, config_dir, orchestrator, name):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        with pytest.raises(ValueError, match="cannot be used as a file name"):
            manager.create_workflow(name, sample_steps(), persist=True)

        assert name not in manager.workflows
        assert json_files(config_dir) == []
        assert sorted(p.name for p in tmp_path.iterdir()) == ["persist", "workflows"]

    @pytest.mark.parametrize(
        ("steps", "error", "match"),
        [
            (
                [
                    WorkflowStep(
                        name="a", module="test", action="echo", dependencies=["x"]
                    )
                ],
                ValueError,
                "invalid dependencies",
            ),
            (
                [
                    WorkflowStep(
                        name="a", module="test", action="echo", dependencies=["b"]
                    ),
                    WorkflowStep(
                        name="b", module="test", action="echo", dependencies=["a"]
                    ),
                ],
                ValueError,
                "invalid dependencies",
            ),
            (
                [
                    WorkflowStep(name="a", module="test", action="echo"),
                    WorkflowStep(name="a", module="test", action="echo"),
                ],
                ValueError,
                "duplicate step names",
            ),
            (
                [WorkflowStep(name="a", module="test", action="echo", run_if="x > 1")],
                NotImplementedError,
                "run_if",
            ),
            (
                [WorkflowStep(name="a", module="", action="echo")],
                ValueError,
                "'module' must be a non-empty string",
            ),
            (
                [
                    WorkflowStep(
                        name="a", module="test", action="echo", parameters={"x": {1, 2}}
                    )
                ],
                TypeError,
                "not JSON serializable",
            ),
            (
                [
                    WorkflowStep(
                        name="a",
                        module="test",
                        action="echo",
                        parameters={"x": float("nan")},
                    )
                ],
                ValueError,
                "not JSON compliant",
            ),
        ],
    )
    def test_nothing_written_and_registration_unchanged(
        self, tmp_path, config_dir, orchestrator, steps, error, match
    ):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        with pytest.raises(error, match=match):
            manager.create_workflow("broken", steps, persist=True)

        assert "broken" not in manager.workflows
        assert json_files(config_dir) == []

    def test_failed_overwrite_restores_previous_and_keeps_file(
        self, tmp_path, config_dir, orchestrator
    ):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        manager.create_workflow("wf", sample_steps(), persist=True)
        before = (config_dir / "wf.json").read_bytes()
        cyclic = [
            WorkflowStep(name="a", module="test", action="echo", dependencies=["a"])
        ]

        with pytest.raises(ValueError):
            manager.create_workflow("wf", cyclic, persist=True)

        assert manager.get_workflow("wf") == sample_steps()
        assert (config_dir / "wf.json").read_bytes() == before
        assert json_files(config_dir) == ["wf.json"]

    def test_does_not_overwrite_file_holding_another_workflow(
        self, tmp_path, config_dir, orchestrator
    ):
        config_dir.mkdir()
        other = config_dir / "wf.json"
        content = json.dumps(
            {"name": "other", "steps": [{"name": "s", "module": "m", "action": "a"}]}
        )
        other.write_text(content, encoding="utf-8")
        manager = make_manager(tmp_path, config_dir, orchestrator)

        with pytest.raises(ValueError, match="already defines workflow 'other'"):
            manager.create_workflow("wf", sample_steps(), persist=True)

        assert other.read_text(encoding="utf-8") == content
        assert "wf" not in manager.workflows

    def test_does_not_overwrite_unreadable_file(
        self, tmp_path, config_dir, orchestrator
    ):
        config_dir.mkdir()
        broken = config_dir / "wf.json"
        broken.write_text("{not json", encoding="utf-8")
        manager = make_manager(tmp_path, config_dir, orchestrator)

        with pytest.raises(ValueError, match="not a readable workflow file"):
            manager.create_workflow("wf", sample_steps(), persist=True)

        assert broken.read_text(encoding="utf-8") == "{not json"

    def test_file_created_after_load_with_same_name_is_updated(
        self, tmp_path, config_dir, orchestrator
    ):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        make_manager(tmp_path, config_dir, orchestrator).create_workflow(
            "wf", sample_steps(), persist=True
        )
        replacement = [WorkflowStep(name="only", module="test", action="echo")]

        manager.create_workflow("wf", replacement, persist=True)

        assert (
            make_manager(tmp_path, config_dir, orchestrator).get_workflow("wf")
            == replacement
        )


class TestLoading:
    def write(self, config_dir, file_name: str, data) -> None:
        config_dir.mkdir(exist_ok=True)
        text = data if isinstance(data, str) else json.dumps(data)
        (config_dir / file_name).write_text(text, encoding="utf-8")

    def test_name_defaults_to_file_stem(self, tmp_path, config_dir, orchestrator):
        self.write(
            config_dir,
            "stem-name.json",
            {"steps": [{"name": "a", "module": "test", "action": "echo"}]},
        )
        manager = make_manager(tmp_path, config_dir, orchestrator)
        assert manager.list_workflows() == ["stem-name"]
        assert manager.get_workflow("stem-name") == [
            WorkflowStep(name="a", module="test", action="echo")
        ]

    @pytest.mark.parametrize(
        ("content", "reason"),
        [
            ("{not json", "Expecting property name"),
            ("[]", "must contain a JSON object"),
            ({"name": "x"}, "'steps' must be a list"),
            ({"name": "", "steps": []}, "'name' must be a non-empty string"),
            ({"steps": ["step"]}, "step 0 must be an object"),
            ({"steps": [{"name": "a", "module": "m"}]}, "'action' must be a non-empty"),
            (
                {
                    "steps": [
                        {"name": "a", "module": "m", "action": "x", "parameters": []}
                    ]
                },
                "'parameters' must be an object",
            ),
            (
                {
                    "steps": [
                        {"name": "a", "module": "m", "action": "x", "dependencies": "b"}
                    ]
                },
                "'dependencies' must be a list",
            ),
            (
                {
                    "steps": [
                        {"name": "a", "module": "m", "action": "x", "timeout": "5"}
                    ]
                },
                "'timeout' must be a number",
            ),
            (
                {
                    "steps": [
                        {"name": "a", "module": "m", "action": "x", "max_retries": -1}
                    ]
                },
                "must not be negative",
            ),
            (
                {
                    "steps": [
                        {"name": "a", "module": "m", "action": "x", "required": "yes"}
                    ]
                },
                "'required' must be true or false",
            ),
            (
                {"steps": [{"name": "a", "module": "m", "action": "x", "run_if": "1"}]},
                "run_if conditions are not supported",
            ),
        ],
    )
    def test_invalid_file_is_logged_and_skipped(
        self, tmp_path, config_dir, orchestrator, caplog, content, reason
    ):
        self.write(config_dir, "bad.json", content)
        self.write(
            config_dir,
            "good.json",
            {
                "name": "good",
                "steps": [{"name": "a", "module": "test", "action": "echo"}],
            },
        )

        with caplog.at_level(logging.WARNING):
            manager = make_manager(tmp_path, config_dir, orchestrator)

        assert manager.list_workflows() == ["good"]
        skipped = [
            r.getMessage() for r in caplog.records if "bad.json" in r.getMessage()
        ]
        assert len(skipped) == 1
        assert "Skipping workflow file" in skipped[0]
        assert reason in skipped[0]

    def test_duplicate_name_later_file_wins_with_warning(
        self, tmp_path, config_dir, orchestrator, caplog
    ):
        for file_name, action in (("a.json", "first"), ("b.json", "second")):
            self.write(
                config_dir,
                file_name,
                {
                    "name": "dup",
                    "steps": [{"name": "s", "module": "m", "action": action}],
                },
            )

        with caplog.at_level(logging.WARNING):
            manager = make_manager(tmp_path, config_dir, orchestrator)

        assert manager.get_workflow("dup")[0].action == "second"
        assert manager.workflow_files["dup"] == config_dir / "b.json"
        assert any(
            "replaces the definition" in record.getMessage()
            for record in caplog.records
        )

    def test_temporary_files_are_not_left_or_loaded(
        self, tmp_path, config_dir, orchestrator
    ):
        manager = make_manager(tmp_path, config_dir, orchestrator)
        for index in range(3):
            manager.create_workflow(f"wf{index}", sample_steps(), persist=True)

        assert json_files(config_dir) == ["wf0.json", "wf1.json", "wf2.json"]
