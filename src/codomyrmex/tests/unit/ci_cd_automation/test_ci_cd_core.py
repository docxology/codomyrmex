"""Comprehensive unit tests for ci_cd_automation core data models, config logic,
and validation — covering ground NOT in test_ci_cd_automation.py or
test_pipeline_manager.py.

Focuses on:
- Deployment / Environment dataclass modeling and serialization
- DeploymentStatus / EnvironmentType enum completeness
- RollbackStrategy / RollbackPlan / RollbackExecution dataclasses
- AsyncPipelineResult edge cases
- Exception hierarchy with context metadata
- Dependency scan models (Vulnerability, ScanReport)
- Pipeline stage dependency resolution edge cases
- Rollout strategy config validation (canary, blue-green, rolling)
- PipelineMonitor multi-step metrics flow
- Pipeline config round-trip with deeply nested structures

Zero-mock policy: all tests use real objects and tmp_path for filesystem.
"""

import json
import os
import time
from datetime import datetime, timezone

import pytest
import yaml

from codomyrmex.ci_cd_automation.deployment_orchestrator import (
    Deployment,
    DeploymentStatus,
    Environment,
    EnvironmentType,
)
from codomyrmex.ci_cd_automation.exceptions import (
    ArtifactError,
    BuildError,
    DeploymentError,
    PipelineError,
    RollbackError,
    StageError,
)
from codomyrmex.ci_cd_automation.pipeline.models import (
    JobStatus,
    Pipeline,
    PipelineJob,
    PipelineStage,
    PipelineStatus,
    StageStatus,
)
from codomyrmex.ci_cd_automation.pipeline.async_manager import (
    AsyncPipelineResult,
)
from codomyrmex.ci_cd_automation.pipeline.manager import PipelineManager
from codomyrmex.ci_cd_automation.pipeline.pipeline_monitor import (
    PipelineMetrics,
    PipelineMonitor,
    PipelineReport,
    ReportType,
    generate_pipeline_reports,
    monitor_pipeline_health,
)
from codomyrmex.ci_cd_automation.rollback_manager import (
    RollbackExecution,
    RollbackManager,
    RollbackPlan,
    RollbackStep,
    RollbackStrategy,
)
from codomyrmex.ci_cd_automation.dependency_scan import (
    ScanReport,
    Vulnerability,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_environment(**overrides) -> Environment:
    """Build an Environment with sensible defaults, overridden by kwargs."""
    defaults = dict(
        name="staging",
        type=EnvironmentType.STAGING,
        host="staging.example.com",
        port=22,
        user="deploy",
    )
    defaults.update(overrides)
    return Environment(**defaults)


def _make_deployment(env: Environment | None = None, **overrides) -> Deployment:
    """Build a Deployment with sensible defaults."""
    if env is None:
        env = _make_environment()
    defaults = dict(
        name="app-v2",
        version="2.0.0",
        environment=env,
        artifacts=["build/app.tar.gz"],
        strategy="rolling",
    )
    defaults.update(overrides)
    return Deployment(**defaults)


# ===========================================================================
# 1. DeploymentStatus / EnvironmentType enum completeness
# ===========================================================================

class TestDeploymentStatusEnum:
    """Verify every deployment status value is accessible and round-trips."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "member,expected_value",
        [
            ("PENDING", "pending"),
            ("RUNNING", "running"),
            ("SUCCESS", "success"),
            ("FAILURE", "failure"),
            ("ROLLED_BACK", "rolled_back"),
            ("CANCELLED", "cancelled"),
        ],
    )
    def test_deployment_status_values(self, member, expected_value):
        status = DeploymentStatus[member]
        assert status.value == expected_value
        assert DeploymentStatus(expected_value) is status

    @pytest.mark.unit
    def test_deployment_status_member_count(self):
        assert len(DeploymentStatus) == 6


class TestEnvironmentTypeEnum:
    """Verify every environment type value is accessible and round-trips."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "member,expected_value",
        [
            ("DEVELOPMENT", "development"),
            ("STAGING", "staging"),
            ("PRODUCTION", "production"),
            ("TESTING", "testing"),
        ],
    )
    def test_environment_type_values(self, member, expected_value):
        et = EnvironmentType[member]
        assert et.value == expected_value
        assert EnvironmentType(expected_value) is et

    @pytest.mark.unit
    def test_environment_type_member_count(self):
        assert len(EnvironmentType) == 4


