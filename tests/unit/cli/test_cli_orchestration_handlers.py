"""End-to-end tests for the ``codomyrmex workflow`` and ``project`` handlers.

Each test runs the handlers in a fresh ``tmp_path`` working directory (via
``monkeypatch.chdir``) and checks what a *new* WorkflowManager/ProjectManager
in that directory sees, which is what a later ``codomyrmex`` process sees. The
workflow templates are run for real through the task orchestrator, and one
test drives the real CLI entry point in separate processes.

Zero-mock policy: real files, real actions, real subprocesses.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from codomyrmex.cli.handlers.orchestration import (
    WORKFLOW_TEMPLATES,
    handle_project_create,
    handle_project_list,
    handle_workflow_create,
    list_workflows,
    run_workflow,
)
from codomyrmex.logistics.orchestration.project import (
    PROJECT_FILE_NAME,
    ProjectManager,
    ProjectStatus,
    ProjectType,
    WorkflowManager,
    WorkflowStep,
)
from codomyrmex.logistics.orchestration.project.task_orchestrator import (
    resolve_module_action,
)

pytestmark = pytest.mark.unit

WORKFLOW_DIR = ("config", "workflows", "production")


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """An almost empty project directory used as the working directory."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    return tmp_path


def workflow_file(workdir, name: str):
    return workdir.joinpath(*WORKFLOW_DIR, f"{name}.json")


def write_workflow(workdir, name: str, steps: list[dict]) -> None:
    path = workflow_file(workdir, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"name": name, "steps": steps}), encoding="utf-8")


def listed_entries(out: str) -> dict[str, list[str]]:
    """Split list output into entries: a 2-space-indented name, then details."""
    entries: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in out.splitlines():
        if line.startswith("    ") and current is not None:
            current.append(line.strip())
        elif line.startswith("  ") and line.strip():
            current = entries.setdefault(line.strip(), [])
    return entries


class TestWorkflowCreate:
    @pytest.mark.slow
    @pytest.mark.parametrize("template", sorted(WORKFLOW_TEMPLATES))
    def test_template_is_saved_loaded_and_runs(self, workdir, capsys, template):
        assert handle_workflow_create("demo", template) is True
        created = capsys.readouterr().out
        path = workflow_file(workdir, "demo")
        assert f"Saved to: {path}" in created

        expected = [WorkflowStep(**spec) for spec in WORKFLOW_TEMPLATES[template]]
        assert json.loads(path.read_text(encoding="utf-8"))["name"] == "demo"
        assert WorkflowManager().get_workflow("demo") == expected
        for step in expected:
            assert callable(resolve_module_action(step.module, step.action))
            assert "{{" not in json.dumps(step.parameters)

        assert run_workflow("demo") is True
        ran = capsys.readouterr().out
        for step in expected:
            assert f"{step.name} ({step.module}.{step.action}): completed" in ran
        assert "Workflow 'demo' completed successfully" in ran

    @pytest.mark.parametrize(
        ("template", "resolved"),
        [
            (None, "basic"),
            ("", "basic"),
            ("ai_analysis", "ai-analysis"),
            ("AI-Analysis", "ai-analysis"),
            ("build_and_test", "build-and-test"),
        ],
    )
    def test_template_spellings(self, workdir, capsys, template, resolved):
        assert handle_workflow_create("demo", template) is True
        assert f"from template '{resolved}'" in capsys.readouterr().out
        assert WorkflowManager().get_workflow("demo") == [
            WorkflowStep(**spec) for spec in WORKFLOW_TEMPLATES[resolved]
        ]

    def test_unknown_template_is_rejected(self, workdir, capsys):
        assert handle_workflow_create("demo", "ai-insights") is False
        out = capsys.readouterr().out
        assert "Unknown workflow template 'ai-insights'" in out
        assert "basic, ai-analysis, build-and-test" in out
        assert sorted(p.name for p in workdir.iterdir()) == ["README.md"]

    def test_existing_workflow_is_not_replaced(self, workdir, capsys):
        assert handle_workflow_create("demo", "basic") is True
        before = workflow_file(workdir, "demo").read_text(encoding="utf-8")

        assert handle_workflow_create("demo", "build-and-test") is False

        assert "already exists" in capsys.readouterr().out
        assert workflow_file(workdir, "demo").read_text(encoding="utf-8") == before

    @pytest.mark.parametrize("name", ["../escape", "has space", "a/b"])
    def test_name_unusable_as_file_name_is_rejected(self, workdir, capsys, name):
        assert handle_workflow_create(name, "basic") is False
        assert "cannot be used as a file name" in capsys.readouterr().out
        assert list(workdir.joinpath(*WORKFLOW_DIR).iterdir()) == []
        assert not (workdir / "config" / "workflows" / "escape.json").exists()

    def test_numeric_names_from_fire_are_accepted(self, workdir):
        # Fire passes ``workflow create 2024`` as the int 2024.
        assert handle_workflow_create(2024, None) is True
        assert workflow_file(workdir, "2024").is_file()
        assert run_workflow(2024) is True
        assert handle_project_create(2024, "custom") is True
        assert ProjectManager().get_project("2024") is not None

    def test_non_integer_numeric_name_is_rejected(self, workdir, capsys):
        assert handle_workflow_create(1.5, None) is False
        assert handle_project_create(1.5, "custom") is False
        assert "quote it" in capsys.readouterr().out
        assert sorted(p.name for p in workdir.iterdir()) == ["README.md"]

    def test_numeric_template_is_unknown(self, workdir, capsys):
        assert handle_workflow_create("demo", 7) is False
        assert "Unknown workflow template '7'" in capsys.readouterr().out


