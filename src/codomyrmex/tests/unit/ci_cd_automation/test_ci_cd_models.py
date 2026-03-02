"""Unit tests for CI/CD pipeline data model classes: PipelineJob, PipelineStage, and Pipeline."""

from datetime import datetime, timezone

from codomyrmex.ci_cd_automation.pipeline import (
    AsyncPipelineResult,
    JobStatus,
    Pipeline,
    PipelineJob,
    PipelineStage,
    PipelineStatus,
    StageStatus,
)


class TestPipelineJob:
    """Test cases for PipelineJob dataclass."""

    def test_pipeline_job_creation(self):
        """Test PipelineJob creation."""
        job = PipelineJob(
            name="test_job",
            commands=["echo 'hello'", "echo 'world'"],
            environment={"TEST_VAR": "test_value"},
            timeout=300
        )

        assert job.name == "test_job"
        assert len(job.commands) == 2
        assert job.environment["TEST_VAR"] == "test_value"
        assert job.timeout == 300
        assert job.status == JobStatus.PENDING

    def test_pipeline_job_defaults(self):
        """Test PipelineJob default values."""
        job = PipelineJob(name="test", commands=["echo test"])

        assert job.environment == {}
        assert job.artifacts == []
        assert job.dependencies == []
        assert job.timeout == 3600  # 1 hour
        assert job.retry_count == 0
        assert job.allow_failure is False
        assert job.status == JobStatus.PENDING

    def test_pipeline_job_to_dict(self):
        """Test PipelineJob to_dict conversion."""
        job = PipelineJob(
            name="test_job",
            commands=["echo test"],
            status=JobStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )

        job_dict = job.to_dict()

        assert job_dict["name"] == "test_job"
        assert job_dict["commands"] == ["echo test"]
        assert job_dict["status"] == "running"
        assert "start_time" in job_dict


class TestPipelineStage:
    """Test cases for PipelineStage dataclass."""

    def test_pipeline_stage_creation(self):
        """Test PipelineStage creation."""
        job = PipelineJob(name="job1", commands=["echo test"])
        stage = PipelineStage(
            name="test_stage",
            jobs=[job],
            dependencies=["previous_stage"],
            parallel=False
        )

        assert stage.name == "test_stage"
        assert len(stage.jobs) == 1
        assert stage.dependencies == ["previous_stage"]
        assert stage.parallel is False
        assert stage.status == StageStatus.PENDING

    def test_pipeline_stage_to_dict(self):
        """Test PipelineStage to_dict conversion."""
        stage = PipelineStage(
            name="test_stage",
            status=StageStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )

        stage_dict = stage.to_dict()

        assert stage_dict["name"] == "test_stage"
        assert stage_dict["status"] == "running"
        assert "start_time" in stage_dict
        assert "jobs" in stage_dict


class TestPipeline:
    """Test cases for Pipeline dataclass."""

    def test_pipeline_creation(self):
        """Test Pipeline creation."""
        stage = PipelineStage(name="stage1", jobs=[])
        pipeline = Pipeline(
            name="test_pipeline",
            description="Test pipeline",
            stages=[stage],
            timeout=1800
        )

        assert pipeline.name == "test_pipeline"
        assert pipeline.description == "Test pipeline"
        assert len(pipeline.stages) == 1
        assert pipeline.timeout == 1800
        assert pipeline.status == PipelineStatus.PENDING

    def test_pipeline_auto_timestamp(self):
        """Test Pipeline automatic timestamp creation."""
        pipeline = Pipeline(name="test", stages=[])

        assert pipeline.created_at is not None
        assert isinstance(pipeline.created_at, datetime)

    def test_pipeline_to_dict(self):
        """Test Pipeline to_dict conversion."""
        pipeline = Pipeline(
            name="test_pipeline",
            stages=[],
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )

        pipeline_dict = pipeline.to_dict()

        assert pipeline_dict["name"] == "test_pipeline"
        assert pipeline_dict["status"] == "running"
        assert "started_at" in pipeline_dict
        assert "stages" in pipeline_dict


class TestAsyncPipelineResult:
    """Test cases for AsyncPipelineResult dataclass."""

    def test_async_pipeline_result_creation(self):
        """Test creating AsyncPipelineResult."""
        result = AsyncPipelineResult(
            pipeline_id="test_123",
            status=PipelineStatus.SUCCESS,
            message="Pipeline completed successfully",
            data={"run_id": 456}
        )

        assert result.pipeline_id == "test_123"
        assert result.status == PipelineStatus.SUCCESS
        assert result.data["run_id"] == 456

    def test_async_pipeline_result_to_dict(self):
        """Test AsyncPipelineResult to_dict conversion."""
        result = AsyncPipelineResult(
            pipeline_id="test_123",
            status=PipelineStatus.FAILURE,
            message="Pipeline failed",
            error="Connection timeout"
        )

        result_dict = result.to_dict()

        assert result_dict["pipeline_id"] == "test_123"
        assert result_dict["status"] == "failure"
        assert result_dict["error"] == "Connection timeout"
        assert "timestamp" in result_dict


# From test_coverage_boost_r4.py
class TestDeploymentEnvironment:
    """Tests for Environment dataclass."""

    def test_environment_creation(self):
        from codomyrmex.ci_cd_automation.deployment_orchestrator import (
            Environment,
            EnvironmentType,
        )

        env = Environment(name="dev", type=EnvironmentType.DEVELOPMENT, host="localhost")
        assert env.name == "dev"
        assert env.type == EnvironmentType.DEVELOPMENT

    def test_environment_to_dict(self):
        from codomyrmex.ci_cd_automation.deployment_orchestrator import (
            Environment,
            EnvironmentType,
        )

        env = Environment(
            name="staging", type=EnvironmentType.STAGING,
            host="staging.example.com", port=22,
        )
        d = env.to_dict()
        assert d["name"] == "staging"
        assert d["host"] == "staging.example.com"


# From test_coverage_boost_r5.py
class TestPipelineModels:
    """Tests for pipeline data models."""

    def test_pipeline_job(self):
        from codomyrmex.ci_cd_automation.pipeline.models import JobStatus, PipelineJob

        job = PipelineJob(name="lint", commands=["flake8 ."])
        assert job.name == "lint"
        assert job.status == JobStatus.PENDING
        d = job.to_dict()
        assert d["name"] == "lint"
        assert d["status"] == "pending"

    def test_pipeline_stage(self):
        from codomyrmex.ci_cd_automation.pipeline.models import (
            PipelineJob,
            PipelineStage,
            StageStatus,
        )

        stage = PipelineStage(
            name="test",
            jobs=[PipelineJob(name="unit", commands=["pytest"])],
        )
        assert stage.status == StageStatus.PENDING
        d = stage.to_dict()
        assert len(d["jobs"]) == 1

    def test_pipeline(self):
        from codomyrmex.ci_cd_automation.pipeline.models import (
            Pipeline,
            PipelineJob,
            PipelineStage,
            PipelineStatus,
        )

        pipeline = Pipeline(
            name="ci",
            description="CI pipeline",
            stages=[
                PipelineStage(name="build", jobs=[
                    PipelineJob(name="compile", commands=["make build"]),
                ]),
                PipelineStage(name="test", jobs=[
                    PipelineJob(name="unit", commands=["pytest"]),
                ], dependencies=["build"]),
            ],
        )
        assert pipeline.status == PipelineStatus.PENDING
        d = pipeline.to_dict()
        assert d["name"] == "ci"
        assert len(d["stages"]) == 2
