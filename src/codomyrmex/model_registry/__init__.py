"""
Model Registry Module

Model versioning, metadata, and lifecycle management.
"""

__version__ = "0.1.0"

import hashlib
import json
import os
from typing import Optional, List, Dict, Any, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from pathlib import Path
import threading


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
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    custom: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
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
    artifact_path: Optional[str] = None
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def full_name(self) -> str:
        """Get full model name with version."""
        return f"{self.model_name}:{self.version}"
    
    def to_dict(self) -> Dict[str, Any]:
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
    tags: Dict[str, str] = field(default_factory=dict)
    versions: List[ModelVersion] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def latest_version(self) -> Optional[ModelVersion]:
        """Get the latest version."""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.created_at)
    
    @property
    def production_version(self) -> Optional[ModelVersion]:
        """Get the production version."""
        for v in self.versions:
            if v.stage == ModelStage.PRODUCTION:
                return v
        return None
    
    def get_version(self, version: str) -> Optional[ModelVersion]:
        """Get a specific version."""
        for v in self.versions:
            if v.version == version:
                return v
        return None


class ModelStore(ABC):
    """Base class for model storage backends."""
    
    @abstractmethod
    def save_artifact(self, model_name: str, version: str, artifact: bytes) -> str:
        """Save model artifact and return path."""
        pass
    
    @abstractmethod
    def load_artifact(self, path: str) -> bytes:
        """Load model artifact from path."""
        pass
    
    @abstractmethod
    def delete_artifact(self, path: str) -> bool:
        """Delete model artifact."""
        pass


