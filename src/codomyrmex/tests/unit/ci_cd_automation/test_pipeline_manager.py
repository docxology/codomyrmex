"""Comprehensive unit tests for ci_cd_automation.pipeline.manager.PipelineManager.

Tests cover: constructor init, pipeline creation from JSON/YAML, config parsing,
pipeline validation, stage dependency validation, variable substitution,
conditional execution, visualization, optimization, save/load round-trip,
parallel execution, synchronous pipeline runs, and cancellation.

Zero-mock policy: all tests use real objects and tmp_path for filesystem.
"""

import asyncio
import json
import os

import pytest
import yaml

from codomyrmex.ci_cd_automation.pipeline.manager import PipelineManager
from codomyrmex.ci_cd_automation.pipeline.models import (
    JobStatus,
    Pipeline,
    PipelineJob,
    PipelineStage,
    PipelineStatus,
    StageStatus,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_config() -> dict:
    """Return the smallest valid pipeline config."""
    return {
        "name": "test_pipeline",
        "stages": [
            {
                "name": "build",
                "jobs": [
                    {
                        "name": "compile",
                        "commands": ["echo hello"],
                    }
                ],
            }
        ],
    }


def _multi_stage_config() -> dict:
    """Return a config with multiple stages and dependencies."""
    return {
        "name": "multi_stage",
        "description": "Pipeline with multiple stages",
        "variables": {"VERSION": "1.0.0"},
        "triggers": {},
        "timeout": 3600,
        "stages": [
            {
                "name": "build",
                "dependencies": [],
                "environment": {"BUILD_TYPE": "release"},
                "allow_failure": False,
                "parallel": True,
                "jobs": [
                    {
                        "name": "compile",
                        "commands": ["echo build ${VERSION}"],
                        "environment": {},
                        "artifacts": ["build/output.bin"],
                        "dependencies": [],
                        "timeout": 600,
                        "retry_count": 1,
                        "allow_failure": False,
                    },
                    {
                        "name": "lint",
                        "commands": ["echo lint"],
                        "timeout": 300,
                    },
                ],
            },
            {
                "name": "test",
                "dependencies": ["build"],
                "parallel": False,
                "jobs": [
                    {
                        "name": "unit_tests",
                        "commands": ["echo test"],
                    }
                ],
            },
            {
                "name": "deploy",
                "dependencies": ["test"],
                "allow_failure": True,
                "jobs": [
                    {
                        "name": "deploy_staging",
                        "commands": ["echo deploy"],
                        "allow_failure": True,
                    }
                ],
            },
        ],
    }


def _write_config(tmp_path, config, filename="pipeline.json"):
    """Write a pipeline config dict to a file and return the path."""
    path = tmp_path / filename
    with open(path, "w") as f:
        if filename.endswith((".yaml", ".yml")):
            yaml.dump(config, f, default_flow_style=False)
        else:
            json.dump(config, f, indent=2)
    return str(path)


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPipelineManagerInit:
    """Tests for PipelineManager constructor."""

    def test_init_default_workspace(self, tmp_path):
        """Constructor creates workspace dirs when workspace_dir is given."""
        workspace = str(tmp_path / "ws")
        mgr = PipelineManager(workspace_dir=workspace)
        assert mgr.workspace_dir == workspace
        assert os.path.isdir(workspace)
        assert os.path.isdir(os.path.join(workspace, "artifacts"))
        assert mgr.pipelines == {}
        assert mgr.active_executions == {}

    def test_init_without_workspace_uses_cwd(self, tmp_path, monkeypatch):
        """When no workspace_dir is passed, uses cwd/.pipelines."""
        # NOTE: monkeypatch.chdir is not mocking -- it actually changes cwd
        monkeypatch.chdir(tmp_path)
        mgr = PipelineManager()
        expected = os.path.join(str(tmp_path), ".pipelines")
        assert mgr.workspace_dir == expected
        assert os.path.isdir(expected)

    def test_init_idempotent_dirs(self, tmp_path):
        """Creating PipelineManager twice with same dir does not raise."""
        workspace = str(tmp_path / "ws")
        PipelineManager(workspace_dir=workspace)
        PipelineManager(workspace_dir=workspace)
        assert os.path.isdir(workspace)


@pytest.mark.unit
class TestCreatePipeline:
    """Tests for create_pipeline (file-based creation)."""

    def test_create_from_json(self, tmp_path):
        config = _minimal_config()
        path = _write_config(tmp_path, config, "pipeline.json")
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr.create_pipeline(path)
        assert pipeline.name == "test_pipeline"
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0].name == "build"
        assert len(pipeline.stages[0].jobs) == 1
        assert pipeline.stages[0].jobs[0].name == "compile"

    def test_create_from_yaml(self, tmp_path):
        config = _minimal_config()
        path = _write_config(tmp_path, config, "pipeline.yaml")
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr.create_pipeline(path)
        assert pipeline.name == "test_pipeline"

    def test_create_from_yml(self, tmp_path):
        config = _minimal_config()
        path = _write_config(tmp_path, config, "pipeline.yml")
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr.create_pipeline(path)
        assert pipeline.name == "test_pipeline"

    def test_create_pipeline_registers(self, tmp_path):
        config = _minimal_config()
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        assert "test_pipeline" in mgr.pipelines

    def test_create_pipeline_multi_stage(self, tmp_path):
        config = _multi_stage_config()
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr.create_pipeline(path)
        assert len(pipeline.stages) == 3
        assert pipeline.stages[1].dependencies == ["build"]
        assert pipeline.stages[0].jobs[0].retry_count == 1

    def test_create_pipeline_bad_path_raises(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        with pytest.raises(Exception):
            mgr.create_pipeline("/nonexistent/path.json")

    def test_create_pipeline_invalid_json_raises(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json!!!")
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        with pytest.raises(Exception):
            mgr.create_pipeline(str(bad_file))

    def test_create_pipeline_defaults(self, tmp_path):
        """Config missing optional fields gets correct defaults."""
        config = {"stages": []}
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr.create_pipeline(path)
        assert pipeline.name == "unnamed_pipeline"
        assert pipeline.description == ""
        assert pipeline.variables == {}
        assert pipeline.timeout == 7200


@pytest.mark.unit
class TestParsePipelineConfig:
    """Tests for _parse_pipeline_config (internal parsing logic)."""

    def test_parse_full_config(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = _multi_stage_config()
        pipeline = mgr._parse_pipeline_config(config)
        assert pipeline.name == "multi_stage"
        assert pipeline.description == "Pipeline with multiple stages"
        assert pipeline.variables == {"VERSION": "1.0.0"}
        assert pipeline.timeout == 3600

    def test_parse_job_fields(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = _multi_stage_config()
        pipeline = mgr._parse_pipeline_config(config)
        compile_job = pipeline.stages[0].jobs[0]
        assert compile_job.commands == ["echo build ${VERSION}"]
        assert compile_job.artifacts == ["build/output.bin"]
        assert compile_job.timeout == 600
        assert compile_job.retry_count == 1
        assert compile_job.allow_failure is False

    def test_parse_stage_properties(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = _multi_stage_config()
        pipeline = mgr._parse_pipeline_config(config)
        build_stage = pipeline.stages[0]
        assert build_stage.parallel is True
        assert build_stage.allow_failure is False
        assert build_stage.environment == {"BUILD_TYPE": "release"}
        test_stage = pipeline.stages[1]
        assert test_stage.parallel is False
        assert test_stage.dependencies == ["build"]

    def test_parse_empty_stages(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr._parse_pipeline_config({"name": "empty", "stages": []})
        assert pipeline.stages == []


@pytest.mark.unit
class TestValidatePipelineConfig:
    """Tests for validate_pipeline_config."""

    def test_valid_config(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = _minimal_config()
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is True
        assert errors == []

    def test_missing_name(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"stages": [{"name": "s1", "jobs": [{"name": "j1", "commands": ["echo"]}]}]}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False
        assert any("name" in e.lower() for e in errors)

    def test_missing_stages(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": "p1"}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False
        assert any("stages" in e.lower() for e in errors)

    def test_missing_both(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        is_valid, errors = mgr.validate_pipeline_config({})
        assert is_valid is False
        assert len(errors) >= 2

    def test_name_not_string(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": 123, "stages": []}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False
        assert any("string" in e.lower() for e in errors)

    def test_stages_not_list(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": "p1", "stages": "not_a_list"}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False
        assert any("list" in e.lower() for e in errors)

    def test_invalid_trigger(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": "p1", "stages": [], "triggers": ["invalid_trigger"]}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False
        assert any("trigger" in e.lower() for e in errors)

    def test_valid_triggers(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {
            "name": "p1",
            "stages": [],
            "triggers": ["push", "pull_request", "manual", "schedule"],
        }
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is True

    def test_triggers_not_list(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": "p1", "stages": [], "triggers": "push"}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False

    def test_invalid_timeout(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": "p1", "stages": [], "timeout": -1}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False
        assert any("timeout" in e.lower() for e in errors)

    def test_zero_timeout(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": "p1", "stages": [], "timeout": 0}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False

    def test_string_timeout(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        config = {"name": "p1", "stages": [], "timeout": "fast"}
        is_valid, errors = mgr.validate_pipeline_config(config)
        assert is_valid is False


@pytest.mark.unit
class TestValidateStageConfig:
    """Tests for _validate_stage_config."""

    def test_valid_stage(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "build", "jobs": [{"name": "j1", "commands": ["echo hi"]}]}
        errors = mgr._validate_stage_config(stage, 0)
        assert errors == []

    def test_missing_stage_name(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"jobs": [{"name": "j1", "commands": ["echo"]}]}
        errors = mgr._validate_stage_config(stage, 0)
        assert any("name" in e.lower() for e in errors)

    def test_stage_name_not_string(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": 42, "jobs": [{"name": "j1", "commands": ["echo"]}]}
        errors = mgr._validate_stage_config(stage, 0)
        assert any("string" in e.lower() for e in errors)

    def test_missing_jobs(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "build"}
        errors = mgr._validate_stage_config(stage, 0)
        assert any("jobs" in e.lower() for e in errors)

    def test_jobs_not_list(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "build", "jobs": "not_a_list"}
        errors = mgr._validate_stage_config(stage, 0)
        assert any("list" in e.lower() for e in errors)

    def test_invalid_dependencies_type(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {
            "name": "build",
            "jobs": [{"name": "j1", "commands": ["echo"]}],
            "dependencies": "not_a_list",
        }
        errors = mgr._validate_stage_config(stage, 0)
        assert any("dependencies" in e.lower() for e in errors)


@pytest.mark.unit
class TestValidateJobConfig:
    """Tests for _validate_job_config."""

    def test_valid_job(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": "build", "commands": ["echo hi"]}
        errors = mgr._validate_job_config(job, 0, 0)
        assert errors == []

    def test_missing_job_name(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"commands": ["echo hi"]}
        errors = mgr._validate_job_config(job, 0, 0)
        assert any("name" in e.lower() for e in errors)

    def test_job_name_not_string(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": 99, "commands": ["echo hi"]}
        errors = mgr._validate_job_config(job, 0, 0)
        assert any("string" in e.lower() for e in errors)

    def test_missing_commands(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": "j1"}
        errors = mgr._validate_job_config(job, 0, 0)
        assert any("commands" in e.lower() for e in errors)

    def test_commands_not_list(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": "j1", "commands": "echo hi"}
        errors = mgr._validate_job_config(job, 0, 0)
        assert any("list" in e.lower() for e in errors)

    def test_empty_commands(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": "j1", "commands": []}
        errors = mgr._validate_job_config(job, 0, 0)
        assert any("empty" in e.lower() for e in errors)

    def test_invalid_timeout(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": "j1", "commands": ["echo"], "timeout": -5}
        errors = mgr._validate_job_config(job, 0, 0)
        assert any("timeout" in e.lower() for e in errors)

    def test_invalid_retry_count(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": "j1", "commands": ["echo"], "retry_count": -1}
        errors = mgr._validate_job_config(job, 0, 0)
        assert any("retry" in e.lower() for e in errors)

    def test_valid_optional_fields(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = {"name": "j1", "commands": ["echo"], "timeout": 60, "retry_count": 3}
        errors = mgr._validate_job_config(job, 0, 0)
        assert errors == []


@pytest.mark.unit
class TestSubstituteVariables:
    """Tests for _substitute_variables."""

    def test_curly_brace_substitution(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        result = mgr._substitute_variables("echo ${VERSION}", {"VERSION": "2.0"})
        assert result == "echo 2.0"

    def test_dollar_sign_substitution(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        result = mgr._substitute_variables("echo $VERSION", {"VERSION": "2.0"})
        assert result == "echo 2.0"

    def test_multiple_variables(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        result = mgr._substitute_variables(
            "${APP}-${ENV}", {"APP": "myapp", "ENV": "prod"}
        )
        assert result == "myapp-prod"

    def test_no_variables(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        result = mgr._substitute_variables("echo hello", {})
        assert result == "echo hello"

    def test_unmatched_variable_left_as_is(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        result = mgr._substitute_variables("echo ${MISSING}", {"OTHER": "val"})
        assert "${MISSING}" in result


@pytest.mark.unit
class TestGetPipelineStatus:
    """Tests for get_pipeline_status and list_pipelines."""

    def test_get_existing(self, tmp_path):
        config = _minimal_config()
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.get_pipeline_status("test_pipeline")
        assert result is not None
        assert result.name == "test_pipeline"

    def test_get_nonexistent(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        result = mgr.get_pipeline_status("does_not_exist")
        assert result is None

    def test_list_pipelines_empty(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        assert mgr.list_pipelines() == []

    def test_list_pipelines_multiple(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        for name in ["alpha", "beta", "gamma"]:
            cfg = {"name": name, "stages": []}
            p = _write_config(tmp_path, cfg, f"{name}.json")
            mgr.create_pipeline(p)
        pipelines = mgr.list_pipelines()
        assert len(pipelines) == 3
        names = {p.name for p in pipelines}
        assert names == {"alpha", "beta", "gamma"}


@pytest.mark.unit
class TestCancelPipeline:
    """Tests for cancel_pipeline."""

    def test_cancel_no_active_execution(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        assert mgr.cancel_pipeline("nonexistent") is False

    def test_cancel_with_active_execution(self, tmp_path):
        """When there is an active execution entry, cancel returns True and sets CANCELLED."""
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        # Register a pipeline first
        config = _minimal_config()
        path = _write_config(tmp_path, config)
        mgr.create_pipeline(path)
        # Simulate an active execution with a real asyncio.Task
        loop = asyncio.new_event_loop()
        try:
            async def _dummy():
                await asyncio.sleep(100)

            task = loop.create_task(_dummy())
            mgr.active_executions["test_pipeline"] = task
            result = mgr.cancel_pipeline("test_pipeline")
            assert result is True
            assert mgr.pipelines["test_pipeline"].status == PipelineStatus.CANCELLED
            # task.cancel() puts it in "cancelling" state; it only becomes
            # "cancelled" after the event loop processes it. Verify cancel
            # was requested:
            assert task.cancelling() > 0 or task.cancelled()
        finally:
            loop.close()


@pytest.mark.unit
class TestConditionalStageExecution:
    """Tests for conditional_stage_execution."""

    def test_no_conditions_returns_true(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "build"}
        assert mgr.conditional_stage_execution(stage, {}) is True

    def test_branch_condition_match(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "deploy", "conditions": {"branch": "main"}}
        assert mgr.conditional_stage_execution(stage, {"branch": "main"}) is True

    def test_branch_condition_no_match(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "deploy", "conditions": {"branch": "main"}}
        assert mgr.conditional_stage_execution(stage, {"branch": "develop"}) is False

    def test_branch_wildcard(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "deploy", "conditions": {"branch": "release/*"}}
        assert mgr.conditional_stage_execution(stage, {"branch": "release/1.0"}) is True
        assert mgr.conditional_stage_execution(stage, {"branch": "feature/x"}) is False

    def test_environment_condition_match(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {
            "name": "deploy",
            "conditions": {"environment": {"CI": "true"}},
        }
        assert mgr.conditional_stage_execution(stage, {"env_CI": "true"}) is True

    def test_environment_condition_no_match(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {
            "name": "deploy",
            "conditions": {"environment": {"CI": "true"}},
        }
        assert mgr.conditional_stage_execution(stage, {"env_CI": "false"}) is False

    def test_custom_condition_failure(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "notify", "conditions": {"custom": "on failure"}}
        assert mgr.conditional_stage_execution(
            stage, {"has_previous_failures": True}
        ) is True

    def test_custom_condition_success(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "notify", "conditions": {"custom": "on success"}}
        assert mgr.conditional_stage_execution(
            stage, {"has_previous_failures": False}
        ) is True


@pytest.mark.unit
class TestMatchesPattern:
    """Tests for _matches_pattern."""

    def test_exact_match(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        assert mgr._matches_pattern("main", "main") is True

    def test_wildcard(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        assert mgr._matches_pattern("release/1.0", "release/*") is True

    def test_no_match(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        assert mgr._matches_pattern("feature/x", "main") is False

    def test_question_mark(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        assert mgr._matches_pattern("v1", "v?") is True
        assert mgr._matches_pattern("v10", "v?") is False


@pytest.mark.unit
class TestGeneratePipelineVisualization:
    """Tests for generate_pipeline_visualization."""

    def test_empty_pipeline(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = Pipeline(name="empty")
        viz = mgr.generate_pipeline_visualization(pipeline)
        assert "graph TD" in viz

    def test_single_stage_with_jobs(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        job = PipelineJob(name="compile", commands=["echo"])
        stage = PipelineStage(name="build", jobs=[job])
        pipeline = Pipeline(name="test", stages=[stage])
        viz = mgr.generate_pipeline_visualization(pipeline)
        assert "stage_build" in viz
        assert "job_compile" in viz
        assert "-->" in viz

    def test_stage_dependencies_in_viz(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        s1 = PipelineStage(name="build", jobs=[])
        s2 = PipelineStage(name="test", dependencies=["build"], jobs=[])
        pipeline = Pipeline(name="test", stages=[s1, s2])
        viz = mgr.generate_pipeline_visualization(pipeline)
        assert "stage_build --> stage_test" in viz

    def test_job_dependencies_in_viz(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        j1 = PipelineJob(name="compile", commands=["echo"])
        j2 = PipelineJob(name="link", commands=["echo"], dependencies=["compile"])
        stage = PipelineStage(name="build", jobs=[j1, j2])
        pipeline = Pipeline(name="test", stages=[stage])
        viz = mgr.generate_pipeline_visualization(pipeline)
        assert "job_compile --> job_link" in viz


@pytest.mark.unit
class TestGetStageDependencies:
    """Tests for get_stage_dependencies."""

    def test_no_deps(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [{"name": "build"}, {"name": "test"}]
        deps = mgr.get_stage_dependencies(stages)
        assert deps == {"build": [], "test": []}

    def test_with_deps(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "build", "dependencies": []},
            {"name": "test", "dependencies": ["build"]},
        ]
        deps = mgr.get_stage_dependencies(stages)
        assert deps["test"] == ["build"]

    def test_empty_list(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        deps = mgr.get_stage_dependencies([])
        assert deps == {}


@pytest.mark.unit
class TestValidateStageDependencies:
    """Tests for validate_stage_dependencies."""

    def test_valid_linear(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "build", "dependencies": []},
            {"name": "test", "dependencies": ["build"]},
            {"name": "deploy", "dependencies": ["test"]},
        ]
        is_valid, errors = mgr.validate_stage_dependencies(stages)
        assert is_valid is True
        assert errors == []

    def test_missing_dependency(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "test", "dependencies": ["build"]},
        ]
        is_valid, errors = mgr.validate_stage_dependencies(stages)
        assert is_valid is False
        assert any("missing" in e.lower() for e in errors)

    def test_self_dependency(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "build", "dependencies": ["build"]},
        ]
        is_valid, errors = mgr.validate_stage_dependencies(stages)
        assert is_valid is False
        assert any("itself" in e.lower() for e in errors)

    def test_cycle_detection(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "a", "dependencies": ["b"]},
            {"name": "b", "dependencies": ["a"]},
        ]
        is_valid, errors = mgr.validate_stage_dependencies(stages)
        assert is_valid is False
        assert any("cycle" in e.lower() for e in errors)

    def test_no_deps_valid(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [{"name": "a"}, {"name": "b"}]
        is_valid, errors = mgr.validate_stage_dependencies(stages)
        assert is_valid is True


@pytest.mark.unit
class TestOptimizePipelineSchedule:
    """Tests for optimize_pipeline_schedule and _calculate_execution_levels."""

    def test_all_independent(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        s1 = PipelineStage(name="a", jobs=[])
        s2 = PipelineStage(name="b", jobs=[])
        s3 = PipelineStage(name="c", jobs=[])
        pipeline = Pipeline(name="test", stages=[s1, s2, s3])
        opt = mgr.optimize_pipeline_schedule(pipeline)
        assert opt["parallel_stages"] == 3
        assert opt["sequential_chains"] == 0
        assert opt["estimated_parallelism"] == 3
        assert len(opt["execution_levels"]) == 1

    def test_linear_chain(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        s1 = PipelineStage(name="a", jobs=[])
        s2 = PipelineStage(name="b", dependencies=["a"], jobs=[])
        s3 = PipelineStage(name="c", dependencies=["b"], jobs=[])
        pipeline = Pipeline(name="test", stages=[s1, s2, s3])
        opt = mgr.optimize_pipeline_schedule(pipeline)
        assert opt["parallel_stages"] == 1
        assert opt["sequential_chains"] == 2
        assert len(opt["execution_levels"]) == 3

    def test_diamond(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        s1 = PipelineStage(name="start", jobs=[])
        s2 = PipelineStage(name="left", dependencies=["start"], jobs=[])
        s3 = PipelineStage(name="right", dependencies=["start"], jobs=[])
        s4 = PipelineStage(name="end", dependencies=["left", "right"], jobs=[])
        pipeline = Pipeline(name="test", stages=[s1, s2, s3, s4])
        opt = mgr.optimize_pipeline_schedule(pipeline)
        levels = opt["execution_levels"]
        assert len(levels) == 3
        assert levels[0] == ["start"]
        assert sorted(levels[1]) == ["left", "right"]
        assert levels[2] == ["end"]

    def test_optimization_suggestions(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        s1 = PipelineStage(name="a", jobs=[])
        s2 = PipelineStage(name="b", jobs=[])
        pipeline = Pipeline(name="test", stages=[s1, s2])
        opt = mgr.optimize_pipeline_schedule(pipeline)
        assert len(opt["optimization_suggestions"]) > 0

    def test_empty_pipeline_optimization(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = Pipeline(name="empty")
        opt = mgr.optimize_pipeline_schedule(pipeline)
        assert opt["parallel_stages"] == 0
        assert opt["estimated_parallelism"] == 0
        assert opt["execution_levels"] == []


@pytest.mark.unit
class TestSavePipelineConfig:
    """Tests for save_pipeline_config (JSON and YAML round-trip)."""

    def test_save_json(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr._parse_pipeline_config(_multi_stage_config())
        out_path = str(tmp_path / "out.json")
        mgr.save_pipeline_config(pipeline, out_path)
        with open(out_path) as f:
            saved = json.load(f)
        assert saved["name"] == "multi_stage"
        assert len(saved["stages"]) == 3
        assert saved["stages"][0]["jobs"][0]["name"] == "compile"

    def test_save_yaml(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr._parse_pipeline_config(_minimal_config())
        out_path = str(tmp_path / "out.yaml")
        mgr.save_pipeline_config(pipeline, out_path)
        with open(out_path) as f:
            saved = yaml.safe_load(f)
        assert saved["name"] == "test_pipeline"

    def test_save_yml_extension(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr._parse_pipeline_config(_minimal_config())
        out_path = str(tmp_path / "out.yml")
        mgr.save_pipeline_config(pipeline, out_path)
        with open(out_path) as f:
            saved = yaml.safe_load(f)
        assert saved["name"] == "test_pipeline"

    def test_round_trip_json(self, tmp_path):
        """Save then reload produces equivalent pipeline."""
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        original_config = _multi_stage_config()
        pipeline = mgr._parse_pipeline_config(original_config)
        out_path = str(tmp_path / "roundtrip.json")
        mgr.save_pipeline_config(pipeline, out_path)
        reloaded = mgr.create_pipeline(out_path)
        assert reloaded.name == pipeline.name
        assert len(reloaded.stages) == len(pipeline.stages)
        for orig, loaded in zip(pipeline.stages, reloaded.stages):
            assert orig.name == loaded.name
            assert len(orig.jobs) == len(loaded.jobs)

    def test_round_trip_yaml(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        pipeline = mgr._parse_pipeline_config(_multi_stage_config())
        out_path = str(tmp_path / "roundtrip.yaml")
        mgr.save_pipeline_config(pipeline, out_path)
        reloaded = mgr.create_pipeline(out_path)
        assert reloaded.name == pipeline.name
        assert len(reloaded.stages) == len(pipeline.stages)


@pytest.mark.unit
class TestParallelPipelineExecution:
    """Tests for parallel_pipeline_execution.

    NOTE: parallel_pipeline_execution has a known bug where
    concurrent.futures.wait(futures, ...) receives the futures dict itself
    instead of futures.values(). This causes AttributeError on Python 3.13+
    when stages have dependencies (the dict iterates over string keys).
    Tests that trigger this code path are marked xfail.
    """

    @pytest.mark.xfail(
        reason="Known bug: concurrent.futures.wait receives dict instead of dict.values()",
        strict=False,
    )
    def test_single_stage_completes(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "build", "jobs": [{"name": "compile"}]},
        ]
        result = mgr.parallel_pipeline_execution(stages)
        assert result["total_stages"] == 1
        assert result["completed_stages"] == 1
        assert result["failed_stages"] == 0
        assert "build" in result["stage_results"]
        assert result["stage_results"]["build"]["status"] == "completed"

    @pytest.mark.xfail(
        reason="Known bug: concurrent.futures.wait receives dict instead of dict.values()",
        strict=False,
    )
    def test_independent_stages_parallel(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "a", "jobs": [{"name": "j1"}]},
            {"name": "b", "jobs": [{"name": "j2"}]},
        ]
        result = mgr.parallel_pipeline_execution(stages)
        assert result["total_stages"] == 2
        assert result["completed_stages"] == 2

    @pytest.mark.xfail(
        reason="Known bug: concurrent.futures.wait receives dict instead of dict.values()",
        strict=False,
    )
    def test_dependent_stages(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stages = [
            {"name": "build", "dependencies": [], "jobs": [{"name": "j1"}]},
            {"name": "test", "dependencies": ["build"], "jobs": [{"name": "j2"}]},
        ]
        result = mgr.parallel_pipeline_execution(stages)
        assert result["completed_stages"] == 2

    @pytest.mark.xfail(
        reason="Known bug: min(0, 4) = 0, invalid max_workers for ThreadPoolExecutor",
        strict=False,
    )
    def test_empty_stages(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        result = mgr.parallel_pipeline_execution([])
        assert result["total_stages"] == 0
        assert result["completed_stages"] == 0


@pytest.mark.unit
class TestExecuteStageParallel:
    """Tests for _execute_stage_parallel."""

    def test_basic_execution(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "build", "jobs": [{"name": "j1"}, {"name": "j2"}]}
        result = mgr._execute_stage_parallel(stage)
        assert result["stage_name"] == "build"
        assert result["status"] == "completed"
        assert result["job_count"] == 2
        assert len(result["jobs"]) == 2

    def test_no_jobs(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        stage = {"name": "empty"}
        result = mgr._execute_stage_parallel(stage)
        assert result["status"] == "completed"
        assert result["job_count"] == 0


@pytest.mark.unit
class TestRunPipelineSync:
    """Tests for run_pipeline (synchronous) and run_pipeline_async."""

    def test_run_unknown_pipeline_raises(self, tmp_path):
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        with pytest.raises(ValueError, match="not found"):
            mgr.run_pipeline("nonexistent")

    def test_run_pipeline_with_echo(self, tmp_path):
        """Run a real pipeline with echo commands."""
        config = {
            "name": "echo_test",
            "stages": [
                {
                    "name": "greet",
                    "parallel": False,
                    "jobs": [
                        {
                            "name": "say_hello",
                            "commands": ["echo hello_world"],
                        }
                    ],
                }
            ],
        }
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.run_pipeline("echo_test")
        assert result.status == PipelineStatus.SUCCESS
        assert result.started_at is not None
        assert result.finished_at is not None
        assert result.duration >= 0
        assert result.stages[0].status == StageStatus.SUCCESS
        assert result.stages[0].jobs[0].status == JobStatus.SUCCESS
        assert "hello_world" in result.stages[0].jobs[0].output

    def test_run_pipeline_with_variables(self, tmp_path):
        """Variable substitution works end-to-end."""
        config = {
            "name": "var_test",
            "variables": {"GREETING": "default"},
            "stages": [
                {
                    "name": "greet",
                    "parallel": False,
                    "jobs": [
                        {
                            "name": "say",
                            "commands": ["echo ${GREETING}"],
                        }
                    ],
                }
            ],
        }
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.run_pipeline("var_test", variables={"GREETING": "overridden"})
        assert result.status == PipelineStatus.SUCCESS
        assert "overridden" in result.stages[0].jobs[0].output

    def test_run_pipeline_failing_command(self, tmp_path):
        """Pipeline with a failing command results in FAILURE status."""
        config = {
            "name": "fail_test",
            "stages": [
                {
                    "name": "fail_stage",
                    "parallel": False,
                    "jobs": [
                        {
                            "name": "bad_job",
                            "commands": ["exit 1"],
                        }
                    ],
                }
            ],
        }
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.run_pipeline("fail_test")
        assert result.status == PipelineStatus.FAILURE

    def test_run_pipeline_allow_failure(self, tmp_path):
        """Job with allow_failure=True does not fail the pipeline."""
        config = {
            "name": "allow_fail",
            "stages": [
                {
                    "name": "s1",
                    "allow_failure": True,
                    "parallel": False,
                    "jobs": [
                        {
                            "name": "j1",
                            "commands": ["exit 1"],
                            "allow_failure": True,
                        }
                    ],
                }
            ],
        }
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.run_pipeline("allow_fail")
        assert result.status == PipelineStatus.SUCCESS

    def test_run_pipeline_skips_unsatisfied_deps(self, tmp_path):
        """Stage with unsatisfied dependencies is skipped."""
        config = {
            "name": "skip_test",
            "stages": [
                {
                    "name": "depends_on_missing",
                    "dependencies": ["nonexistent_stage"],
                    "jobs": [
                        {
                            "name": "j1",
                            "commands": ["echo should_not_run"],
                        }
                    ],
                }
            ],
        }
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.run_pipeline("skip_test")
        assert result.stages[0].status == StageStatus.SKIPPED

    def test_run_pipeline_multi_stage_sequential(self, tmp_path):
        """Multi-stage pipeline with sequential jobs executes correctly."""
        config = {
            "name": "multi",
            "stages": [
                {
                    "name": "first",
                    "parallel": False,
                    "jobs": [{"name": "j1", "commands": ["echo stage1"]}],
                },
                {
                    "name": "second",
                    "dependencies": ["first"],
                    "parallel": False,
                    "jobs": [{"name": "j2", "commands": ["echo stage2"]}],
                },
            ],
        }
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.run_pipeline("multi")
        assert result.status == PipelineStatus.SUCCESS
        assert result.stages[0].status == StageStatus.SUCCESS
        assert result.stages[1].status == StageStatus.SUCCESS

    def test_run_pipeline_parallel_jobs(self, tmp_path):
        """Pipeline with parallel jobs in a stage."""
        config = {
            "name": "par_test",
            "stages": [
                {
                    "name": "parallel_stage",
                    "parallel": True,
                    "jobs": [
                        {"name": "j1", "commands": ["echo a"]},
                        {"name": "j2", "commands": ["echo b"]},
                        {"name": "j3", "commands": ["echo c"]},
                    ],
                }
            ],
        }
        path = _write_config(tmp_path, config)
        mgr = PipelineManager(workspace_dir=str(tmp_path / "ws"))
        mgr.create_pipeline(path)
        result = mgr.run_pipeline("par_test")
        assert result.status == PipelineStatus.SUCCESS
        for job in result.stages[0].jobs:
            assert job.status == JobStatus.SUCCESS
