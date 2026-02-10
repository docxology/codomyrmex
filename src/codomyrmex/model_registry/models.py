"""
Model Registry Models

Data classes and enums for model versioning and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ModelStage(Enum):
    """Lifecycle stages for models."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ModelFramework(Enum):
    """Supported ML frameworks."""
    SKLEARN = "sklearn"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    CUSTOM = "custom"


@dataclass
class ModelMetrics:
    """Performance metrics for a model."""
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None
    auc_roc: float | None = None
    mse: float | None = None
    mae: float | None = None
    custom: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {k: v for k, v in self.__dict__.items() if v is not None and k != 'custom'}
        result.update(self.custom)
        return result


@dataclass
class ModelVersion:
    """A specific version of a model."""
    version: str
    model_name: str
    stage: ModelStage = ModelStage.DEVELOPMENT
    framework: ModelFramework = ModelFramework.CUSTOM
    artifact_path: str | None = None
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    parameters: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def full_name(self) -> str:
        """Get full model name with version."""
        return f"{self.model_name}:{self.version}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "model_name": self.model_name,
            "stage": self.stage.value,
            "framework": self.framework.value,
            "artifact_path": self.artifact_path,
            "metrics": self.metrics.to_dict(),
            "parameters": self.parameters,
            "tags": self.tags,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class RegisteredModel:
    """A registered model with multiple versions."""
    name: str
    description: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    versions: list[ModelVersion] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def latest_version(self) -> ModelVersion | None:
        """Get the latest version."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.created_at)

    @property
    def production_version(self) -> ModelVersion | None:
        """Get the production version."""
        for v in self.versions:
            if v.stage == ModelStage.PRODUCTION:
                return v
        return None

    def get_version(self, version: str) -> ModelVersion | None:
        """Get a specific version."""
        for v in self.versions:
            if v.version == version:
                return v
        return None