class TestWorkflowListAndRun:
    def test_list_shows_steps_modules_and_file(self, workdir, capsys):
        handle_workflow_create("analysis", "ai-analysis")
        handle_workflow_create("checks", "build-and-test")
        write_workflow(
            workdir,
            "manual",
            [
                {
                    "name": "only",
                    "module": "environment_setup",
                    "action": "validate_environment",
                }
            ],
        )
        capsys.readouterr()

        assert list_workflows() is True
        out = capsys.readouterr().out

        config_dir = workdir.joinpath(*WORKFLOW_DIR)
        assert f"Definitions directory: {config_dir}" in out
        assert listed_entries(out) == {
            "analysis": [
                "Steps: 3",
                "Modules: coding.static_analysis, security",
                f"File: {config_dir / 'analysis.json'}",
            ],
            "checks": [
                "Steps: 3",
                "Modules: environment_setup, ci_cd_automation.build, "
                "coding.static_analysis",
                f"File: {config_dir / 'checks.json'}",
            ],
            "manual": [
                "Steps: 1",
                "Modules: environment_setup",
                f"File: {config_dir / 'manual.json'}",
            ],
        }

    def test_list_without_workflows(self, workdir, capsys):
        assert list_workflows() is True
        assert "No workflows found" in capsys.readouterr().out

    def test_run_unknown_workflow(self, workdir, capsys):
        handle_workflow_create("present", "basic")
        capsys.readouterr()

        assert run_workflow("absent") is False
        out = capsys.readouterr().out
        assert "Workflow 'absent' not found" in out
        assert "Available: present" in out

    def test_run_reports_failing_step(self, workdir, capsys):
        write_workflow(
            workdir,
            "broken",
            [
                {
                    "name": "ok",
                    "module": "environment_setup",
                    "action": "validate_environment",
                },
                {
                    "name": "bad",
                    "module": "environment_setup",
                    "action": "no_such_action",
                },
            ],
        )

        assert run_workflow("broken") is False
        out = capsys.readouterr().out
        assert "ok (environment_setup.validate_environment): completed" in out
        assert "bad (environment_setup.no_such_action): failed" in out
        assert "has no action 'no_such_action'" in out
        assert "Workflow 'broken' failed" in out

    def test_run_rejects_invalid_dependencies(self, workdir, capsys):
        write_workflow(
            workdir,
            "cyclic",
            [
                {"name": "a", "module": "m", "action": "x", "dependencies": ["b"]},
                {"name": "b", "module": "m", "action": "x", "dependencies": ["a"]},
            ],
        )

        assert run_workflow("cyclic") is False
        assert "could not run" in capsys.readouterr().out


