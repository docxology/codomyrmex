"""Unit tests for core CEREBRUM engine."""

import pytest

from codomyrmex.cerebrum import Case, ModelError
from codomyrmex.cerebrum.core import CerebrumEngine, ModelManager


@pytest.mark.unit
class TestModelManager:
    """Test ModelManager class."""

    def test_create_model(self):
        """Test model creation."""
        manager = ModelManager()
        model = manager.create_model("test_model", "case_based")
        assert model.name == "test_model"
        assert model.model_type == "case_based"

    def test_create_duplicate_model(self):
        """Test creating duplicate model."""
        manager = ModelManager()
        manager.create_model("test_model", "case_based")
        with pytest.raises(ModelError):
            manager.create_model("test_model", "case_based")

    def test_get_model(self):
        """Test retrieving model."""
        manager = ModelManager()
        manager.create_model("test_model", "case_based")
        model = manager.get_model("test_model")
        assert model.name == "test_model"

    def test_get_model_not_found(self):
        """Test retrieving non-existent model."""
        manager = ModelManager()
        with pytest.raises(ModelError):
            manager.get_model("nonexistent")


@pytest.mark.unit
class TestCerebrumEngine:
    """Test CerebrumEngine class."""

    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = CerebrumEngine()
        assert engine.case_base is not None
        assert engine.model_manager is not None

    def test_add_case(self):
        """Test adding cases."""
        engine = CerebrumEngine()
        case = Case(case_id="test", features={"x": 1})
        engine.add_case(case)
        assert engine.case_base.size() == 1

    def test_reason(self):
        """Test reasoning."""
        engine = CerebrumEngine()

        # Add cases
        case1 = Case(case_id="case1", features={"x": 1}, outcome="success")
        case2 = Case(case_id="case2", features={"x": 2}, outcome="failure")
        engine.add_case(case1)
        engine.add_case(case2)

        # Query
        query = Case(case_id="query", features={"x": 1.5})
        result = engine.reason(query)

        assert result.prediction is not None
        assert 0 <= result.confidence <= 1

    def test_create_model(self):
        """Test model creation."""
        engine = CerebrumEngine()
        model = engine.create_model("test", "case_based")
        assert model.name == "test"

    def test_learn_from_case(self):
        """Test learning from case."""
        engine = CerebrumEngine()
        case = Case(case_id="test", features={"x": 1})
        engine.learn_from_case(case, "success")

        retrieved = engine.case_base.get_case("test")
        assert retrieved.outcome == "success"


