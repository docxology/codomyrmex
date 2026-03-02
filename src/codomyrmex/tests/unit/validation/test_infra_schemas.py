"""
Unit tests for validation.schemas.infra — Zero-Mock compliant.

Covers: DeploymentStatus (all 6 values), PipelineStatus (all 5 values),
MetricType (all 4 values), Deployment (defaults, to_dict), Pipeline (defaults,
to_dict), Resource (defaults, to_dict), BuildArtifact (defaults, to_dict),
Metric (defaults, to_dict), WorkflowStep (defaults, to_dict).
"""

import pytest

from codomyrmex.validation.schemas.infra import (
    BuildArtifact,
    Credential,
    Deployment,
    DeploymentStatus,
    Metric,
    MetricType,
    Permission,
    Pipeline,
    PipelineStatus,
    Resource,
    WorkflowStep,
)

# ── DeploymentStatus ───────────────────────────────────────────────────


@pytest.mark.unit
class TestDeploymentStatus:
    def test_pending_value(self):
        assert DeploymentStatus.PENDING.value == "pending"

    def test_in_progress_value(self):
        assert DeploymentStatus.IN_PROGRESS.value == "in_progress"

    def test_deployed_value(self):
        assert DeploymentStatus.DEPLOYED.value == "deployed"

    def test_failed_value(self):
        assert DeploymentStatus.FAILED.value == "failed"

    def test_rolling_back_value(self):
        assert DeploymentStatus.ROLLING_BACK.value == "rolling_back"

    def test_rolled_back_value(self):
        assert DeploymentStatus.ROLLED_BACK.value == "rolled_back"

    def test_six_members(self):
        assert len(DeploymentStatus) == 6


# ── PipelineStatus ────────────────────────────────────────────────────


@pytest.mark.unit
class TestPipelineStatus:
    def test_queued_value(self):
        assert PipelineStatus.QUEUED.value == "queued"

    def test_running_value(self):
        assert PipelineStatus.RUNNING.value == "running"

    def test_succeeded_value(self):
        assert PipelineStatus.SUCCEEDED.value == "succeeded"

    def test_failed_value(self):
        assert PipelineStatus.FAILED.value == "failed"

    def test_cancelled_value(self):
        assert PipelineStatus.CANCELLED.value == "cancelled"

    def test_five_members(self):
        assert len(PipelineStatus) == 5


# ── MetricType ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricType:
    def test_counter_value(self):
        assert MetricType.COUNTER.value == "counter"

    def test_gauge_value(self):
        assert MetricType.GAUGE.value == "gauge"

    def test_histogram_value(self):
        assert MetricType.HISTOGRAM.value == "histogram"

    def test_summary_value(self):
        assert MetricType.SUMMARY.value == "summary"

    def test_four_members(self):
        assert len(MetricType) == 4


# ── Deployment ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDeployment:
    def test_id_and_name_stored(self):
        d = Deployment(id="dep-1", name="prod deploy")
        assert d.id == "dep-1"
        assert d.name == "prod deploy"

    def test_status_default_pending(self):
        d = Deployment(id="d", name="n")
        assert d.status == DeploymentStatus.PENDING

    def test_target_default_empty(self):
        d = Deployment(id="d", name="n")
        assert d.target == ""

    def test_version_default_empty(self):
        d = Deployment(id="d", name="n")
        assert d.version == ""

    def test_artifacts_default_empty(self):
        d = Deployment(id="d", name="n")
        assert d.artifacts == []

    def test_to_dict_keys(self):
        d = Deployment(id="d", name="n")
        keys = d.to_dict().keys()
        for k in ("id", "name", "status", "target", "version",
                   "environment", "artifacts", "metadata"):
            assert k in keys

    def test_to_dict_status_is_string(self):
        d = Deployment(id="d", name="n", status=DeploymentStatus.DEPLOYED)
        assert d.to_dict()["status"] == "deployed"

    def test_to_dict_artifacts_populated(self):
        d = Deployment(id="d", name="n", artifacts=["app.tar.gz"])
        assert d.to_dict()["artifacts"] == ["app.tar.gz"]


# ── Pipeline (infra) ──────────────────────────────────────────────────


@pytest.mark.unit
class TestInfraPipeline:
    def test_id_and_name_stored(self):
        p = Pipeline(id="p1", name="CI")
        assert p.id == "p1"
        assert p.name == "CI"

    def test_status_default_queued(self):
        p = Pipeline(id="p1", name="CI")
        assert p.status == PipelineStatus.QUEUED

    def test_stages_default_empty(self):
        p = Pipeline(id="p1", name="CI")
        assert p.stages == []

    def test_current_stage_default_empty(self):
        p = Pipeline(id="p1", name="CI")
        assert p.current_stage == ""

    def test_to_dict_keys(self):
        p = Pipeline(id="p1", name="CI")
        for k in ("id", "name", "status", "stages", "current_stage", "metadata"):
            assert k in p.to_dict()

    def test_to_dict_status_is_string(self):
        p = Pipeline(id="p1", name="CI", status=PipelineStatus.SUCCEEDED)
        assert p.to_dict()["status"] == "succeeded"

    def test_to_dict_stages_list(self):
        p = Pipeline(id="p1", name="CI", stages=["build", "test"])
        assert p.to_dict()["stages"] == ["build", "test"]


