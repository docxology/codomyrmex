"""Unit tests for the Codomyrmex schemas module.

Comprehensive tests for all 27 exports across the three submodules:
core (8 exports), code (8 exports), infra (11 exports).
Covers enum values, dataclass construction, to_dict() serialization,
computed properties, and Config get/set methods.
"""

import pytest

from codomyrmex.validation.schemas import (
    # Core types
    Result,
    ResultStatus,
    Task,
    TaskStatus,
    Config,
    ModuleInfo,
    ToolDefinition,
    Notification,
    # Code types
    CodeEntity,
    CodeEntityType,
    AnalysisResult,
    AnalysisSeverity,
    SecurityFinding,
    SecuritySeverity,
    TestResult as SchemaTestResult,
    TestStatus as SchemaTestStatus,
    # Infrastructure types
    Deployment,
    DeploymentStatus,
    Pipeline,
    PipelineStatus,
    Resource,
    BuildArtifact,
    Metric,
    MetricType,
    Credential,
    Permission,
    WorkflowStep,
)


# ---------------------------------------------------------------------------
# Module-level import tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSchemasModuleImport:
    """Tests for schemas module importability and __all__ completeness."""

    def test_schemas_module_import(self):
        """Test that schemas module can be imported."""
        from codomyrmex.database_management import schemas

        assert schemas is not None

    def test_schemas_version(self):
        """Test that schemas module exposes a version string."""
        from codomyrmex.database_management import schemas

        assert hasattr(schemas, "__version__")
        assert schemas.__version__ == "0.1.0"

    def test_all_27_exports_importable(self):
        """Every name listed in __all__ should be importable from the package."""
        from codomyrmex.database_management import schemas

        expected = [
            "Result", "ResultStatus", "Task", "TaskStatus",
            "Config", "ModuleInfo", "ToolDefinition", "Notification",
            "CodeEntity", "CodeEntityType", "AnalysisResult", "AnalysisSeverity",
            "SecurityFinding", "SecuritySeverity", "TestResult", "TestStatus",
            "Deployment", "DeploymentStatus", "Pipeline", "PipelineStatus",
            "Resource", "BuildArtifact", "Metric", "MetricType",
            "Credential", "Permission", "WorkflowStep",
        ]
        for name in expected:
            assert hasattr(schemas, name), f"{name} missing from schemas package"

    def test_all_list_length(self):
        """The __all__ list should contain exactly 27 names."""
        from codomyrmex.database_management import schemas

        assert len(schemas.__all__) == 27


# ---------------------------------------------------------------------------
# core.py — Enum tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestResultStatusEnum:
    """Tests for ResultStatus enum values."""

    def test_values(self):
        assert ResultStatus.SUCCESS.value == "success"
        assert ResultStatus.FAILURE.value == "failure"
        assert ResultStatus.PARTIAL.value == "partial"
        assert ResultStatus.SKIPPED.value == "skipped"
        assert ResultStatus.TIMEOUT.value == "timeout"

    def test_member_count(self):
        assert len(ResultStatus) == 5


@pytest.mark.unit
class TestTaskStatusEnum:
    """Tests for TaskStatus enum values."""

    def test_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_member_count(self):
        assert len(TaskStatus) == 5


