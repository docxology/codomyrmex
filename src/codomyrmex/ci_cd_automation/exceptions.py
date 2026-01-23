"""CI/CD Automation Exception Classes.

This module defines exceptions specific to CI/CD automation operations
including pipelines, builds, deployments, and artifact management.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import CodomyrmexError, CICDError


class PipelineError(CICDError):
    """Base exception for pipeline-related errors.

    Raised when pipeline operations fail, including creation,
    execution, and configuration errors.
    """

    def __init__(
        self,
        message: str,
        pipeline_name: str | None = None,
        stage: str | None = None,
        **kwargs: Any
    ):
        """Initialize PipelineError.

        Args:
            message: Error description
            pipeline_name: Name of the pipeline that failed
            stage: Pipeline stage where error occurred
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if pipeline_name:
            self.context["pipeline_name"] = pipeline_name
        if stage:
            self.context["stage"] = stage


class BuildError(CICDError):
    """Raised when build operations fail.

    This includes compilation errors, build script failures,
    and build environment issues.
    """

    def __init__(
        self,
        message: str,
        build_id: str | None = None,
        build_target: str | None = None,
        exit_code: int | None = None,
        **kwargs: Any
    ):
        """Initialize BuildError.

        Args:
            message: Error description
            build_id: Identifier of the failed build
            build_target: Target being built when error occurred
            exit_code: Build process exit code
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if build_id:
            self.context["build_id"] = build_id
        if build_target:
            self.context["build_target"] = build_target
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class DeploymentError(CICDError):
    """Raised when deployment operations fail.

    This includes deployment script failures, environment issues,
    and rollback failures.
    """

    def __init__(
        self,
        message: str,
        deployment_id: str | None = None,
        environment: str | None = None,
        target_version: str | None = None,
        **kwargs: Any
    ):
        """Initialize DeploymentError.

        Args:
            message: Error description
            deployment_id: Identifier of the failed deployment
            environment: Target environment (e.g., staging, production)
            target_version: Version being deployed
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if deployment_id:
            self.context["deployment_id"] = deployment_id
        if environment:
            self.context["environment"] = environment
        if target_version:
            self.context["target_version"] = target_version


class ArtifactError(CICDError):
    """Raised when artifact operations fail.

    This includes artifact storage, retrieval, versioning,
    and registry operations.
    """

    def __init__(
        self,
        message: str,
        artifact_name: str | None = None,
        artifact_version: str | None = None,
        registry: str | None = None,
        **kwargs: Any
    ):
        """Initialize ArtifactError.

        Args:
            message: Error description
            artifact_name: Name of the artifact
            artifact_version: Version of the artifact
            registry: Registry where artifact operation failed
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if artifact_name:
            self.context["artifact_name"] = artifact_name
        if artifact_version:
            self.context["artifact_version"] = artifact_version
        if registry:
            self.context["registry"] = registry


class StageError(CICDError):
    """Raised when a pipeline stage fails."""

    def __init__(
        self,
        message: str,
        stage_name: str | None = None,
        job_name: str | None = None,
        **kwargs: Any
    ):
        """Initialize StageError.

        Args:
            message: Error description
            stage_name: Name of the failed stage
            job_name: Name of the job within the stage
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if stage_name:
            self.context["stage_name"] = stage_name
        if job_name:
            self.context["job_name"] = job_name


class RollbackError(CICDError):
    """Raised when rollback operations fail."""

    def __init__(
        self,
        message: str,
        from_version: str | None = None,
        to_version: str | None = None,
        **kwargs: Any
    ):
        """Initialize RollbackError.

        Args:
            message: Error description
            from_version: Current version being rolled back from
            to_version: Target version to roll back to
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if from_version:
            self.context["from_version"] = from_version
        if to_version:
            self.context["to_version"] = to_version


__all__ = [
    "PipelineError",
    "BuildError",
    "DeploymentError",
    "ArtifactError",
    "StageError",
    "RollbackError",
]