# ===========================================================================
# 2. Environment dataclass modelling
# ===========================================================================

class TestEnvironmentDataclass:
    """Tests for the Environment dataclass beyond basic creation."""

    @pytest.mark.unit
    def test_environment_with_all_optional_fields(self):
        env = Environment(
            name="prod",
            type=EnvironmentType.PRODUCTION,
            host="prod.example.com",
            port=2222,
            user="root",
            key_path="/home/deploy/.ssh/id_rsa",
            docker_registry="registry.example.com",
            kubernetes_context="prod-cluster",
            variables={"APP_ENV": "production"},
            pre_deploy_hooks=["echo pre"],
            post_deploy_hooks=["echo post"],
            health_checks=[{"type": "http", "endpoint": "http://localhost/health"}],
        )
        d = env.to_dict()
        assert d["name"] == "prod"
        assert d["type"] == "production"
        assert d["port"] == 2222
        assert d["key_path"] == "/home/deploy/.ssh/id_rsa"
        assert d["docker_registry"] == "registry.example.com"
        assert d["kubernetes_context"] == "prod-cluster"
        assert d["variables"]["APP_ENV"] == "production"
        assert len(d["pre_deploy_hooks"]) == 1
        assert len(d["post_deploy_hooks"]) == 1
        assert len(d["health_checks"]) == 1

    @pytest.mark.unit
    def test_environment_defaults(self):
        env = Environment(
            name="dev",
            type=EnvironmentType.DEVELOPMENT,
            host="localhost",
        )
        assert env.port == 22
        assert env.user == "deploy"
        assert env.key_path is None
        assert env.docker_registry is None
        assert env.kubernetes_context is None
        assert env.variables == {}
        assert env.pre_deploy_hooks == []
        assert env.post_deploy_hooks == []
        assert env.health_checks == []


# ===========================================================================
# 3. Deployment dataclass modelling and serialization
# ===========================================================================

class TestDeploymentDataclass:
    """Tests for Deployment dataclass creation and to_dict round-trip."""

    @pytest.mark.unit
    def test_deployment_auto_created_at(self):
        dep = _make_deployment()
        assert dep.created_at is not None
        assert isinstance(dep.created_at, datetime)

    @pytest.mark.unit
    def test_deployment_to_dict_contains_all_keys(self):
        dep = _make_deployment()
        d = dep.to_dict()
        expected_keys = {
            "name", "version", "environment", "artifacts", "strategy",
            "timeout", "rollback_on_failure", "status", "created_at",
            "started_at", "finished_at", "duration", "logs", "metrics",
        }
        assert expected_keys == set(d.keys())

    @pytest.mark.unit
    def test_deployment_to_dict_nested_environment(self):
        env = _make_environment(name="prod", type=EnvironmentType.PRODUCTION, host="prod.example.com")
        dep = _make_deployment(env=env)
        d = dep.to_dict()
        assert d["environment"]["name"] == "prod"
        assert d["environment"]["type"] == "production"

    @pytest.mark.unit
    @pytest.mark.parametrize("strategy", ["rolling", "blue_green", "canary"])
    def test_deployment_strategy_stored(self, strategy):
        dep = _make_deployment(strategy=strategy)
        assert dep.strategy == strategy
        assert dep.to_dict()["strategy"] == strategy

    @pytest.mark.unit
    def test_deployment_rollback_on_failure_default_true(self):
        dep = _make_deployment()
        assert dep.rollback_on_failure is True

    @pytest.mark.unit
    def test_deployment_rollback_on_failure_false(self):
        dep = _make_deployment(rollback_on_failure=False)
        assert dep.rollback_on_failure is False
        assert dep.to_dict()["rollback_on_failure"] is False