# ---------------------------------------------------------------------------
# core.py — Dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestResult:
    """Tests for the Result dataclass."""

    def test_construction_with_defaults(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.status == ResultStatus.SUCCESS
        assert r.data is None
        assert r.message == ""
        assert r.errors == []
        assert r.metadata == {}
        assert r.duration_ms is None

    def test_construction_with_all_fields(self):
        r = Result(
            status=ResultStatus.FAILURE,
            data={"key": "val"},
            message="it broke",
            errors=["err1", "err2"],
            metadata={"attempt": 3},
            duration_ms=42.5,
        )
        assert r.status == ResultStatus.FAILURE
        assert r.data == {"key": "val"}
        assert r.message == "it broke"
        assert r.errors == ["err1", "err2"]
        assert r.metadata == {"attempt": 3}
        assert r.duration_ms == 42.5

    def test_ok_property_true_for_success(self):
        r = Result(status=ResultStatus.SUCCESS)
        assert r.ok is True

    def test_ok_property_false_for_failure(self):
        r = Result(status=ResultStatus.FAILURE)
        assert r.ok is False

    def test_ok_property_false_for_partial(self):
        r = Result(status=ResultStatus.PARTIAL)
        assert r.ok is False

    def test_ok_property_false_for_timeout(self):
        r = Result(status=ResultStatus.TIMEOUT)
        assert r.ok is False

    def test_to_dict(self):
        r = Result(
            status=ResultStatus.SUCCESS,
            data="hello",
            message="done",
            errors=[],
            metadata={"k": 1},
            duration_ms=10.0,
        )
        d = r.to_dict()
        assert d["status"] == "success"
        assert d["data"] == "hello"
        assert d["message"] == "done"
        assert d["errors"] == []
        assert d["metadata"] == {"k": 1}
        assert d["duration_ms"] == 10.0

    def test_to_dict_returns_plain_dict(self):
        r = Result(status=ResultStatus.SUCCESS)
        d = r.to_dict()
        assert isinstance(d, dict)


@pytest.mark.unit
class TestTask:
    """Tests for the Task dataclass."""

    def test_construction_with_defaults(self):
        t = Task(id="t1", name="build")
        assert t.id == "t1"
        assert t.name == "build"
        assert t.status == TaskStatus.PENDING
        assert t.description == ""
        assert t.module == ""
        assert t.input_data == {}
        assert t.output_data == {}
        assert t.dependencies == []
        assert t.metadata == {}

    def test_construction_with_all_fields(self):
        t = Task(
            id="t2",
            name="deploy",
            status=TaskStatus.COMPLETED,
            description="Deploy v2",
            module="deployment",
            input_data={"version": "2.0"},
            output_data={"url": "https://app.example.com"},
            dependencies=["t1"],
            metadata={"env": "prod"},
        )
        assert t.status == TaskStatus.COMPLETED
        assert t.dependencies == ["t1"]

    def test_to_dict(self):
        t = Task(id="t1", name="build", status=TaskStatus.IN_PROGRESS)
        d = t.to_dict()
        assert d["id"] == "t1"
        assert d["name"] == "build"
        assert d["status"] == "in_progress"


@pytest.mark.unit
class TestConfig:
    """Tests for the Config dataclass including get/set methods."""

    def test_construction_with_defaults(self):
        c = Config(name="myconf")
        assert c.name == "myconf"
        assert c.values == {}
        assert c.version == "1.0.0"
        assert c.module == ""

    def test_get_returns_value(self):
        c = Config(name="c", values={"debug": True})
        assert c.get("debug") is True

    def test_get_returns_default_for_missing_key(self):
        c = Config(name="c")
        assert c.get("missing", 42) == 42

    def test_get_returns_none_for_missing_key_no_default(self):
        c = Config(name="c")
        assert c.get("missing") is None

    def test_set_adds_new_key(self):
        c = Config(name="c")
        c.set("port", 8080)
        assert c.get("port") == 8080

    def test_set_overwrites_existing_key(self):
        c = Config(name="c", values={"port": 80})
        c.set("port", 443)
        assert c.get("port") == 443


@pytest.mark.unit
class TestModuleInfo:
    """Tests for ModuleInfo dataclass."""

    def test_construction_with_defaults(self):
        m = ModuleInfo(name="schemas")
        assert m.name == "schemas"
        assert m.version == "0.1.0"
        assert m.layer == ""
        assert m.description == ""
        assert m.dependencies == []
        assert m.has_cli is False
        assert m.has_mcp is False
        assert m.has_events is False

    def test_construction_with_all_fields(self):
        m = ModuleInfo(
            name="logging_monitoring",
            version="0.2.0",
            layer="foundation",
            description="Centralized logging",
            dependencies=[],
            has_cli=True,
            has_mcp=False,
            has_events=True,
        )
        assert m.layer == "foundation"
        assert m.has_cli is True
        assert m.has_events is True


@pytest.mark.unit
class TestToolDefinition:
    """Tests for ToolDefinition dataclass."""

    def test_construction_with_defaults(self):
        td = ToolDefinition(name="analyze", description="Run analysis", module="static_analysis")
        assert td.name == "analyze"
        assert td.description == "Run analysis"
        assert td.module == "static_analysis"
        assert td.input_schema == {}
        assert td.output_schema == {}
        assert td.tags == []


@pytest.mark.unit
class TestNotification:
    """Tests for Notification dataclass."""

    def test_construction_with_defaults(self):
        n = Notification(title="Alert", message="Something happened")
        assert n.title == "Alert"
        assert n.message == "Something happened"
        assert n.level == "info"
        assert n.source == ""
        assert n.metadata == {}


# ---------------------------------------------------------------------------
# code.py — Enum tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCodeEntityTypeEnum:
    """Tests for CodeEntityType enum."""

    def test_values(self):
        assert CodeEntityType.FILE.value == "file"
        assert CodeEntityType.CLASS.value == "class"
        assert CodeEntityType.FUNCTION.value == "function"
        assert CodeEntityType.METHOD.value == "method"
        assert CodeEntityType.VARIABLE.value == "variable"
        assert CodeEntityType.MODULE.value == "module"
        assert CodeEntityType.PACKAGE.value == "package"
        assert CodeEntityType.IMPORT.value == "import"

    def test_member_count(self):
        assert len(CodeEntityType) == 8


@pytest.mark.unit
class TestAnalysisSeverityEnum:
    """Tests for AnalysisSeverity enum."""

    def test_values(self):
        assert AnalysisSeverity.INFO.value == "info"
        assert AnalysisSeverity.LOW.value == "low"
        assert AnalysisSeverity.MEDIUM.value == "medium"
        assert AnalysisSeverity.HIGH.value == "high"
        assert AnalysisSeverity.CRITICAL.value == "critical"

    def test_member_count(self):
        assert len(AnalysisSeverity) == 5


@pytest.mark.unit
class TestSecuritySeverityEnum:
    """Tests for SecuritySeverity enum."""

    def test_values(self):
        assert SecuritySeverity.LOW.value == "low"
        assert SecuritySeverity.MEDIUM.value == "medium"
        assert SecuritySeverity.HIGH.value == "high"
        assert SecuritySeverity.CRITICAL.value == "critical"

    def test_member_count(self):
        assert len(SecuritySeverity) == 4


@pytest.mark.unit
class TestSchemaTestStatusEnum:
    """Tests for TestStatus enum."""

    def test_values(self):
        assert SchemaTestStatus.PASSED.value == "passed"
        assert SchemaTestStatus.FAILED.value == "failed"
        assert SchemaTestStatus.SKIPPED.value == "skipped"
        assert SchemaTestStatus.ERROR.value == "error"
        assert SchemaTestStatus.XFAIL.value == "xfail"

    def test_member_count(self):
        assert len(SchemaTestStatus) == 5


# ---------------------------------------------------------------------------
# code.py — Dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCodeEntity:
    """Tests for CodeEntity dataclass."""

    def test_construction_with_defaults(self):
        ce = CodeEntity(name="main", entity_type=CodeEntityType.FUNCTION)
        assert ce.name == "main"
        assert ce.entity_type == CodeEntityType.FUNCTION
        assert ce.file_path == ""
        assert ce.line_start == 0
        assert ce.line_end == 0
        assert ce.language == "python"
        assert ce.content == ""
        assert ce.metadata == {}

    def test_to_dict(self):
        ce = CodeEntity(
            name="MyClass",
            entity_type=CodeEntityType.CLASS,
            file_path="src/models.py",
            line_start=10,
            line_end=50,
        )
        d = ce.to_dict()
        assert d["name"] == "MyClass"
        assert d["entity_type"] == "class"
        assert d["file_path"] == "src/models.py"
        assert d["line_start"] == 10
        assert d["line_end"] == 50
        assert d["language"] == "python"


@pytest.mark.unit
class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_construction_with_defaults(self):
        ar = AnalysisResult(analyzer="ruff", target="src/")
        assert ar.analyzer == "ruff"
        assert ar.target == "src/"
        assert ar.severity == AnalysisSeverity.INFO
        assert ar.message == ""

    def test_to_dict(self):
        ar = AnalysisResult(
            analyzer="mypy",
            target="core.py",
            severity=AnalysisSeverity.HIGH,
            message="Type error",
            file_path="core.py",
            line=42,
            column=5,
            rule_id="E501",
            suggestion="Fix the type annotation",
        )
        d = ar.to_dict()
        assert d["analyzer"] == "mypy"
        assert d["severity"] == "high"
        assert d["line"] == 42
        assert d["rule_id"] == "E501"


@pytest.mark.unit
class TestSecurityFinding:
    """Tests for SecurityFinding dataclass."""

    def test_construction_with_defaults(self):
        sf = SecurityFinding(title="SQL Injection", severity=SecuritySeverity.CRITICAL)
        assert sf.title == "SQL Injection"
        assert sf.severity == SecuritySeverity.CRITICAL
        assert sf.description == ""
        assert sf.cwe_id == ""

    def test_to_dict(self):
        sf = SecurityFinding(
            title="XSS",
            severity=SecuritySeverity.HIGH,
            description="Cross-site scripting",
            file_path="templates/index.html",
            line=15,
            cwe_id="CWE-79",
            owasp_category="A7",
            remediation="Sanitize user input",
        )
        d = sf.to_dict()
        assert d["title"] == "XSS"
        assert d["severity"] == "high"
        assert d["cwe_id"] == "CWE-79"
        assert d["owasp_category"] == "A7"


@pytest.mark.unit
class TestSchemaTestResult:
    """Tests for TestResult dataclass."""

    def test_construction_with_defaults(self):
        tr = SchemaTestResult(test_name="test_login", status=SchemaTestStatus.PASSED)
        assert tr.test_name == "test_login"
        assert tr.status == SchemaTestStatus.PASSED
        assert tr.duration_ms == 0.0
        assert tr.module == ""
        assert tr.stdout == ""
        assert tr.stderr == ""

    def test_to_dict(self):
        tr = SchemaTestResult(
            test_name="test_auth",
            status=SchemaTestStatus.FAILED,
            duration_ms=120.5,
            module="auth",
            message="AssertionError",
        )
        d = tr.to_dict()
        assert d["test_name"] == "test_auth"
        assert d["status"] == "failed"
        assert d["duration_ms"] == 120.5
        assert d["module"] == "auth"


# ---------------------------------------------------------------------------
# infra.py — Enum tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDeploymentStatusEnum:
    """Tests for DeploymentStatus enum."""

    def test_values(self):
        assert DeploymentStatus.PENDING.value == "pending"
        assert DeploymentStatus.IN_PROGRESS.value == "in_progress"
        assert DeploymentStatus.DEPLOYED.value == "deployed"
        assert DeploymentStatus.FAILED.value == "failed"
        assert DeploymentStatus.ROLLING_BACK.value == "rolling_back"
        assert DeploymentStatus.ROLLED_BACK.value == "rolled_back"

    def test_member_count(self):
        assert len(DeploymentStatus) == 6


@pytest.mark.unit
class TestPipelineStatusEnum:
    """Tests for PipelineStatus enum."""

    def test_values(self):
        assert PipelineStatus.QUEUED.value == "queued"
        assert PipelineStatus.RUNNING.value == "running"
        assert PipelineStatus.SUCCEEDED.value == "succeeded"
        assert PipelineStatus.FAILED.value == "failed"
        assert PipelineStatus.CANCELLED.value == "cancelled"

    def test_member_count(self):
        assert len(PipelineStatus) == 5


@pytest.mark.unit
class TestMetricTypeEnum:
    """Tests for MetricType enum."""

    def test_values(self):
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.SUMMARY.value == "summary"

    def test_member_count(self):
        assert len(MetricType) == 4


# ---------------------------------------------------------------------------
# infra.py — Dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDeployment:
    """Tests for Deployment dataclass."""

    def test_construction_with_defaults(self):
        dep = Deployment(id="d1", name="prod-deploy")
        assert dep.id == "d1"
        assert dep.name == "prod-deploy"
        assert dep.status == DeploymentStatus.PENDING
        assert dep.target == ""
        assert dep.version == ""
        assert dep.environment == ""
        assert dep.artifacts == []
        assert dep.metadata == {}

    def test_to_dict(self):
        dep = Deployment(
            id="d2",
            name="staging",
            status=DeploymentStatus.DEPLOYED,
            target="k8s-cluster",
            version="1.0.0",
            environment="staging",
            artifacts=["app.tar.gz"],
        )
        d = dep.to_dict()
        assert d["id"] == "d2"
        assert d["status"] == "deployed"
        assert d["artifacts"] == ["app.tar.gz"]


@pytest.mark.unit
class TestPipeline:
    """Tests for Pipeline dataclass."""

    def test_construction_with_defaults(self):
        p = Pipeline(id="p1", name="ci-main")
        assert p.id == "p1"
        assert p.status == PipelineStatus.QUEUED
        assert p.stages == []
        assert p.current_stage == ""

    def test_to_dict(self):
        p = Pipeline(
            id="p2",
            name="deploy-pipe",
            status=PipelineStatus.RUNNING,
            stages=["build", "test", "deploy"],
            current_stage="test",
        )
        d = p.to_dict()
        assert d["status"] == "running"
        assert d["stages"] == ["build", "test", "deploy"]
        assert d["current_stage"] == "test"


@pytest.mark.unit
class TestResource:
    """Tests for Resource dataclass."""

    def test_construction_with_defaults(self):
        r = Resource(id="r1", name="web-server")
        assert r.status == "active"
        assert r.resource_type == ""
        assert r.provider == ""
        assert r.properties == {}

    def test_to_dict(self):
        r = Resource(
            id="r2",
            name="db-instance",
            resource_type="rds",
            provider="aws",
            status="provisioning",
            properties={"engine": "postgres"},
        )
        d = r.to_dict()
        assert d["resource_type"] == "rds"
        assert d["provider"] == "aws"
        assert d["status"] == "provisioning"


@pytest.mark.unit
class TestBuildArtifact:
    """Tests for BuildArtifact dataclass."""

    def test_construction_with_defaults(self):
        ba = BuildArtifact(name="app.whl", path="/dist/app.whl")
        assert ba.name == "app.whl"
        assert ba.path == "/dist/app.whl"
        assert ba.artifact_type == ""
        assert ba.size_bytes == 0
        assert ba.checksum == ""

    def test_to_dict(self):
        ba = BuildArtifact(
            name="image.tar",
            path="/builds/image.tar",
            artifact_type="docker_image",
            size_bytes=52428800,
            checksum="sha256:abc123",
        )
        d = ba.to_dict()
        assert d["artifact_type"] == "docker_image"
        assert d["size_bytes"] == 52428800
        assert d["checksum"] == "sha256:abc123"


@pytest.mark.unit
class TestMetric:
    """Tests for Metric dataclass."""

    def test_construction_with_defaults(self):
        m = Metric(name="cpu_usage", value=72.5)
        assert m.name == "cpu_usage"
        assert m.value == 72.5
        assert m.metric_type == MetricType.GAUGE
        assert m.labels == {}
        assert m.unit == ""

    def test_to_dict(self):
        m = Metric(
            name="request_count",
            value=1500,
            metric_type=MetricType.COUNTER,
            labels={"endpoint": "/api/v1"},
            unit="requests",
        )
        d = m.to_dict()
        assert d["metric_type"] == "counter"
        assert d["labels"] == {"endpoint": "/api/v1"}
        assert d["unit"] == "requests"


@pytest.mark.unit
class TestCredential:
    """Tests for Credential dataclass."""

    def test_construction_with_defaults(self):
        c = Credential(id="c1", name="github-token")
        assert c.id == "c1"
        assert c.name == "github-token"
        assert c.credential_type == ""
        assert c.provider == ""
        assert c.is_valid is True
        assert c.metadata == {}

    def test_construction_with_all_fields(self):
        c = Credential(
            id="c2",
            name="aws-key",
            credential_type="api_key",
            provider="aws",
            is_valid=False,
            metadata={"rotated": True},
        )
        assert c.credential_type == "api_key"
        assert c.is_valid is False


@pytest.mark.unit
class TestPermission:
    """Tests for Permission dataclass."""

    def test_construction_with_defaults(self):
        p = Permission(subject="user:admin", action="write", resource="repo:main")
        assert p.subject == "user:admin"
        assert p.action == "write"
        assert p.resource == "repo:main"
        assert p.effect == "allow"
        assert p.conditions == {}

    def test_construction_with_deny(self):
        p = Permission(
            subject="user:guest",
            action="delete",
            resource="repo:main",
            effect="deny",
            conditions={"ip_range": "10.0.0.0/8"},
        )
        assert p.effect == "deny"
        assert p.conditions == {"ip_range": "10.0.0.0/8"}


@pytest.mark.unit
class TestWorkflowStep:
    """Tests for WorkflowStep dataclass."""

    def test_construction_with_defaults(self):
        ws = WorkflowStep(id="s1", name="lint", action="run_linter")
        assert ws.id == "s1"
        assert ws.name == "lint"
        assert ws.action == "run_linter"
        assert ws.status == "pending"
        assert ws.input_data == {}
        assert ws.output_data == {}
        assert ws.dependencies == []

    def test_to_dict(self):
        ws = WorkflowStep(
            id="s2",
            name="deploy",
            action="deploy_to_prod",
            status="completed",
            input_data={"version": "2.0"},
            output_data={"url": "https://app.example.com"},
            dependencies=["s1"],
            metadata={"duration": 45},
        )
        d = ws.to_dict()
        assert d["id"] == "s2"
        assert d["action"] == "deploy_to_prod"
        assert d["status"] == "completed"
        assert d["dependencies"] == ["s1"]
