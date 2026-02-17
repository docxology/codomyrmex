"""
Model Registry

Central model registry for versioning and lifecycle management.
"""

import threading
from datetime import datetime
from typing import Any

from .models import (
    ModelFramework,
    ModelMetrics,
    ModelStage,
    ModelVersion,
    RegisteredModel,
)
from .stores import InMemoryModelStore, ModelStore


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

    def __init__(self, store: ModelStore | None = None):
        self.store = store or InMemoryModelStore()
        self._models: dict[str, RegisteredModel] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        version: str,
        framework: ModelFramework = ModelFramework.CUSTOM,
        metrics: ModelMetrics | None = None,
        parameters: dict[str, Any] | None = None,
        description: str = "",
        tags: dict[str, str] | None = None,
        artifact: bytes | None = None,
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

    def get_model(self, name: str) -> RegisteredModel | None:
        """Get a registered model by name."""
        return self._models.get(name)

    def get_version(self, name: str, version: str) -> ModelVersion | None:
        """Get a specific model version."""
        model = self.get_model(name)
        if model:
            return model.get_version(version)
        return None

    def get_latest(self, name: str) -> ModelVersion | None:
        """Get the latest version of a model."""
        model = self.get_model(name)
        if model:
            return model.latest_version
        return None

    def get_production_model(self, name: str) -> ModelVersion | None:
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
    ) -> ModelVersion | None:
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

    def list_models(self) -> list[str]:
        """List all registered model names."""
        return list(self._models.keys())

    def list_versions(self, name: str) -> list[ModelVersion]:
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

    def load_artifact(self, name: str, version: str) -> bytes | None:
        """Load a model artifact."""
        model_version = self.get_version(name, version)
        if model_version and model_version.artifact_path:
            return self.store.load_artifact(model_version.artifact_path)
        return None
