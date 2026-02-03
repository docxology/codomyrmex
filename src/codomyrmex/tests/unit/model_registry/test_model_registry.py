"""Unit tests for model_registry module."""
import pytest


@pytest.mark.unit
class TestModelRegistryImports:
    """Test suite for model_registry module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import model_registry
        assert model_registry is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.model_registry import __all__
        expected_exports = [
            "ModelStage",
            "ModelFramework",
            "ModelMetrics",
            "ModelVersion",
            "RegisteredModel",
            "ModelStore",
            "FileModelStore",
            "InMemoryModelStore",
            "ModelRegistry",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestModelStage:
    """Test suite for ModelStage enum."""

    def test_model_stage_values(self):
        """Verify all model stages are available."""
        from codomyrmex.model_registry import ModelStage

        assert ModelStage.DEVELOPMENT.value == "development"
        assert ModelStage.STAGING.value == "staging"
        assert ModelStage.PRODUCTION.value == "production"
        assert ModelStage.ARCHIVED.value == "archived"


@pytest.mark.unit
class TestModelFramework:
    """Test suite for ModelFramework enum."""

    def test_model_framework_values(self):
        """Verify all model frameworks are available."""
        from codomyrmex.model_registry import ModelFramework

        assert ModelFramework.SKLEARN.value == "sklearn"
        assert ModelFramework.PYTORCH.value == "pytorch"
        assert ModelFramework.TENSORFLOW.value == "tensorflow"
        assert ModelFramework.ONNX.value == "onnx"
        assert ModelFramework.CUSTOM.value == "custom"


@pytest.mark.unit
class TestModelMetrics:
    """Test suite for ModelMetrics dataclass."""

    def test_metrics_creation(self):
        """Verify ModelMetrics can be created."""
        from codomyrmex.model_registry import ModelMetrics

        metrics = ModelMetrics(
            accuracy=0.95,
            precision=0.92,
            recall=0.88,
            f1_score=0.90,
        )

        assert metrics.accuracy == 0.95
        assert metrics.precision == 0.92

    def test_metrics_to_dict(self):
        """Verify metrics serialization."""
        from codomyrmex.model_registry import ModelMetrics

        metrics = ModelMetrics(
            accuracy=0.85,
            mse=0.05,
            custom={"auc": 0.92},
        )

        result = metrics.to_dict()
        assert result["accuracy"] == 0.85
        assert result["mse"] == 0.05
        assert result["auc"] == 0.92


@pytest.mark.unit
class TestModelVersion:
    """Test suite for ModelVersion dataclass."""

    def test_version_creation(self):
        """Verify ModelVersion can be created."""
        from codomyrmex.model_registry import (
            ModelVersion, ModelStage, ModelFramework
        )

        version = ModelVersion(
            version="1.0.0",
            model_name="classifier",
            stage=ModelStage.DEVELOPMENT,
            framework=ModelFramework.SKLEARN,
        )

        assert version.version == "1.0.0"
        assert version.model_name == "classifier"
        assert version.stage == ModelStage.DEVELOPMENT

    def test_version_full_name(self):
        """Verify full name property."""
        from codomyrmex.model_registry import ModelVersion

        version = ModelVersion(version="2.0", model_name="my_model")

        assert version.full_name == "my_model:2.0"

    def test_version_to_dict(self):
        """Verify version serialization."""
        from codomyrmex.model_registry import (
            ModelVersion, ModelMetrics, ModelFramework
        )

        version = ModelVersion(
            version="1.0",
            model_name="test",
            framework=ModelFramework.PYTORCH,
            metrics=ModelMetrics(accuracy=0.9),
            parameters={"epochs": 100},
        )

        result = version.to_dict()
        assert result["version"] == "1.0"
        assert result["framework"] == "pytorch"
        assert result["parameters"]["epochs"] == 100


@pytest.mark.unit
class TestRegisteredModel:
    """Test suite for RegisteredModel dataclass."""

    def test_model_creation(self):
        """Verify RegisteredModel can be created."""
        from codomyrmex.model_registry import RegisteredModel

        model = RegisteredModel(
            name="my_classifier",
            description="A classification model",
        )

        assert model.name == "my_classifier"
        assert len(model.versions) == 0

    def test_model_latest_version(self):
        """Verify latest version retrieval."""
        from codomyrmex.model_registry import RegisteredModel, ModelVersion
        from datetime import datetime, timedelta

        model = RegisteredModel(name="test")

        v1 = ModelVersion(version="1.0", model_name="test")
        v1.created_at = datetime.now() - timedelta(days=1)

        v2 = ModelVersion(version="2.0", model_name="test")
        v2.created_at = datetime.now()

        model.versions = [v1, v2]

        assert model.latest_version.version == "2.0"

    def test_model_production_version(self):
        """Verify production version retrieval."""
        from codomyrmex.model_registry import (
            RegisteredModel, ModelVersion, ModelStage
        )

        model = RegisteredModel(name="test")

        v1 = ModelVersion(version="1.0", model_name="test", stage=ModelStage.ARCHIVED)
        v2 = ModelVersion(version="2.0", model_name="test", stage=ModelStage.PRODUCTION)

        model.versions = [v1, v2]

        assert model.production_version.version == "2.0"

    def test_model_get_version(self):
        """Verify version retrieval by version string."""
        from codomyrmex.model_registry import RegisteredModel, ModelVersion

        model = RegisteredModel(name="test")
        model.versions = [
            ModelVersion(version="1.0", model_name="test"),
            ModelVersion(version="2.0", model_name="test"),
        ]

        v = model.get_version("1.0")
        assert v is not None
        assert v.version == "1.0"

        missing = model.get_version("3.0")
        assert missing is None


@pytest.mark.unit
class TestInMemoryModelStore:
    """Test suite for InMemoryModelStore."""

    def test_store_save_and_load(self):
        """Verify artifact storage and retrieval."""
        from codomyrmex.model_registry import InMemoryModelStore

        store = InMemoryModelStore()
        artifact = b"model binary data"

        path = store.save_artifact("my_model", "1.0", artifact)
        loaded = store.load_artifact(path)

        assert loaded == artifact

    def test_store_delete(self):
        """Verify artifact deletion."""
        from codomyrmex.model_registry import InMemoryModelStore

        store = InMemoryModelStore()
        path = store.save_artifact("model", "1.0", b"data")

        assert store.delete_artifact(path) is True
        assert store.delete_artifact(path) is False  # Already deleted

    def test_store_load_missing(self):
        """Verify loading missing artifact raises error."""
        from codomyrmex.model_registry import InMemoryModelStore

        store = InMemoryModelStore()

        with pytest.raises(FileNotFoundError):
            store.load_artifact("nonexistent/path")


@pytest.mark.unit
class TestModelRegistry:
    """Test suite for ModelRegistry."""

    def test_registry_register_model(self):
        """Verify model registration."""
        from codomyrmex.model_registry import (
            ModelRegistry, ModelFramework, ModelMetrics
        )

        registry = ModelRegistry()

        version = registry.register(
            name="classifier",
            version="1.0.0",
            framework=ModelFramework.SKLEARN,
            metrics=ModelMetrics(accuracy=0.95),
            description="Test classifier",
        )

        assert version.model_name == "classifier"
        assert version.version == "1.0.0"

    def test_registry_duplicate_version_error(self):
        """Verify duplicate version raises error."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()

        registry.register(name="model", version="1.0")

        with pytest.raises(ValueError, match="already exists"):
            registry.register(name="model", version="1.0")

    def test_registry_get_model(self):
        """Verify model retrieval."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()
        registry.register(name="test_model", version="1.0")

        model = registry.get_model("test_model")
        assert model is not None
        assert model.name == "test_model"

        missing = registry.get_model("nonexistent")
        assert missing is None

    def test_registry_get_version(self):
        """Verify version retrieval."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()
        registry.register(name="model", version="1.0")
        registry.register(name="model", version="2.0")

        v = registry.get_version("model", "1.0")
        assert v is not None
        assert v.version == "1.0"

    def test_registry_get_latest(self):
        """Verify latest version retrieval."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()
        registry.register(name="model", version="1.0")
        registry.register(name="model", version="2.0")

        latest = registry.get_latest("model")
        assert latest.version == "2.0"

    def test_registry_transition_stage(self):
        """Verify stage transition."""
        from codomyrmex.model_registry import ModelRegistry, ModelStage

        registry = ModelRegistry()
        registry.register(name="model", version="1.0")

        registry.transition_stage("model", "1.0", ModelStage.STAGING)

        version = registry.get_version("model", "1.0")
        assert version.stage == ModelStage.STAGING

    def test_registry_production_transition_demotes_previous(self):
        """Verify production promotion demotes previous production version."""
        from codomyrmex.model_registry import ModelRegistry, ModelStage

        registry = ModelRegistry()
        registry.register(name="model", version="1.0")
        registry.register(name="model", version="2.0")

        # Promote 1.0 to production
        registry.transition_stage("model", "1.0", ModelStage.PRODUCTION)

        # Promote 2.0 to production - should demote 1.0
        registry.transition_stage("model", "2.0", ModelStage.PRODUCTION)

        v1 = registry.get_version("model", "1.0")
        v2 = registry.get_version("model", "2.0")

        assert v1.stage == ModelStage.ARCHIVED
        assert v2.stage == ModelStage.PRODUCTION

    def test_registry_list_models(self):
        """Verify model listing."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()
        registry.register(name="model_a", version="1.0")
        registry.register(name="model_b", version="1.0")

        models = registry.list_models()
        assert "model_a" in models
        assert "model_b" in models

    def test_registry_list_versions(self):
        """Verify version listing."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()
        registry.register(name="model", version="1.0")
        registry.register(name="model", version="2.0")
        registry.register(name="model", version="3.0")

        versions = registry.list_versions("model")
        assert len(versions) == 3

    def test_registry_delete_version(self):
        """Verify version deletion."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()
        registry.register(name="model", version="1.0")
        registry.register(name="model", version="2.0")

        deleted = registry.delete_version("model", "1.0")
        assert deleted is True

        versions = registry.list_versions("model")
        assert len(versions) == 1
        assert versions[0].version == "2.0"

    def test_registry_artifact_storage(self):
        """Verify artifact storage and retrieval."""
        from codomyrmex.model_registry import ModelRegistry

        registry = ModelRegistry()
        artifact = b"serialized model data"

        registry.register(name="model", version="1.0", artifact=artifact)

        loaded = registry.load_artifact("model", "1.0")
        assert loaded == artifact