class TestProjectCreate:
    def test_created_project_is_listed_by_new_manager(self, workdir, capsys):
        assert (
            handle_project_create("alpha", "ai-analysis", description="First") is True
        )
        out = capsys.readouterr().out

        project = ProjectManager().get_project("alpha")
        assert project is not None
        assert project.path == workdir / "alpha"
        assert project.type is ProjectType.AI_ANALYSIS
        assert project.status is ProjectStatus.ACTIVE
        assert project.description == "First"
        assert (workdir / "alpha" / PROJECT_FILE_NAME).is_file()
        for line in (
            f"Path: {workdir / 'alpha'}",
            "Type: ai_analysis",
            "Status: active",
            "Description: First",
            f"Metadata: {workdir / 'alpha' / PROJECT_FILE_NAME}",
        ):
            assert line in out

    @pytest.mark.parametrize(
        ("template", "expected"),
        [
            ("ai_analysis", ProjectType.AI_ANALYSIS),
            ("ai-analysis", ProjectType.AI_ANALYSIS),
            ("Web-Application", ProjectType.WEB_APPLICATION),
            ("custom", ProjectType.CUSTOM),
        ],
    )
    def test_template_spellings(self, workdir, template, expected):
        assert handle_project_create("p", template) is True
        assert ProjectManager().get_project("p").type is expected

    def test_unknown_template_lists_valid_ones(self, workdir, capsys):
        assert handle_project_create("p", "spaceship") is False
        out = capsys.readouterr().out
        assert "Unknown project template 'spaceship'" in out
        for project_type in ProjectType:
            assert project_type.value in out
        assert not (workdir / "p").exists()

    def test_duplicate_project_is_rejected(self, workdir, capsys):
        assert handle_project_create("alpha", "custom") is True
        assert handle_project_create("alpha", "research") is False
        assert "Project 'alpha' already exists" in capsys.readouterr().out
        assert ProjectManager().get_project("alpha").type is ProjectType.CUSTOM

    def test_existing_directory_is_rejected(self, workdir, capsys):
        (workdir / "taken").mkdir()
        (workdir / "taken" / "keep.txt").write_text("data", encoding="utf-8")

        assert handle_project_create("taken", "custom") is False

        assert "already exists" in capsys.readouterr().out
        assert sorted(p.name for p in (workdir / "taken").iterdir()) == ["keep.txt"]

    @pytest.mark.parametrize("name", ["../escape", "a/b", "..", ""])
    def test_name_must_be_a_directory_name(self, workdir, capsys, name):
        assert handle_project_create(name, "custom") is False
        assert "Invalid project name" in capsys.readouterr().out
        assert sorted(p.name for p in workdir.iterdir()) == ["README.md"]
        assert not (workdir.parent / "escape").exists()

    def test_scaffolding_failure_is_not_reported_as_success(self, workdir, capsys):
        (workdir / "a-file").write_text("not a directory", encoding="utf-8")

        result = handle_project_create(
            "p", "custom", path=str(workdir / "a-file" / "p")
        )

        assert result is False
        out = capsys.readouterr().out
        assert "Failed to create project 'p'" in out
        assert "Created project" not in out
        assert ProjectManager().get_project("p") is None

    def test_path_outside_working_directory_warns(self, workdir, tmp_path, capsys):
        target = tmp_path / "elsewhere" / "gamma"

        assert handle_project_create("gamma", "custom", path=str(target)) is True

        out = capsys.readouterr().out
        assert f"   {target.parent.resolve()}" in out.splitlines()
        assert (target / PROJECT_FILE_NAME).is_file()
        assert ProjectManager().get_project("gamma") is None
        assert ProjectManager(projects_root=target.parent).get_project("gamma")


class TestProjectList:
    def test_lists_saved_projects(self, workdir, capsys):
        handle_project_create("beta", "web-application", description="Web")
        handle_project_create("alpha", "research")
        ProjectManager().update_project_status("alpha", ProjectStatus.PAUSED)
        capsys.readouterr()

        assert handle_project_list() is True
        out = capsys.readouterr().out

        assert f"Projects directory: {workdir}" in out
        entries = listed_entries(out)
        assert list(entries) == ["alpha", "beta"]
        saved = {p.name: p for p in ProjectManager().list_projects()}
        assert entries["alpha"] == [
            "Status: paused",
            "Type: research",
            f"Path: {workdir / 'alpha'}",
            f"Updated: {saved['alpha'].updated_at.isoformat(timespec='seconds')}",
        ]
        assert entries["beta"] == [
            "Status: active",
            "Type: web_application",
            f"Path: {workdir / 'beta'}",
            "Description: Web",
            f"Updated: {saved['beta'].updated_at.isoformat(timespec='seconds')}",
        ]

    def test_without_projects(self, workdir, capsys):
        assert handle_project_list() is True
        assert "No projects found" in capsys.readouterr().out


def run_cli_process(workdir, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "codomyrmex.cli", *args],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def run_cli(workdir, *args: str) -> str:
    completed = run_cli_process(workdir, *args)
    assert completed.returncode == 0, completed.stderr
    return completed.stdout


@pytest.mark.slow
def test_cli_state_survives_between_processes(workdir):
    """Regression: create/list/run in separate processes used to lose state."""
    created = run_cli(workdir, "workflow", "create", "demo", "--template", "basic")
    assert "Created workflow 'demo'" in created

    assert "demo" in run_cli(workdir, "workflow", "list")
    ran = run_cli(workdir, "workflow", "run", "demo")
    assert (
        "validate_environment (environment_setup.validate_environment): completed"
        in ran
    )
    assert "Workflow 'demo' completed successfully" in ran

    assert "Created project 'alpha'" in run_cli(
        workdir, "project", "create", "alpha", "--template", "ai-analysis"
    )
    listed = run_cli(workdir, "project", "list")
    assert "alpha" in listed
    assert "Type: ai_analysis" in listed


@pytest.mark.slow
def test_cli_process_exit_status_reflects_failure(workdir):
    """Regression: failed commands exited 0, hiding failures from scripts."""
    failed = run_cli_process(workdir, "workflow", "run", "does-not-exist")
    assert failed.returncode == 1
    assert "does-not-exist" in failed.stdout + failed.stderr
