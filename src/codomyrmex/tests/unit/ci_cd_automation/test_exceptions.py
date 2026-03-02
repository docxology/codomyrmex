"""Tests for CI/CD automation exception classes.

Validates instantiation, hierarchy, context population, message formatting,
and raise/catch behavior for all exception classes in
codomyrmex.ci_cd_automation.exceptions.
"""

import pytest

from codomyrmex.ci_cd_automation.exceptions import (
    ArtifactError,
    BuildError,
    DeploymentError,
    PipelineError,
    RollbackError,
    StageError,
)
from codomyrmex.exceptions import CICDError
from codomyrmex.exceptions.base import CodomyrmexError


# ---------------------------------------------------------------------------
# PipelineError
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestPipelineError:
    """Tests for PipelineError."""

    def test_inherits_from_cicd_error(self):
        assert issubclass(PipelineError, CICDError)

    def test_inherits_from_codomyrmex_error(self):
        assert issubclass(PipelineError, CodomyrmexError)

    def test_inherits_from_exception(self):
        assert issubclass(PipelineError, Exception)

    def test_instantiation_message_only(self):
        err = PipelineError("pipeline broke")
        assert err.message == "pipeline broke"
        assert "pipeline_name" not in err.context
        assert "stage" not in err.context

    def test_instantiation_with_pipeline_name(self):
        err = PipelineError("fail", pipeline_name="deploy-prod")
        assert err.context["pipeline_name"] == "deploy-prod"

    def test_instantiation_with_stage(self):
        err = PipelineError("fail", stage="lint")
        assert err.context["stage"] == "lint"

    def test_instantiation_with_all_params(self):
        err = PipelineError("fail", pipeline_name="ci", stage="test")
        assert err.context["pipeline_name"] == "ci"
        assert err.context["stage"] == "test"

    def test_none_pipeline_name_excluded(self):
        err = PipelineError("fail", pipeline_name=None)
        assert "pipeline_name" not in err.context

    def test_none_stage_excluded(self):
        err = PipelineError("fail", stage=None)
        assert "stage" not in err.context

    def test_raise_and_catch_as_pipeline_error(self):
        with pytest.raises(PipelineError):
            raise PipelineError("boom")

    def test_raise_and_catch_as_cicd_error(self):
        with pytest.raises(CICDError):
            raise PipelineError("boom")

    def test_str_representation(self):
        err = PipelineError("fail", pipeline_name="ci")
        s = str(err)
        assert "PipelineError" in s
        assert "fail" in s
        assert "pipeline_name=ci" in s

    def test_to_dict(self):
        err = PipelineError("fail", pipeline_name="ci")
        d = err.to_dict()
        assert d["error_type"] == "PipelineError"
        assert d["message"] == "fail"
        assert d["context"]["pipeline_name"] == "ci"

    def test_error_code_default(self):
        err = PipelineError("fail")
        assert err.error_code == "PipelineError"

    def test_kwargs_forwarded(self):
        err = PipelineError("fail", custom_key="custom_val")
        assert err.context["custom_key"] == "custom_val"


