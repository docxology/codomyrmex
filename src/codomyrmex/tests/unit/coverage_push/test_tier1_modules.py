"""Tests for cerebrum, fpf, containerization, and git_operations modules.

Coverage push: targeting the 4 highest-gap Tier-1/2 modules.
"""

import pytest


# ===================================================================
# Cerebrum Core Models
# ===================================================================

@pytest.mark.unit
class TestCerebrumModel:
    """Test cerebrum Model dataclass."""

    def test_model_creation(self):
        """Test functionality: model creation."""
        from codomyrmex.cerebrum.core.models import Model
        m = Model(name="test_model", model_type="bayesian")
        assert m.name == "test_model"
        assert m.model_type == "bayesian"

    def test_model_to_dict(self):
        """Test functionality: model to dict."""
        from codomyrmex.cerebrum.core.models import Model
        m = Model(name="test", model_type="cbr", parameters={"k": 5})
        d = m.to_dict()
        assert d["name"] == "test"
        assert d["parameters"]["k"] == 5

    def test_model_from_dict(self):
        """Test functionality: model from dict."""
        from codomyrmex.cerebrum.core.models import Model
        d = {"name": "restored", "model_type": "neural", "parameters": {"lr": 0.01}}
        m = Model.from_dict(d)
        assert m.name == "restored"
        assert m.parameters["lr"] == 0.01

    def test_model_roundtrip(self):
        """Test functionality: model roundtrip."""
        from codomyrmex.cerebrum.core.models import Model
        original = Model(name="rt", model_type="hybrid", parameters={"a": 1}, metadata={"v": "2"})
        restored = Model.from_dict(original.to_dict())
        assert original.to_dict() == restored.to_dict()


@pytest.mark.unit
class TestReasoningResult:
    """Test ReasoningResult dataclass."""

    def test_creation(self):
        """Test functionality: creation."""
        from codomyrmex.cerebrum.core.models import ReasoningResult
        r = ReasoningResult(prediction="yes", confidence=0.95)
        assert r.prediction == "yes"
        assert r.confidence == 0.95

    def test_to_dict(self):
        """Test functionality: to dict."""
        from codomyrmex.cerebrum.core.models import ReasoningResult
        r = ReasoningResult(prediction=42, confidence=0.8, evidence={"key": "val"})
        d = r.to_dict()
        assert d["prediction"] == 42
        assert d["confidence"] == 0.8
        assert d["evidence"]["key"] == "val"


@pytest.mark.unit
class TestCerebrumConfig:
    """Test CerebrumConfig dataclass."""

    def test_defaults(self):
        """Test functionality: defaults."""
        from codomyrmex.cerebrum.core.config import CerebrumConfig
        cfg = CerebrumConfig()
        assert cfg.case_similarity_threshold == 0.7
        assert cfg.max_retrieved_cases == 10
        assert cfg.inference_method == "variable_elimination"

    def test_to_dict(self):
        """Test functionality: to dict."""
        from codomyrmex.cerebrum.core.config import CerebrumConfig
        cfg = CerebrumConfig(learning_rate=0.05)
        d = cfg.to_dict()
        assert d["learning_rate"] == 0.05
        assert "case_similarity_threshold" in d

    def test_from_dict(self):
        """Test functionality: from dict."""
        from codomyrmex.cerebrum.core.config import CerebrumConfig
        cfg = CerebrumConfig()
        d = cfg.to_dict()
        restored = CerebrumConfig.from_dict(d)
        assert restored.case_similarity_threshold == cfg.case_similarity_threshold


@pytest.mark.unit
class TestTransformations:
    """Test cerebrum transformation classes."""

    def test_model_transformer_init(self):
        """Test functionality: model transformer init."""
        from codomyrmex.cerebrum.core.transformations import AdaptationTransformer
        t = AdaptationTransformer()
        assert t is not None

    def test_adaptation_transformer_init(self):
        """Test functionality: adaptation transformer init."""
        from codomyrmex.cerebrum.core.transformations import AdaptationTransformer
        t = AdaptationTransformer(adaptation_rate=0.2)
        assert t.adaptation_rate == 0.2

    def test_learning_transformer_init(self):
        """Test functionality: learning transformer init."""
        from codomyrmex.cerebrum.core.transformations import LearningTransformer
        t = LearningTransformer(learning_rate=0.05)
        assert t.learning_rate == 0.05

    def test_transformation_manager_register(self):
        """Test functionality: transformation manager register."""
        from codomyrmex.cerebrum.core.transformations import (
            AdaptationTransformer, TransformationManager,
        )
        mgr = TransformationManager()
        mgr.register_transformer("basic", AdaptationTransformer())
        assert "basic" in mgr.transformers

    def test_adaptation_update_parameters(self):
        """Test functionality: adaptation update parameters."""
        from codomyrmex.cerebrum.core.models import Model
        from codomyrmex.cerebrum.core.transformations import AdaptationTransformer
        t = AdaptationTransformer(adaptation_rate=0.5)
        m = Model(name="test", model_type="cbr", parameters={"weight": 1.0})
        updated = t.update_parameters(m, {"weight": 2.0})
        assert updated is not None
        # The weight should have changed toward 2.0
        assert updated.parameters["weight"] != 1.0


# ===================================================================
# FPF Models
# ===================================================================