# ===========================================================================
# 4. Rollback dataclass and enum modelling
# ===========================================================================

class TestRollbackStrategyEnum:
    """Ensure all rollback strategy variants are accessible."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "member,expected_value",
        [
            ("IMMEDIATE", "immediate"),
            ("ROLLING", "rolling"),
            ("BLUE_GREEN", "blue_green"),
            ("CANARY", "canary"),
            ("MANUAL", "manual"),
        ],
    )
    def test_rollback_strategy_values(self, member, expected_value):
        rs = RollbackStrategy[member]
        assert rs.value == expected_value

    @pytest.mark.unit
    def test_rollback_strategy_member_count(self):
        assert len(RollbackStrategy) == 5


class TestRollbackPlanDataclass:
    """Tests for the RollbackPlan dataclass."""

    @pytest.mark.unit
    def test_rollback_plan_creation(self):
        step = RollbackStep(
            name="stop_services",
            description="Stop all services",
            action=lambda: None,
            timeout=60,
        )
        plan = RollbackPlan(
            deployment_id="deploy-123",
            strategy=RollbackStrategy.IMMEDIATE,
            steps=[step],
            created_at=datetime.now(),
            reason="Health check failed",
            estimated_duration=60,
            risk_level="high",
        )
        assert plan.deployment_id == "deploy-123"
        assert plan.strategy == RollbackStrategy.IMMEDIATE
        assert len(plan.steps) == 1
        assert plan.risk_level == "high"
        assert plan.estimated_duration == 60

    @pytest.mark.unit
    def test_rollback_plan_default_risk_level(self):
        plan = RollbackPlan(
            deployment_id="deploy-456",
            strategy=RollbackStrategy.ROLLING,
            steps=[],
            created_at=datetime.now(),
            reason="Test",
            estimated_duration=0,
        )
        assert plan.risk_level == "medium"


class TestRollbackExecutionDataclass:
    """Tests for the RollbackExecution dataclass."""

    @pytest.mark.unit
    def test_rollback_execution_defaults(self):
        exe = RollbackExecution(
            execution_id="rb-001",
            deployment_id="deploy-789",
            strategy=RollbackStrategy.CANARY,
            status="running",
            start_time=datetime.now(),
        )
        assert exe.end_time is None
        assert exe.current_step == 0
        assert exe.completed_steps == 0
        assert exe.failed_steps == 0
        assert exe.errors == []
        assert exe.warnings == []

    @pytest.mark.unit
    def test_rollback_execution_tracks_errors(self):
        exe = RollbackExecution(
            execution_id="rb-002",
            deployment_id="deploy-aaa",
            strategy=RollbackStrategy.IMMEDIATE,
            status="failed",
            start_time=datetime.now(),
            errors=["Step A timed out", "Step B failed"],
            failed_steps=2,
        )
        assert len(exe.errors) == 2
        assert exe.failed_steps == 2


# ===========================================================================
# 5. RollbackManager — plan creation and strategy-specific default steps
# ===========================================================================

class TestRollbackManagerPlanCreation:
    """Test RollbackManager.create_rollback_plan default step generation."""

    @pytest.mark.unit
    def test_immediate_strategy_default_steps(self, tmp_path):
        mgr = RollbackManager(workspace_dir=str(tmp_path))
        plan = mgr.create_rollback_plan(
            deployment_id="dep-imm",
            strategy=RollbackStrategy.IMMEDIATE,
            reason="Smoke test failed",
        )
        step_names = [s.name for s in plan.steps]
        assert "stop_services" in step_names
        assert "restore_backup" in step_names
        assert "restart_services" in step_names

    @pytest.mark.unit
    def test_rolling_strategy_default_steps(self, tmp_path):
        mgr = RollbackManager(workspace_dir=str(tmp_path))
        plan = mgr.create_rollback_plan(
            deployment_id="dep-roll",
            strategy=RollbackStrategy.ROLLING,
            reason="Increased error rate",
        )
        step_names = [s.name for s in plan.steps]
        assert "identify_healthy_instances" in step_names
        assert "rollback_instances" in step_names
        assert "validate_rollback" in step_names

    @pytest.mark.unit
    def test_canary_strategy_uses_generic_steps(self, tmp_path):
        mgr = RollbackManager(workspace_dir=str(tmp_path))
        plan = mgr.create_rollback_plan(
            deployment_id="dep-canary",
            strategy=RollbackStrategy.CANARY,
            reason="Canary failure",
        )
        step_names = [s.name for s in plan.steps]
        assert "prepare_rollback" in step_names
        assert "execute_rollback" in step_names
        assert "validate_rollback" in step_names

    @pytest.mark.unit
    def test_estimated_duration_is_sum_of_timeouts(self, tmp_path):
        mgr = RollbackManager(workspace_dir=str(tmp_path))
        plan = mgr.create_rollback_plan(
            deployment_id="dep-dur",
            strategy=RollbackStrategy.IMMEDIATE,
            reason="Test duration calc",
        )
        expected = sum(s.timeout for s in plan.steps)
        assert plan.estimated_duration == expected

    @pytest.mark.unit
    def test_plan_persisted_to_disk(self, tmp_path):
        mgr = RollbackManager(workspace_dir=str(tmp_path))
        mgr.create_rollback_plan(
            deployment_id="dep-persist",
            strategy=RollbackStrategy.ROLLING,
            reason="Persistence test",
        )
        plan_files = list((tmp_path / "rollback_plans").glob("plan_dep-persist_*.json"))
        assert len(plan_files) == 1
        data = json.loads(plan_files[0].read_text())
        assert data["deployment_id"] == "dep-persist"
        assert data["strategy"] == "rolling"


# ===========================================================================
# 6. AsyncPipelineResult edge cases
# ===========================================================================

class TestAsyncPipelineResultEdgeCases:
    """Edge cases for AsyncPipelineResult serialization."""

    @pytest.mark.unit
    def test_result_with_none_data_and_error(self):
        result = AsyncPipelineResult(
            pipeline_id="p-1",
            status=PipelineStatus.PENDING,
            message="Queued",
            data=None,
            error=None,
        )
        d = result.to_dict()
        assert d["data"] is None
        assert d["error"] is None

    @pytest.mark.unit
    def test_result_with_error_and_data(self):
        result = AsyncPipelineResult(
            pipeline_id="p-2",
            status=PipelineStatus.FAILURE,
            message="Partial failure",
            data={"partial": True},
            error="Stage 3 timed out",
        )
        d = result.to_dict()
        assert d["data"]["partial"] is True
        assert "timed out" in d["error"]

    @pytest.mark.unit
    def test_result_timestamp_is_utc_iso(self):
        result = AsyncPipelineResult(
            pipeline_id="p-3",
            status=PipelineStatus.SUCCESS,
            message="Done",
        )
        d = result.to_dict()
        # The timestamp field should be an ISO-format string
        ts = d["timestamp"]
        assert isinstance(ts, str)
        assert "T" in ts  # ISO 8601 marker


# ===========================================================================
# 7. Exception hierarchy with context metadata
# ===========================================================================

class TestExceptionHierarchy:
    """Test CI/CD exception classes carry context metadata."""

    @pytest.mark.unit
    def test_pipeline_error_context(self):
        err = PipelineError(
            "Build stage failed",
            pipeline_name="main-ci",
            stage="build",
        )
        assert "main-ci" in str(err) or err.context["pipeline_name"] == "main-ci"
        assert err.context["stage"] == "build"

    @pytest.mark.unit
    def test_build_error_context(self):
        err = BuildError(
            "Compilation failed",
            build_id="b-123",
            build_target="src/app",
            exit_code=2,
        )
        assert err.context["build_id"] == "b-123"
        assert err.context["build_target"] == "src/app"
        assert err.context["exit_code"] == 2

    @pytest.mark.unit
    def test_deployment_error_context(self):
        err = DeploymentError(
            "Deploy timed out",
            deployment_id="d-456",
            environment="production",
            target_version="3.0.0",
        )
        assert err.context["deployment_id"] == "d-456"
        assert err.context["environment"] == "production"
        assert err.context["target_version"] == "3.0.0"

    @pytest.mark.unit
    def test_artifact_error_context(self):
        err = ArtifactError(
            "Upload failed",
            artifact_name="app.tar.gz",
            artifact_version="1.2.3",
            registry="gcr.io/myproject",
        )
        assert err.context["artifact_name"] == "app.tar.gz"
        assert err.context["registry"] == "gcr.io/myproject"

    @pytest.mark.unit
    def test_stage_error_context(self):
        err = StageError(
            "Job failed in test stage",
            stage_name="test",
            job_name="integration_tests",
        )
        assert err.context["stage_name"] == "test"
        assert err.context["job_name"] == "integration_tests"

    @pytest.mark.unit
    def test_rollback_error_context(self):
        err = RollbackError(
            "Rollback failed",
            from_version="2.0.0",
            to_version="1.9.0",
        )
        assert err.context["from_version"] == "2.0.0"
        assert err.context["to_version"] == "1.9.0"


# ===========================================================================
# 8. Dependency scan models (Vulnerability, ScanReport)
# ===========================================================================

class TestVulnerabilityDataclass:
    """Test the Vulnerability dataclass."""

    @pytest.mark.unit
    def test_vulnerability_creation(self):
        vuln = Vulnerability(
            package="requests",
            version="2.25.0",
            cve_id="CVE-2023-32681",
            severity="high",
            summary="SSRF vulnerability",
            fixed_in="2.31.0",
        )
        assert vuln.package == "requests"
        assert vuln.severity == "high"

    @pytest.mark.unit
    def test_vulnerability_to_dict(self):
        vuln = Vulnerability(package="flask", version="1.0", cve_id="CVE-XXXX", severity="medium")
        d = vuln.to_dict()
        assert d["package"] == "flask"
        assert d["severity"] == "medium"
        assert d["fixed_in"] == ""  # default

    @pytest.mark.unit
    def test_vulnerability_defaults(self):
        vuln = Vulnerability(package="numpy")
        assert vuln.version == ""
        assert vuln.cve_id == ""
        assert vuln.severity == "unknown"
        assert vuln.summary == ""
        assert vuln.fixed_in == ""


class TestScanReport:
    """Test the ScanReport dataclass."""

    @pytest.mark.unit
    def test_clean_report(self):
        report = ScanReport(packages_scanned=15)
        assert report.is_clean is True
        assert report.has_critical is False

    @pytest.mark.unit
    def test_report_with_critical_vulnerability(self):
        vuln = Vulnerability(package="openssl", severity="critical")
        report = ScanReport(
            packages_scanned=20,
            vulnerabilities=[vuln],
        )
        assert report.is_clean is False
        assert report.has_critical is True

    @pytest.mark.unit
    def test_report_count_by_severity(self):
        vulns = [
            Vulnerability(package="a", severity="high"),
            Vulnerability(package="b", severity="high"),
            Vulnerability(package="c", severity="low"),
        ]
        report = ScanReport(packages_scanned=10, vulnerabilities=vulns)
        counts = report.count_by_severity
        assert counts["high"] == 2
        assert counts["low"] == 1


# ===========================================================================
# 9. PipelineMonitor multi-step metrics flow
# ===========================================================================

class TestPipelineMonitorMetricsFlow:
    """Test the full start -> record -> finish monitoring lifecycle."""

    @pytest.mark.unit
    def test_full_monitoring_lifecycle(self, tmp_path):
        monitor = PipelineMonitor(workspace_dir=str(tmp_path))
        exec_id = monitor.start_monitoring("ci-main")

        monitor.record_stage_completion(exec_id, "build", success=True)
        monitor.record_stage_completion(exec_id, "test", success=True)
        monitor.record_stage_completion(exec_id, "deploy", success=False)

        monitor.record_job_completion(exec_id, "compile", success=True)
        monitor.record_job_completion(exec_id, "lint", success=True)
        monitor.record_job_completion(exec_id, "unit_tests", success=True)
        monitor.record_job_completion(exec_id, "integration", success=False)

        metrics = monitor.finish_monitoring(exec_id)

        assert metrics.pipeline_name == "ci-main"
        assert metrics.stage_count == 3
        assert metrics.job_count == 4
        assert metrics.error_count == 2  # 1 failed stage + 1 failed job
        assert metrics.success_rate == 50.0  # 2 out of 4 jobs succeeded

    @pytest.mark.unit
    def test_record_to_nonexistent_execution_is_noop(self, tmp_path):
        monitor = PipelineMonitor(workspace_dir=str(tmp_path))
        # Should not raise, just log a warning
        monitor.record_stage_completion("nonexistent-id", "build", success=True)
        monitor.record_job_completion("nonexistent-id", "lint", success=True)

    @pytest.mark.unit
    def test_finish_nonexistent_execution_raises(self, tmp_path):
        monitor = PipelineMonitor(workspace_dir=str(tmp_path))
        with pytest.raises(Exception):
            monitor.finish_monitoring("nonexistent-id")

    @pytest.mark.unit
    def test_generate_pipeline_reports_convenience(self, tmp_path):
        reports = generate_pipeline_reports(
            execution_id="exec-999",
            report_types=[ReportType.EXECUTION, ReportType.PERFORMANCE],
            workspace_dir=str(tmp_path),
        )
        assert "execution" in reports
        assert "performance" in reports
        assert isinstance(reports["execution"], PipelineReport)

    @pytest.mark.unit
    def test_monitor_pipeline_health_convenience(self, tmp_path):
        health = monitor_pipeline_health("main-ci", workspace_dir=str(tmp_path))
        assert health["pipeline_name"] == "main-ci"
        assert "status" in health

    @pytest.mark.unit
    def test_metrics_summary(self, tmp_path):
        monitor = PipelineMonitor(workspace_dir=str(tmp_path))
        summary = monitor.get_metrics_summary(days=30)
        assert summary["period_days"] == 30
        assert "total_executions" in summary
        assert "trending_metrics" in summary


# ===========================================================================
# 10. Pipeline config round-trip with deeply nested structures
# ===========================================================================

class TestPipelineConfigRoundTrip:
    """Test save/load round-trip with complex nested pipeline configs."""

    @pytest.mark.unit
    def test_round_trip_complex_pipeline_json(self, tmp_path):
        """Build a pipeline object, save to JSON, reload, and verify."""
        mgr = PipelineManager(workspace_dir=str(tmp_path))

        # Build a complex pipeline programmatically
        pipeline = Pipeline(
            name="complex-ci",
            description="Multi-stage with env vars and artifacts",
            variables={"VERSION": "4.0.0", "REGION": "us-east-1"},
            triggers={"push": True},
            timeout=5400,
        )
        job1 = PipelineJob(
            name="compile",
            commands=["make build"],
            environment={"CC": "gcc"},
            artifacts=["build/*.o"],
            timeout=600,
            retry_count=2,
        )
        job2 = PipelineJob(
            name="lint",
            commands=["make lint"],
            allow_failure=True,
        )
        stage_build = PipelineStage(
            name="build",
            jobs=[job1, job2],
            environment={"BUILD_MODE": "release"},
            parallel=True,
        )
        stage_test = PipelineStage(
            name="test",
            jobs=[PipelineJob(name="unit", commands=["make test"])],
            dependencies=["build"],
            parallel=False,
        )
        pipeline.stages = [stage_build, stage_test]

        # Save
        out_path = str(tmp_path / "pipeline.json")
        mgr.save_pipeline_config(pipeline, out_path)

        # Reload
        loaded = mgr.create_pipeline(out_path)

        assert loaded.name == "complex-ci"
        assert loaded.description == "Multi-stage with env vars and artifacts"
        assert loaded.variables["VERSION"] == "4.0.0"
        assert loaded.timeout == 5400
        assert len(loaded.stages) == 2
        assert loaded.stages[0].name == "build"
        assert len(loaded.stages[0].jobs) == 2
        assert loaded.stages[0].jobs[0].retry_count == 2
        assert loaded.stages[0].jobs[1].allow_failure is True
        assert loaded.stages[1].dependencies == ["build"]

    @pytest.mark.unit
    def test_round_trip_complex_pipeline_yaml(self, tmp_path):
        """Build a pipeline, save to YAML, reload, verify."""
        mgr = PipelineManager(workspace_dir=str(tmp_path))

        pipeline = Pipeline(
            name="yaml-pipeline",
            description="YAML round-trip test",
            variables={"DEPLOY_TARGET": "k8s"},
        )
        stage = PipelineStage(
            name="deploy",
            jobs=[
                PipelineJob(
                    name="push-image",
                    commands=["docker push app:latest"],
                    environment={"REGISTRY": "gcr.io"},
                    artifacts=["image-digest.txt"],
                ),
            ],
            allow_failure=True,
        )
        pipeline.stages = [stage]

        out_path = str(tmp_path / "pipeline.yaml")
        mgr.save_pipeline_config(pipeline, out_path)

        loaded = mgr.create_pipeline(out_path)
        assert loaded.name == "yaml-pipeline"
        assert loaded.stages[0].allow_failure is True
        assert loaded.stages[0].jobs[0].environment["REGISTRY"] == "gcr.io"

    @pytest.mark.unit
    def test_pipeline_config_validation_rejects_non_string_name(self):
        mgr = PipelineManager()
        valid, errors = mgr.validate_pipeline_config({"name": 123, "stages": []})
        assert valid is False
        assert any("name must be a string" in e for e in errors)

    @pytest.mark.unit
    def test_pipeline_config_validation_rejects_negative_timeout(self):
        mgr = PipelineManager()
        valid, errors = mgr.validate_pipeline_config({
            "name": "t",
            "stages": [],
            "timeout": -10,
        })
        assert valid is False
        assert any("Timeout" in e for e in errors)

    @pytest.mark.unit
    @pytest.mark.parametrize("bad_trigger", ["cron", "webhook", "merge_request"])
    def test_pipeline_config_validation_rejects_invalid_triggers(self, bad_trigger):
        mgr = PipelineManager()
        valid, errors = mgr.validate_pipeline_config({
            "name": "t",
            "stages": [],
            "triggers": [bad_trigger],
        })
        assert valid is False
        assert any("Invalid trigger" in e for e in errors)


# ===========================================================================
# 11. Pipeline model status enum completeness
# ===========================================================================

class TestPipelineStatusEnums:
    """Ensure all pipeline/stage/job status enums are consistent."""

    @pytest.mark.unit
    @pytest.mark.parametrize("enum_cls", [PipelineStatus, StageStatus, JobStatus])
    def test_status_enums_have_six_members(self, enum_cls):
        assert len(enum_cls) == 6

    @pytest.mark.unit
    @pytest.mark.parametrize("enum_cls", [PipelineStatus, StageStatus, JobStatus])
    def test_status_enums_share_same_values(self, enum_cls):
        expected = {"pending", "running", "success", "failure", "cancelled", "skipped"}
        actual = {member.value for member in enum_cls}
        assert actual == expected

    @pytest.mark.unit
    def test_report_type_enum_values(self):
        expected = {"execution", "performance", "quality", "compliance", "summary"}
        actual = {member.value for member in ReportType}
        assert actual == expected