# ---------------------------------------------------------------------------
# BuildError
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestBuildError:
    """Tests for BuildError."""

    def test_inherits_from_cicd_error(self):
        assert issubclass(BuildError, CICDError)

    def test_instantiation_message_only(self):
        err = BuildError("compile failed")
        assert err.message == "compile failed"
        assert "build_id" not in err.context
        assert "build_target" not in err.context
        assert "exit_code" not in err.context

    def test_instantiation_with_build_id(self):
        err = BuildError("fail", build_id="b-123")
        assert err.context["build_id"] == "b-123"

    def test_instantiation_with_build_target(self):
        err = BuildError("fail", build_target="libfoo")
        assert err.context["build_target"] == "libfoo"

    def test_instantiation_with_exit_code(self):
        err = BuildError("fail", exit_code=137)
        assert err.context["exit_code"] == 137

    def test_exit_code_zero_is_included(self):
        err = BuildError("fail", exit_code=0)
        assert err.context["exit_code"] == 0

    def test_exit_code_none_excluded(self):
        err = BuildError("fail", exit_code=None)
        assert "exit_code" not in err.context

    def test_instantiation_with_all_params(self):
        err = BuildError("fail", build_id="b-1", build_target="app", exit_code=1)
        assert err.context["build_id"] == "b-1"
        assert err.context["build_target"] == "app"
        assert err.context["exit_code"] == 1

    def test_none_build_id_excluded(self):
        err = BuildError("fail", build_id=None)
        assert "build_id" not in err.context

    def test_none_build_target_excluded(self):
        err = BuildError("fail", build_target=None)
        assert "build_target" not in err.context

    def test_raise_and_catch(self):
        with pytest.raises(BuildError):
            raise BuildError("boom")

    def test_raise_catch_as_cicd(self):
        with pytest.raises(CICDError):
            raise BuildError("boom")

    def test_str_representation(self):
        err = BuildError("fail", build_id="b-1", exit_code=2)
        s = str(err)
        assert "BuildError" in s
        assert "fail" in s
        assert "build_id=b-1" in s
        assert "exit_code=2" in s

    def test_to_dict(self):
        err = BuildError("fail", build_target="app")
        d = err.to_dict()
        assert d["error_type"] == "BuildError"
        assert d["context"]["build_target"] == "app"

    def test_error_code_default(self):
        err = BuildError("fail")
        assert err.error_code == "BuildError"


# ---------------------------------------------------------------------------
# DeploymentError
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestDeploymentError:
    """Tests for DeploymentError."""

    def test_inherits_from_cicd_error(self):
        assert issubclass(DeploymentError, CICDError)

    def test_instantiation_message_only(self):
        err = DeploymentError("deploy failed")
        assert err.message == "deploy failed"
        assert "deployment_id" not in err.context
        assert "environment" not in err.context
        assert "target_version" not in err.context

    def test_instantiation_with_deployment_id(self):
        err = DeploymentError("fail", deployment_id="d-456")
        assert err.context["deployment_id"] == "d-456"

    def test_instantiation_with_environment(self):
        err = DeploymentError("fail", environment="production")
        assert err.context["environment"] == "production"

    def test_instantiation_with_target_version(self):
        err = DeploymentError("fail", target_version="2.1.0")
        assert err.context["target_version"] == "2.1.0"

    def test_instantiation_with_all_params(self):
        err = DeploymentError(
            "fail", deployment_id="d-1", environment="staging", target_version="1.0.0"
        )
        assert err.context["deployment_id"] == "d-1"
        assert err.context["environment"] == "staging"
        assert err.context["target_version"] == "1.0.0"

    def test_none_params_excluded(self):
        err = DeploymentError(
            "fail", deployment_id=None, environment=None, target_version=None
        )
        assert "deployment_id" not in err.context
        assert "environment" not in err.context
        assert "target_version" not in err.context

    def test_raise_and_catch(self):
        with pytest.raises(DeploymentError):
            raise DeploymentError("boom")

    def test_raise_catch_as_cicd(self):
        with pytest.raises(CICDError):
            raise DeploymentError("boom")

    def test_str_representation(self):
        err = DeploymentError("fail", environment="prod")
        s = str(err)
        assert "DeploymentError" in s
        assert "environment=prod" in s

    def test_to_dict(self):
        err = DeploymentError("fail", target_version="3.0")
        d = err.to_dict()
        assert d["error_type"] == "DeploymentError"
        assert d["context"]["target_version"] == "3.0"

    def test_error_code_default(self):
        err = DeploymentError("fail")
        assert err.error_code == "DeploymentError"


