"""
Unit tests for model_ops.registry — Zero-Mock compliant.

Covers: ModelStage, ModelFramework, ModelMetrics, ModelVersion,
RegisteredModel, InMemoryModelStore, FileModelStore, ModelRegistry.
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.model_ops.registry.models import (
    ModelFramework,
    ModelMetrics,
    ModelStage,
    ModelVersion,
    RegisteredModel,
)
from codomyrmex.model_ops.registry.registry import ModelRegistry
from codomyrmex.model_ops.registry.stores import FileModelStore, InMemoryModelStore

# ── ModelStage / ModelFramework enums ────────────────────────────────


@pytest.mark.unit
class TestEnums:
    def test_model_stage_values(self):
        assert ModelStage.DEVELOPMENT.value == "development"
        assert ModelStage.STAGING.value == "staging"
        assert ModelStage.PRODUCTION.value == "production"
        assert ModelStage.ARCHIVED.value == "archived"

    def test_model_framework_values(self):
        assert ModelFramework.SKLEARN.value == "sklearn"
        assert ModelFramework.PYTORCH.value == "pytorch"
        assert ModelFramework.CUSTOM.value == "custom"


# ── ModelMetrics ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestModelMetrics:
    def test_defaults_are_none(self):
        m = ModelMetrics()
        assert m.accuracy is None
        assert m.f1_score is None
        assert m.custom == {}

    def test_to_dict_excludes_none(self):
        m = ModelMetrics(accuracy=0.95, f1_score=0.93)
        d = m.to_dict()
        assert d["accuracy"] == 0.95
        assert d["f1_score"] == 0.93
        assert "recall" not in d

    def test_to_dict_includes_custom(self):
        m = ModelMetrics(custom={"latency_ms": 12.3})
        d = m.to_dict()
        assert d["latency_ms"] == 12.3

    def test_all_metrics(self):
        m = ModelMetrics(
            accuracy=0.9,
            precision=0.88,
            recall=0.85,
            f1_score=0.87,
            auc_roc=0.92,
            mse=0.01,
            mae=0.05,
        )
        d = m.to_dict()
        assert len(d) == 7


# ── ModelVersion ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestModelVersion:
    def test_full_name(self):
        mv = ModelVersion(version="1.0.0", model_name="my_model")
        assert mv.full_name == "my_model:1.0.0"

    def test_defaults(self):
        mv = ModelVersion(version="v1", model_name="clf")
        assert mv.stage == ModelStage.DEVELOPMENT
        assert mv.framework == ModelFramework.CUSTOM
        assert mv.artifact_path is None
        assert mv.parameters == {}
        assert mv.tags == {}

    def test_to_dict(self):
        mv = ModelVersion(
            version="1.2.3",
            model_name="bert",
            framework=ModelFramework.PYTORCH,
            description="A fine-tuned BERT",
        )
        d = mv.to_dict()
        assert d["version"] == "1.2.3"
        assert d["model_name"] == "bert"
        assert d["framework"] == "pytorch"
        assert d["description"] == "A fine-tuned BERT"
        assert d["stage"] == "development"
        assert "created_at" in d
        assert "updated_at" in d


# ── RegisteredModel ───────────────────────────────────────────────────


@pytest.mark.unit
class TestRegisteredModel:
    def test_empty_model(self):
        rm = RegisteredModel(name="my_model")
        assert rm.latest_version is None
        assert rm.production_version is None
        assert rm.get_version("1.0") is None

    def test_latest_version_single(self):
        rm = RegisteredModel(name="clf")
        v = ModelVersion(version="1.0.0", model_name="clf")
        rm.versions.append(v)
        assert rm.latest_version is v

    def test_latest_version_multiple(self):
        import time
        rm = RegisteredModel(name="clf")
        v1 = ModelVersion(version="1.0.0", model_name="clf")
        time.sleep(0.001)
        v2 = ModelVersion(version="2.0.0", model_name="clf")
        rm.versions.extend([v1, v2])
        assert rm.latest_version is v2

    def test_production_version_none_when_not_promoted(self):
        rm = RegisteredModel(name="clf")
        v = ModelVersion(version="1.0.0", model_name="clf")
        rm.versions.append(v)
        assert rm.production_version is None

    def test_production_version_returns_promoted(self):
        rm = RegisteredModel(name="clf")
        v = ModelVersion(version="1.0.0", model_name="clf", stage=ModelStage.PRODUCTION)
        rm.versions.append(v)
        assert rm.production_version is v

    def test_get_version_found(self):
        rm = RegisteredModel(name="clf")
        v = ModelVersion(version="1.2.3", model_name="clf")
        rm.versions.append(v)
        assert rm.get_version("1.2.3") is v

    def test_get_version_not_found(self):
        rm = RegisteredModel(name="clf")
        assert rm.get_version("99.99") is None


# ── InMemoryModelStore ────────────────────────────────────────────────


@pytest.mark.unit
class TestInMemoryModelStore:
    def test_save_and_load_artifact(self):
        store = InMemoryModelStore()
        path = store.save_artifact("clf", "1.0", b"\x00\x01\x02")
        loaded = store.load_artifact(path)
        assert loaded == b"\x00\x01\x02"

    def test_load_missing_raises(self):
        store = InMemoryModelStore()
        with pytest.raises(FileNotFoundError):
            store.load_artifact("nonexistent/path")

    def test_delete_artifact(self):
        store = InMemoryModelStore()
        path = store.save_artifact("m", "v1", b"data")
        assert store.delete_artifact(path) is True
        with pytest.raises(FileNotFoundError):
            store.load_artifact(path)

    def test_delete_missing_returns_false(self):
        store = InMemoryModelStore()
        assert store.delete_artifact("ghost/path") is False

    def test_path_format(self):
        store = InMemoryModelStore()
        path = store.save_artifact("my_model", "2.0.1", b"x")
        assert "my_model" in path
        assert "2.0.1" in path


# ── FileModelStore ────────────────────────────────────────────────────


@pytest.mark.unit
class TestFileModelStore:
    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FileModelStore(base_path=tmpdir)
            path = store.save_artifact("mymodel", "v1", b"hello bytes")
            loaded = store.load_artifact(path)
            assert loaded == b"hello bytes"

    def test_delete_artifact(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FileModelStore(base_path=tmpdir)
            path = store.save_artifact("m", "v1", b"data")
            assert Path(path).exists()
            assert store.delete_artifact(path) is True
            assert not Path(path).exists()

    def test_delete_missing_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FileModelStore(base_path=tmpdir)
            assert store.delete_artifact("/nonexistent/path.bin") is False


# ── ModelRegistry ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestModelRegistry:
    def test_register_basic(self):
        reg = ModelRegistry()
        v = reg.register("clf", "1.0.0")
        assert v.version == "1.0.0"
        assert v.model_name == "clf"

    def test_register_with_metrics(self):
        reg = ModelRegistry()
        m = ModelMetrics(accuracy=0.95)
        v = reg.register("bert", "v1", metrics=m)
        assert v.metrics.accuracy == 0.95

    def test_register_with_framework(self):
        reg = ModelRegistry()
        v = reg.register("net", "v1", framework=ModelFramework.PYTORCH)
        assert v.framework == ModelFramework.PYTORCH

    def test_register_duplicate_raises(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        with pytest.raises(ValueError, match="already exists"):
            reg.register("clf", "1.0.0")

    def test_get_model_registered(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        model = reg.get_model("clf")
        assert model is not None
        assert model.name == "clf"

    def test_get_model_missing_returns_none(self):
        reg = ModelRegistry()
        assert reg.get_model("ghost") is None

    def test_get_version(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        v = reg.get_version("clf", "1.0.0")
        assert v is not None
        assert v.version == "1.0.0"

    def test_get_version_missing_model_returns_none(self):
        reg = ModelRegistry()
        assert reg.get_version("ghost", "1.0") is None

    def test_get_version_missing_version_returns_none(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        assert reg.get_version("clf", "99.0") is None

    def test_get_latest(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        v = reg.get_latest("clf")
        assert v is not None
        assert v.version == "1.0.0"

    def test_get_latest_missing_returns_none(self):
        reg = ModelRegistry()
        assert reg.get_latest("ghost") is None

    def test_get_production_model_none_initially(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        assert reg.get_production_model("clf") is None

    def test_transition_stage_to_production(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        v = reg.transition_stage("clf", "1.0.0", ModelStage.PRODUCTION)
        assert v is not None
        assert v.stage == ModelStage.PRODUCTION
        assert reg.get_production_model("clf") is v

    def test_transition_demotes_previous_production(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        reg.register("clf", "2.0.0")
        reg.transition_stage("clf", "1.0.0", ModelStage.PRODUCTION)
        reg.transition_stage("clf", "2.0.0", ModelStage.PRODUCTION)
        v1 = reg.get_version("clf", "1.0.0")
        v2 = reg.get_version("clf", "2.0.0")
        assert v1.stage == ModelStage.ARCHIVED
        assert v2.stage == ModelStage.PRODUCTION

    def test_transition_missing_model_returns_none(self):
        reg = ModelRegistry()
        assert reg.transition_stage("ghost", "1.0", ModelStage.PRODUCTION) is None

    def test_transition_missing_version_returns_none(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        assert reg.transition_stage("clf", "99.0", ModelStage.PRODUCTION) is None

    def test_list_models(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0")
        reg.register("reg", "1.0")
        names = reg.list_models()
        assert "clf" in names
        assert "reg" in names
        assert len(names) == 2

    def test_list_versions(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0")
        reg.register("clf", "2.0")
        versions = reg.list_versions("clf")
        assert len(versions) == 2

    def test_list_versions_missing_model_empty(self):
        reg = ModelRegistry()
        assert reg.list_versions("ghost") == []

    def test_delete_version(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0")
        assert reg.delete_version("clf", "1.0") is True
        assert reg.get_version("clf", "1.0") is None

    def test_delete_version_missing_model_false(self):
        reg = ModelRegistry()
        assert reg.delete_version("ghost", "1.0") is False

    def test_delete_version_missing_version_false(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0")
        assert reg.delete_version("clf", "99.0") is False

    def test_register_with_artifact_and_load(self):
        reg = ModelRegistry()
        artifact = b"model_bytes_here"
        reg.register("clf", "1.0.0", artifact=artifact)
        loaded = reg.load_artifact("clf", "1.0.0")
        assert loaded == artifact

    def test_load_artifact_no_artifact_returns_none(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        assert reg.load_artifact("clf", "1.0.0") is None

    def test_load_artifact_missing_model_returns_none(self):
        reg = ModelRegistry()
        assert reg.load_artifact("ghost", "1.0") is None

    def test_transition_to_staging(self):
        reg = ModelRegistry()
        reg.register("clf", "1.0.0")
        v = reg.transition_stage("clf", "1.0.0", ModelStage.STAGING)
        assert v.stage == ModelStage.STAGING

    def test_register_with_tags_and_params(self):
        reg = ModelRegistry()
        v = reg.register(
            "clf",
            "1.0.0",
            parameters={"n_estimators": 100},
            tags={"env": "prod"},
            description="My classifier",
        )
        assert v.parameters["n_estimators"] == 100
        assert v.tags["env"] == "prod"
        assert v.description == "My classifier"
