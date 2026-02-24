"""
Infrastructure shared types for Codomyrmex.

Provides types for deployments, pipelines, resources, and build artifacts.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeploymentStatus(Enum):
    """Status of a deployment."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class PipelineStatus(Enum):
    """Status of a CI/CD pipeline."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Type of metric."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Deployment:
    """
    Represents a deployment operation.

    Used by deployment, containerization, edge_computing modules.
    """
    id: str
    name: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    target: str = ""
    version: str = ""
    environment: str = ""
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "target": self.target,
            "version": self.version,
            "environment": self.environment,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }


@dataclass
class Pipeline:
    """
    Represents a CI/CD pipeline.

    Used by ci_cd_automation, build_synthesis modules.
    """
    id: str
    name: str
    status: PipelineStatus = PipelineStatus.QUEUED
    stages: list[str] = field(default_factory=list)
    current_stage: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "stages": self.stages,
            "current_stage": self.current_stage,
            "metadata": self.metadata,
        }


@dataclass
class Resource:
    """
    Represents a managed resource.

    Used by cloud, containerization, service_mesh modules.
    """
    id: str
    name: str
    resource_type: str = ""
    provider: str = ""
    status: str = "active"
    properties: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "name": self.name,
            "resource_type": self.resource_type,
            "provider": self.provider,
            "status": self.status,
            "properties": self.properties,
            "metadata": self.metadata,
        }


@dataclass
class BuildArtifact:
    """
    Represents a build artifact.

    Used by build_synthesis, ci_cd_automation modules.
    """
    name: str
    path: str
    artifact_type: str = ""  # binary, docker_image, package, etc.
    size_bytes: int = 0
    checksum: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "name": self.name,
            "path": self.path,
            "artifact_type": self.artifact_type,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "metadata": self.metadata,
        }


@dataclass
class Metric:
    """
    Represents a metric measurement.

    Used by metrics, telemetry, observability_dashboard modules.
    """
    name: str
    value: float
    metric_type: MetricType = MetricType.GAUGE
    labels: dict[str, str] = field(default_factory=dict)
    unit: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type.value,
            "labels": self.labels,
            "unit": self.unit,
            "metadata": self.metadata,
        }


@dataclass
class Credential:
    """
    Represents a credential reference (never stores secrets directly).

    Used by auth, encryption, security modules.
    """
    id: str
    name: str
    credential_type: str = ""  # api_key, token, certificate, etc.
    provider: str = ""
    is_valid: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Permission:
    """
    Represents a permission grant.

    Used by auth, security modules.
    """
    subject: str
    action: str
    resource: str
    effect: str = "allow"  # allow, deny
    conditions: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """
    Represents a step in a workflow.

    Used by orchestrator, logistics modules.
    """
    id: str
    name: str
    action: str
    status: str = "pending"
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "name": self.name,
            "action": self.action,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


__all__ = [
    "Deployment",
    "DeploymentStatus",
    "Pipeline",
    "PipelineStatus",
    "Resource",
    "BuildArtifact",
    "Metric",
    "MetricType",
    "Credential",
    "Permission",
    "WorkflowStep",
]