# ---------------------------------------------------------------------------
# ArtifactError
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestArtifactError:
    """Tests for ArtifactError."""

    def test_inherits_from_cicd_error(self):
        assert issubclass(ArtifactError, CICDError)

    def test_instantiation_message_only(self):
        err = ArtifactError("artifact missing")
        assert err.message == "artifact missing"
        assert "artifact_name" not in err.context
        assert "artifact_version" not in err.context
        assert "registry" not in err.context

    def test_instantiation_with_artifact_name(self):
        err = ArtifactError("fail", artifact_name="mylib")
        assert err.context["artifact_name"] == "mylib"

    def test_instantiation_with_artifact_version(self):
        err = ArtifactError("fail", artifact_version="1.2.3")
        assert err.context["artifact_version"] == "1.2.3"

    def test_instantiation_with_registry(self):
        err = ArtifactError("fail", registry="docker.io")
        assert err.context["registry"] == "docker.io"

    def test_instantiation_with_all_params(self):
        err = ArtifactError(
            "fail", artifact_name="pkg", artifact_version="0.1", registry="ghcr.io"
        )
        assert err.context["artifact_name"] == "pkg"
        assert err.context["artifact_version"] == "0.1"
        assert err.context["registry"] == "ghcr.io"

    def test_none_params_excluded(self):
        err = ArtifactError(
            "fail", artifact_name=None, artifact_version=None, registry=None
        )
        assert "artifact_name" not in err.context
        assert "artifact_version" not in err.context
        assert "registry" not in err.context

    def test_raise_and_catch(self):
        with pytest.raises(ArtifactError):
            raise ArtifactError("boom")

    def test_raise_catch_as_cicd(self):
        with pytest.raises(CICDError):
            raise ArtifactError("boom")

    def test_str_representation(self):
        err = ArtifactError("fail", artifact_name="pkg", registry="ecr")
        s = str(err)
        assert "ArtifactError" in s
        assert "artifact_name=pkg" in s
        assert "registry=ecr" in s

    def test_to_dict(self):
        err = ArtifactError("fail", artifact_name="lib")
        d = err.to_dict()
        assert d["error_type"] == "ArtifactError"
        assert d["context"]["artifact_name"] == "lib"

    def test_error_code_default(self):
        err = ArtifactError("fail")
        assert err.error_code == "ArtifactError"


# ---------------------------------------------------------------------------
# StageError
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestStageError:
    """Tests for StageError."""

    def test_inherits_from_cicd_error(self):
        assert issubclass(StageError, CICDError)

    def test_instantiation_message_only(self):
        err = StageError("stage failed")
        assert err.message == "stage failed"
        assert "stage_name" not in err.context
        assert "job_name" not in err.context

    def test_instantiation_with_stage_name(self):
        err = StageError("fail", stage_name="build")
        assert err.context["stage_name"] == "build"

    def test_instantiation_with_job_name(self):
        err = StageError("fail", job_name="compile-x86")
        assert err.context["job_name"] == "compile-x86"

    def test_instantiation_with_all_params(self):
        err = StageError("fail", stage_name="test", job_name="unit-tests")
        assert err.context["stage_name"] == "test"
        assert err.context["job_name"] == "unit-tests"

    def test_none_params_excluded(self):
        err = StageError("fail", stage_name=None, job_name=None)
        assert "stage_name" not in err.context
        assert "job_name" not in err.context

    def test_raise_and_catch(self):
        with pytest.raises(StageError):
            raise StageError("boom")

    def test_raise_catch_as_cicd(self):
        with pytest.raises(CICDError):
            raise StageError("boom")

    def test_str_representation(self):
        err = StageError("fail", stage_name="deploy")
        s = str(err)
        assert "StageError" in s
        assert "stage_name=deploy" in s

    def test_to_dict(self):
        err = StageError("fail", job_name="lint")
        d = err.to_dict()
        assert d["error_type"] == "StageError"
        assert d["context"]["job_name"] == "lint"

    def test_error_code_default(self):
        err = StageError("fail")
        assert err.error_code == "StageError"