# ── Resource ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestResource:
    def test_id_and_name_stored(self):
        r = Resource(id="r1", name="my-cluster")
        assert r.id == "r1"
        assert r.name == "my-cluster"

    def test_resource_type_default_empty(self):
        r = Resource(id="r1", name="n")
        assert r.resource_type == ""

    def test_status_default_active(self):
        r = Resource(id="r1", name="n")
        assert r.status == "active"

    def test_to_dict_keys(self):
        r = Resource(id="r1", name="n")
        for k in ("id", "name", "resource_type", "provider",
                   "status", "properties", "metadata"):
            assert k in r.to_dict()

    def test_to_dict_status_stored(self):
        r = Resource(id="r1", name="n", status="terminating")
        assert r.to_dict()["status"] == "terminating"


# ── BuildArtifact ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestBuildArtifact:
    def test_name_and_path_stored(self):
        a = BuildArtifact(name="app.tar.gz", path="/dist/app.tar.gz")
        assert a.name == "app.tar.gz"
        assert a.path == "/dist/app.tar.gz"

    def test_size_bytes_default_zero(self):
        a = BuildArtifact(name="x", path="/x")
        assert a.size_bytes == 0

    def test_checksum_default_empty(self):
        a = BuildArtifact(name="x", path="/x")
        assert a.checksum == ""

    def test_artifact_type_default_empty(self):
        a = BuildArtifact(name="x", path="/x")
        assert a.artifact_type == ""

    def test_to_dict_keys(self):
        a = BuildArtifact(name="x", path="/x")
        for k in ("name", "path", "artifact_type", "size_bytes", "checksum", "metadata"):
            assert k in a.to_dict()

    def test_to_dict_size_bytes(self):
        a = BuildArtifact(name="x", path="/x", size_bytes=1024)
        assert a.to_dict()["size_bytes"] == 1024


# ── Metric ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetric:
    def test_name_and_value_stored(self):
        m = Metric(name="cpu_usage", value=0.75)
        assert m.name == "cpu_usage"
        assert m.value == pytest.approx(0.75)

    def test_metric_type_default_gauge(self):
        m = Metric(name="cpu", value=0.5)
        assert m.metric_type == MetricType.GAUGE

    def test_unit_default_empty(self):
        m = Metric(name="cpu", value=0.5)
        assert m.unit == ""

    def test_labels_default_empty(self):
        m = Metric(name="cpu", value=0.5)
        assert m.labels == {}

    def test_to_dict_keys(self):
        m = Metric(name="cpu", value=0.5)
        for k in ("name", "value", "metric_type", "labels", "unit", "metadata"):
            assert k in m.to_dict()

    def test_to_dict_metric_type_is_string(self):
        m = Metric(name="requests", value=100, metric_type=MetricType.COUNTER)
        assert m.to_dict()["metric_type"] == "counter"

    def test_to_dict_value(self):
        m = Metric(name="latency", value=1.23)
        assert m.to_dict()["value"] == pytest.approx(1.23)


# ── WorkflowStep ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestWorkflowStep:
    def test_id_name_action_stored(self):
        ws = WorkflowStep(id="step-1", name="Build", action="build_code")
        assert ws.id == "step-1"
        assert ws.name == "Build"
        assert ws.action == "build_code"

    def test_status_default_pending(self):
        ws = WorkflowStep(id="s", name="n", action="a")
        assert ws.status == "pending"

    def test_dependencies_default_empty(self):
        ws = WorkflowStep(id="s", name="n", action="a")
        assert ws.dependencies == []

    def test_input_data_default_empty(self):
        ws = WorkflowStep(id="s", name="n", action="a")
        assert ws.input_data == {}

    def test_output_data_default_empty(self):
        ws = WorkflowStep(id="s", name="n", action="a")
        assert ws.output_data == {}

    def test_to_dict_keys(self):
        ws = WorkflowStep(id="s", name="n", action="a")
        for k in ("id", "name", "action", "status", "input_data",
                   "output_data", "dependencies", "metadata"):
            assert k in ws.to_dict()

    def test_to_dict_dependencies(self):
        ws = WorkflowStep(id="s", name="n", action="a", dependencies=["step-0"])
        assert ws.to_dict()["dependencies"] == ["step-0"]


# ── Credential ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCredential:
    def test_id_and_name_stored(self):
        c = Credential(id="cred-1", name="db-password")
        assert c.id == "cred-1"
        assert c.name == "db-password"

    def test_credential_type_default_empty(self):
        c = Credential(id="c", name="n")
        assert c.credential_type == ""

    def test_is_valid_default_true(self):
        c = Credential(id="c", name="n")
        assert c.is_valid is True


# ── Permission ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPermission:
    def test_subject_action_resource_stored(self):
        p = Permission(subject="user:alice", action="read", resource="reports/*")
        assert p.subject == "user:alice"
        assert p.action == "read"
        assert p.resource == "reports/*"

    def test_effect_default_allow(self):
        p = Permission(subject="u", action="a", resource="r")
        assert p.effect == "allow"

    def test_conditions_default_empty(self):
        p = Permission(subject="u", action="a", resource="r")
        assert p.conditions == {}
