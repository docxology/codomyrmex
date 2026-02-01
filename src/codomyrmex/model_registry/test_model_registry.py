"""
Tests for Model Registry Module
"""

import pytest
from codomyrmex.model_registry import (
    ModelStage,
    ModelFramework,
    ModelMetrics,
    ModelVersion,
    RegisteredModel,
    InMemoryModelStore,
    ModelRegistry,
)


class TestModelMetrics:
    """Tests for ModelMetrics."""
    
    def test_to_dict(self):
        """Should convert to dict."""
        m = ModelMetrics(accuracy=0.95, f1_score=0.93, custom={"auc": 0.98})
        d = m.to_dict()
        
        assert d["accuracy"] == 0.95
        assert d["f1_score"] == 0.93
        assert d["auc"] == 0.98


class TestModelVersion:
    """Tests for ModelVersion."""
    
    def test_full_name(self):
        """Should generate full name."""
        v = ModelVersion(version="1.0.0", model_name="classifier")
        assert v.full_name == "classifier:1.0.0"
    
    def test_to_dict(self):
        """Should convert to dict."""
        v = ModelVersion(
            version="1.0.0",
            model_name="classifier",
            framework=ModelFramework.SKLEARN,
        )
        d = v.to_dict()
        
        assert d["version"] == "1.0.0"
        assert d["framework"] == "sklearn"


class TestRegisteredModel:
    """Tests for RegisteredModel."""
    
    def test_latest_version(self):
        """Should get latest version."""
        model = RegisteredModel(name="test")
        model.versions.append(ModelVersion("1.0.0", "test"))
        model.versions.append(ModelVersion("2.0.0", "test"))
        
        # Latest is by created_at, manually adjust for test
        latest = model.latest_version
        assert latest is not None
    
    def test_production_version(self):
        """Should get production version."""
        model = RegisteredModel(name="test")
        model.versions.append(ModelVersion("1.0.0", "test", stage=ModelStage.DEVELOPMENT))
        model.versions.append(ModelVersion("2.0.0", "test", stage=ModelStage.PRODUCTION))
        
        prod = model.production_version
        assert prod.version == "2.0.0"
    
    def test_get_version(self):
        """Should get specific version."""
        model = RegisteredModel(name="test")
        model.versions.append(ModelVersion("1.0.0", "test"))
        
        v = model.get_version("1.0.0")
        assert v.version == "1.0.0"


class TestInMemoryModelStore:
    """Tests for InMemoryModelStore."""
    
    def test_save_and_load(self):
        """Should save and load artifact."""
        store = InMemoryModelStore()
        
        artifact = b"model_bytes_here"
        path = store.save_artifact("model", "1.0.0", artifact)
        
        loaded = store.load_artifact(path)
        assert loaded == artifact
    
    def test_delete(self):
        """Should delete artifact."""
        store = InMemoryModelStore()
        path = store.save_artifact("model", "1.0.0", b"data")
        
        result = store.delete_artifact(path)
        assert result is True
        
        with pytest.raises(FileNotFoundError):
            store.load_artifact(path)


class TestModelRegistry:
    """Tests for ModelRegistry."""
    
    def test_register_model(self):
        """Should register model."""
        registry = ModelRegistry()
        
        version = registry.register(
            name="classifier",
            version="1.0.0",
            framework=ModelFramework.SKLEARN,
            metrics=ModelMetrics(accuracy=0.95),
        )
        
        assert version.model_name == "classifier"
        assert version.version == "1.0.0"
    
    def test_register_with_artifact(self):
        """Should store artifact."""
        registry = ModelRegistry()
        
        artifact = b"serialized_model"
        version = registry.register(
            name="model",
            version="1.0.0",
            artifact=artifact,
        )
        
        loaded = registry.load_artifact("model", "1.0.0")
        assert loaded == artifact
    
    def test_get_model(self):
        """Should get registered model."""
        registry = ModelRegistry()
        registry.register(name="test", version="1.0.0")
        
        model = registry.get_model("test")
        assert model is not None
        assert model.name == "test"
    
    def test_get_version(self):
        """Should get specific version."""
        registry = ModelRegistry()
        registry.register(name="test", version="1.0.0")
        registry.register(name="test", version="2.0.0")
        
        v = registry.get_version("test", "1.0.0")
        assert v.version == "1.0.0"
    
    def test_duplicate_version_error(self):
        """Should error on duplicate version."""
        registry = ModelRegistry()
        registry.register(name="test", version="1.0.0")
        
        with pytest.raises(ValueError):
            registry.register(name="test", version="1.0.0")
    
    def test_transition_stage(self):
        """Should transition stage."""
        registry = ModelRegistry()
        registry.register(name="test", version="1.0.0")
        
        version = registry.transition_stage("test", "1.0.0", ModelStage.PRODUCTION)
        
        assert version.stage == ModelStage.PRODUCTION
    
    def test_promote_demotes_current(self):
        """Should demote current production when promoting."""
        registry = ModelRegistry()
        registry.register(name="test", version="1.0.0")
        registry.register(name="test", version="2.0.0")
        
        registry.transition_stage("test", "1.0.0", ModelStage.PRODUCTION)
        registry.transition_stage("test", "2.0.0", ModelStage.PRODUCTION)
        
        v1 = registry.get_version("test", "1.0.0")
        v2 = registry.get_version("test", "2.0.0")
        
        assert v1.stage == ModelStage.ARCHIVED
        assert v2.stage == ModelStage.PRODUCTION
    
    def test_list_models(self):
        """Should list all models."""
        registry = ModelRegistry()
        registry.register(name="model1", version="1.0.0")
        registry.register(name="model2", version="1.0.0")
        
        models = registry.list_models()
        assert set(models) == {"model1", "model2"}
    
    def test_delete_version(self):
        """Should delete version."""
        registry = ModelRegistry()
        registry.register(name="test", version="1.0.0")
        
        result = registry.delete_version("test", "1.0.0")
        assert result is True
        
        assert registry.get_version("test", "1.0.0") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