@pytest.mark.unit
class TestFPFModels:
    """Test FPF Pydantic models."""

    def test_pattern_status_enum(self):
        """Test functionality: pattern status enum."""
        from codomyrmex.fpf.core.models import PatternStatus
        assert PatternStatus.STABLE == "Stable"
        assert PatternStatus.DRAFT == "Draft"

    def test_relationship_type_enum(self):
        """Test functionality: relationship type enum."""
        from codomyrmex.fpf.core.models import RelationshipType
        assert RelationshipType.BUILDS_ON == "builds_on"
        assert RelationshipType.CONSTRAINS == "constrains"

    def test_concept_type_enum(self):
        """Test functionality: concept type enum."""
        from codomyrmex.fpf.core.models import ConceptType
        assert ConceptType.MECHANISM == "Mechanism"
        assert ConceptType.PRINCIPLE == "Principle"

    def test_pattern_creation(self):
        """Test functionality: pattern creation."""
        from codomyrmex.fpf.core.models import Pattern, PatternStatus
        p = Pattern(id="P1", title="Test Pattern", status=PatternStatus.DRAFT, content="body text")
        assert p.id == "P1"
        assert p.title == "Test Pattern"

    def test_concept_creation(self):
        """Test functionality: concept creation."""
        from codomyrmex.fpf.core.models import Concept, ConceptType
        c = Concept(name="TestConcept", type=ConceptType.TERM, definition="A test concept", pattern_id="P1")
        assert c.name == "TestConcept"

    def test_relationship_creation(self):
        """Test functionality: relationship creation."""
        from codomyrmex.fpf.core.models import Relationship, RelationshipType
        r = Relationship(source="P1", target="P2", type=RelationshipType.BUILDS_ON)
        assert r.source == "P1"
        assert r.target == "P2"

    def test_fpf_spec_creation(self):
        """Test functionality: fpf spec creation."""
        from codomyrmex.fpf.core.models import FPFSpec
        spec = FPFSpec(version="1.0")
        assert spec.version == "1.0"

    def test_fpf_spec_get_pattern_by_id(self):
        """Test functionality: fpf spec get pattern by id."""
        from codomyrmex.fpf.core.models import FPFSpec, Pattern, PatternStatus
        spec = FPFSpec(
            version="1.0",
            patterns=[Pattern(id="P1", title="First", status=PatternStatus.STABLE, content="body")],
        )
        found = spec.get_pattern_by_id("P1")
        assert found is not None
        assert found.title == "First"

    def test_fpf_spec_pattern_not_found(self):
        """Test functionality: fpf spec pattern not found."""
        from codomyrmex.fpf.core.models import FPFSpec
        spec = FPFSpec(version="1.0")
        assert spec.get_pattern_by_id("nonexistent") is None

    def test_fpf_index_creation(self):
        """Test functionality: fpf index creation."""
        from codomyrmex.fpf.core.models import FPFIndex
        idx = FPFIndex()
        assert idx is not None

    def test_fpf_index_search(self):
        """Test functionality: fpf index search."""
        from codomyrmex.fpf.core.models import FPFIndex, Pattern, PatternStatus
        idx = FPFIndex(
            pattern_index={"P1": Pattern(id="P1", title="Cognitive Architecture", status=PatternStatus.STABLE, content="desc")},
        )
        results = idx.search_patterns("cognitive")
        assert len(results) >= 1


# ===================================================================
# Containerization
# ===================================================================

@pytest.mark.unit
class TestContainerConfig:
    """Test ContainerConfig dataclass."""

    def test_creation(self):
        """Test functionality: creation."""
        from codomyrmex.containerization.docker.docker_manager import ContainerConfig
        cfg = ContainerConfig(image_name="python", tag="3.12")
        assert cfg.image_name == "python"
        assert cfg.tag == "3.12"

    def test_get_full_image_name(self):
        """Test functionality: get full image name."""
        from codomyrmex.containerization.docker.docker_manager import ContainerConfig
        cfg = ContainerConfig(image_name="python", tag="3.12-slim")
        assert cfg.get_full_image_name() == "python:3.12-slim"

    def test_defaults(self):
        """Test functionality: defaults."""
        from codomyrmex.containerization.docker.docker_manager import ContainerConfig
        cfg = ContainerConfig(image_name="test")
        assert cfg.tag == "latest"
        assert cfg.restart_policy == "no"
        assert cfg.build_args == {}


@pytest.mark.unit
class TestDockerManagerImport:
    """Test DockerManager can be imported (Docker may not be available)."""

    def test_import(self):
        """Test functionality: import."""
        from codomyrmex.containerization.docker.docker_manager import DockerManager
        assert DockerManager is not None

    def test_optimize_recommendations(self):
        """Test functionality: optimize recommendations."""
        from codomyrmex.containerization.docker.docker_manager import DockerManager
        mgr = DockerManager.__new__(DockerManager)
        # optimize_container_image returns a string recommendation
        result = mgr.optimize_container_image("python:3.12", ["numpy", "pandas"])
        assert isinstance(result, (str, dict))


# ===================================================================
# Git Operations
# ===================================================================

@pytest.mark.unit
class TestGitOperationsImport:
    """Test git_operations module imports."""

    def test_import_module(self):
        """Test functionality: import module."""
        import codomyrmex.git_operations
        assert codomyrmex.git_operations is not None

    def test_mcp_tools_import(self):
        """Test functionality: mcp tools import."""
        from codomyrmex.git_operations import mcp_tools
        # Module exports individual tool functions, not a list
        assert hasattr(mcp_tools, 'git_repo_status')
        assert callable(mcp_tools.git_repo_status)