# ---------------------------------------------------------------------------
# RollbackError
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestRollbackError:
    """Tests for RollbackError."""

    def test_inherits_from_cicd_error(self):
        assert issubclass(RollbackError, CICDError)

    def test_instantiation_message_only(self):
        err = RollbackError("rollback failed")
        assert err.message == "rollback failed"
        assert "from_version" not in err.context
        assert "to_version" not in err.context

    def test_instantiation_with_from_version(self):
        err = RollbackError("fail", from_version="2.0.0")
        assert err.context["from_version"] == "2.0.0"

    def test_instantiation_with_to_version(self):
        err = RollbackError("fail", to_version="1.9.0")
        assert err.context["to_version"] == "1.9.0"

    def test_instantiation_with_all_params(self):
        err = RollbackError("fail", from_version="2.0", to_version="1.0")
        assert err.context["from_version"] == "2.0"
        assert err.context["to_version"] == "1.0"

    def test_none_params_excluded(self):
        err = RollbackError("fail", from_version=None, to_version=None)
        assert "from_version" not in err.context
        assert "to_version" not in err.context

    def test_raise_and_catch(self):
        with pytest.raises(RollbackError):
            raise RollbackError("boom")

    def test_raise_catch_as_cicd(self):
        with pytest.raises(CICDError):
            raise RollbackError("boom")

    def test_str_representation(self):
        err = RollbackError("fail", from_version="2.0", to_version="1.0")
        s = str(err)
        assert "RollbackError" in s
        assert "from_version=2.0" in s
        assert "to_version=1.0" in s

    def test_to_dict(self):
        err = RollbackError("fail", from_version="3.0")
        d = err.to_dict()
        assert d["error_type"] == "RollbackError"
        assert d["context"]["from_version"] == "3.0"

    def test_error_code_default(self):
        err = RollbackError("fail")
        assert err.error_code == "RollbackError"


# ---------------------------------------------------------------------------
# Cross-cutting hierarchy tests
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestExceptionHierarchy:
    """Verify that all exceptions form the correct inheritance chain."""

    @pytest.mark.parametrize(
        "exc_cls",
        [PipelineError, BuildError, DeploymentError, ArtifactError, StageError, RollbackError],
    )
    def test_all_are_subclass_of_cicd_error(self, exc_cls):
        assert issubclass(exc_cls, CICDError)

    @pytest.mark.parametrize(
        "exc_cls",
        [PipelineError, BuildError, DeploymentError, ArtifactError, StageError, RollbackError],
    )
    def test_all_are_subclass_of_codomyrmex_error(self, exc_cls):
        assert issubclass(exc_cls, CodomyrmexError)

    @pytest.mark.parametrize(
        "exc_cls",
        [PipelineError, BuildError, DeploymentError, ArtifactError, StageError, RollbackError],
    )
    def test_all_are_subclass_of_exception(self, exc_cls):
        assert issubclass(exc_cls, Exception)

    @pytest.mark.parametrize(
        "exc_cls",
        [PipelineError, BuildError, DeploymentError, ArtifactError, StageError, RollbackError],
    )
    def test_catch_as_base_exception(self, exc_cls):
        with pytest.raises(CodomyrmexError):
            raise exc_cls("test")

    @pytest.mark.parametrize(
        "exc_cls",
        [PipelineError, BuildError, DeploymentError, ArtifactError, StageError, RollbackError],
    )
    def test_empty_context_by_default(self, exc_cls):
        err = exc_cls("msg")
        assert isinstance(err.context, dict)

    @pytest.mark.parametrize(
        "exc_cls",
        [PipelineError, BuildError, DeploymentError, ArtifactError, StageError, RollbackError],
    )
    def test_str_without_context_omits_context_section(self, exc_cls):
        err = exc_cls("bare message")
        s = str(err)
        assert "bare message" in s
        assert "Context:" not in s