class FileModelStore(ModelStore):
    """File-based model storage."""
    
    def __init__(self, base_path: str = "./models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, model_name: str, version: str) -> Path:
        """Get path for a model version."""
        return self.base_path / model_name / version / "model.bin"
    
    def save_artifact(self, model_name: str, version: str, artifact: bytes) -> str:
        """Save model artifact."""
        path = self._get_path(model_name, version)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(artifact)
        return str(path)
    
    def load_artifact(self, path: str) -> bytes:
        """Load model artifact."""
        return Path(path).read_bytes()
    
    def delete_artifact(self, path: str) -> bool:
        """Delete model artifact."""
        try:
            Path(path).unlink()
            return True
        except FileNotFoundError:
            return False


class InMemoryModelStore(ModelStore):
    """In-memory model storage for testing."""
    
    def __init__(self):
        self._artifacts: Dict[str, bytes] = {}
        self._lock = threading.Lock()
    
    def save_artifact(self, model_name: str, version: str, artifact: bytes) -> str:
        """Save model artifact."""
        path = f"{model_name}/{version}/model.bin"
        with self._lock:
            self._artifacts[path] = artifact
        return path
    
    def load_artifact(self, path: str) -> bytes:
        """Load model artifact."""
        artifact = self._artifacts.get(path)
        if artifact is None:
            raise FileNotFoundError(f"Artifact not found: {path}")
        return artifact
    
    def delete_artifact(self, path: str) -> bool:
        """Delete model artifact."""
        with self._lock:
            if path in self._artifacts:
                del self._artifacts[path]
                return True
        return False


class ModelRegistry:
    """
    Central model registry for versioning and management.
    
    Usage:
        registry = ModelRegistry()
        
        # Register a model
        version = registry.register(
            name="my_classifier",
            version="1.0.0",
            framework=ModelFramework.SKLEARN,
            metrics=ModelMetrics(accuracy=0.95, f1_score=0.93),
            parameters={"n_estimators": 100},
            artifact=model_bytes,  # Optional serialized model
        )
        
        # Get model
        model = registry.get_model("my_classifier")
        latest = model.latest_version
        
        # Promote to production
        registry.transition_stage("my_classifier", "1.0.0", ModelStage.PRODUCTION)
        
        # Get production model
        prod_version = registry.get_production_model("my_classifier")
    """
    
    def __init__(self, store: Optional[ModelStore] = None):
        self.store = store or InMemoryModelStore()
        self._models: Dict[str, RegisteredModel] = {}
        self._lock = threading.Lock()
    
    def register(
        self,
        name: str,
        version: str,
        framework: ModelFramework = ModelFramework.CUSTOM,
        metrics: Optional[ModelMetrics] = None,
        parameters: Optional[Dict[str, Any]] = None,
        description: str = "",
        tags: Optional[Dict[str, str]] = None,
        artifact: Optional[bytes] = None,
    ) -> ModelVersion:
        """
        Register a new model version.
        
        Args:
            name: Model name
            version: Version string
            framework: ML framework used
            metrics: Performance metrics
            parameters: Training parameters
            description: Version description
            tags: Key-value tags
            artifact: Serialized model bytes
            
        Returns:
            The registered ModelVersion
        """
        with self._lock:
            # Create registered model if needed
            if name not in self._models:
                self._models[name] = RegisteredModel(name=name)
            
            model = self._models[name]
            
            # Check if version exists
            existing = model.get_version(version)
            if existing:
                raise ValueError(f"Version {version} already exists for model {name}")
            
            # Save artifact if provided
            artifact_path = None
            if artifact:
                artifact_path = self.store.save_artifact(name, version, artifact)
            
            # Create version
            model_version = ModelVersion(
                version=version,
                model_name=name,
                framework=framework,
                metrics=metrics or ModelMetrics(),
                parameters=parameters or {},
                description=description,
                tags=tags or {},
                artifact_path=artifact_path,
            )
            
            model.versions.append(model_version)
            return model_version
    
    def get_model(self, name: str) -> Optional[RegisteredModel]:
        """Get a registered model by name."""
        return self._models.get(name)
    
    def get_version(self, name: str, version: str) -> Optional[ModelVersion]:
        """Get a specific model version."""
        model = self.get_model(name)
        if model:
            return model.get_version(version)
        return None
    
    def get_latest(self, name: str) -> Optional[ModelVersion]:
        """Get the latest version of a model."""
        model = self.get_model(name)
        if model:
            return model.latest_version
        return None
    
    def get_production_model(self, name: str) -> Optional[ModelVersion]:
        """Get the production version of a model."""
        model = self.get_model(name)
        if model:
            return model.production_version
        return None
    
    def transition_stage(
        self,
        name: str,
        version: str,
        stage: ModelStage,
    ) -> Optional[ModelVersion]:
        """
        Transition a model version to a new stage.
        
        If transitioning to PRODUCTION, any existing production version
        is moved to ARCHIVED.
        """
        with self._lock:
            model = self.get_model(name)
            if not model:
                return None
            
            model_version = model.get_version(version)
            if not model_version:
                return None
            
            # If promoting to production, demote current production
            if stage == ModelStage.PRODUCTION:
                current_prod = model.production_version
                if current_prod and current_prod.version != version:
                    current_prod.stage = ModelStage.ARCHIVED
                    current_prod.updated_at = datetime.now()
            
            model_version.stage = stage
            model_version.updated_at = datetime.now()
            return model_version
    
    def list_models(self) -> List[str]:
        """List all registered model names."""
        return list(self._models.keys())
    
    def list_versions(self, name: str) -> List[ModelVersion]:
        """List all versions of a model."""
        model = self.get_model(name)
        if model:
            return model.versions.copy()
        return []
    
    def delete_version(self, name: str, version: str) -> bool:
        """Delete a model version."""
        with self._lock:
            model = self.get_model(name)
            if not model:
                return False
            
            model_version = model.get_version(version)
            if not model_version:
                return False
            
            # Delete artifact
            if model_version.artifact_path:
                self.store.delete_artifact(model_version.artifact_path)
            
            model.versions.remove(model_version)
            return True
    
    def load_artifact(self, name: str, version: str) -> Optional[bytes]:
        """Load a model artifact."""
        model_version = self.get_version(name, version)
        if model_version and model_version.artifact_path:
            return self.store.load_artifact(model_version.artifact_path)
        return None


__all__ = [
    # Enums
    "ModelStage",
    "ModelFramework",
    # Data classes
    "ModelMetrics",
    "ModelVersion",
    "RegisteredModel",
    # Stores
    "ModelStore",
    "FileModelStore",
    "InMemoryModelStore",
    # Registry
    "ModelRegistry",
]
