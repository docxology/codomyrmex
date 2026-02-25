"""Tests for the CEREBRUM module.

Tests cover:
- Module imports
- Case creation and management
- CaseBase operations (add, retrieve, similarity)
- ModelManager CRUD operations
- CerebrumEngine orchestration
- CerebrumConfig defaults and serialization
- Utility functions (hash, normalize, euclidean, cosine, softmax)
- TransformationManager and transformers
- ReasoningResult structure
"""

import pytest

from codomyrmex import cerebrum
from codomyrmex.cerebrum import (
    AdaptationTransformer,
    Case,
    CaseBase,
    CerebrumConfig,
    CerebrumEngine,
    LearningTransformer,
    Model,
    ModelManager,
    ReasoningResult,
    TransformationManager,
    compute_cosine_similarity,
    compute_euclidean_distance,
    compute_hash,
    normalize_features,
    softmax,
)
from codomyrmex.cerebrum.core.exceptions import (
    CaseNotFoundError,
    InvalidCaseError,
    ModelError,
)


@pytest.mark.unit
def test_cerebrum_module_import():
    """Verify that the cerebrum module can be imported successfully."""
    assert cerebrum is not None
    assert hasattr(cerebrum, "__path__")


@pytest.mark.unit
def test_cerebrum_module_structure():
    """Verify basic structure of cerebrum module."""
    assert hasattr(cerebrum, "__file__")


# --- Case Tests ---


@pytest.mark.unit
def test_case_creation():
    """Case can be created with required fields."""
    case = Case(case_id="c1", features={"x": 1.0, "y": 2.0})
    assert case.case_id == "c1"
    assert case.features == {"x": 1.0, "y": 2.0}
    assert case.outcome is None
    assert case.context == {}


@pytest.mark.unit
def test_case_empty_id_raises():
    """Case with empty ID raises InvalidCaseError."""
    with pytest.raises(InvalidCaseError):
        Case(case_id="", features={"x": 1})


@pytest.mark.unit
def test_case_empty_features_raises():
    """Case with empty features raises InvalidCaseError."""
    with pytest.raises(InvalidCaseError):
        Case(case_id="c1", features={})


@pytest.mark.unit
def test_case_serialization_roundtrip():
    """Case can be serialized to dict and reconstructed."""
    original = Case(case_id="c2", features={"a": 10}, outcome="win", metadata={"tag": "test"})
    data = original.to_dict()
    restored = Case.from_dict(data)
    assert restored.case_id == original.case_id
    assert restored.features == original.features
    assert restored.outcome == original.outcome
    assert restored.metadata == original.metadata


# --- CaseBase Tests ---


@pytest.mark.unit
def test_case_base_add_and_retrieve():
    """CaseBase stores cases and retrieves them by ID."""
    cb = CaseBase()
    case = Case(case_id="c1", features={"x": 1.0})
    cb.add_case(case)
    assert cb.size() == 1
    retrieved = cb.get_case("c1")
    assert retrieved.case_id == "c1"


@pytest.mark.unit
def test_case_base_not_found_raises():
    """CaseBase raises CaseNotFoundError for missing ID."""
    cb = CaseBase()
    with pytest.raises(CaseNotFoundError):
        cb.get_case("nonexistent")


@pytest.mark.unit
def test_case_base_similarity_search():
    """CaseBase retrieves similar cases sorted by similarity."""
    cb = CaseBase(similarity_metric="euclidean")
    cb.add_case(Case(case_id="c1", features={"x": 1.0, "y": 1.0}))
    cb.add_case(Case(case_id="c2", features={"x": 2.0, "y": 2.0}))
    cb.add_case(Case(case_id="c3", features={"x": 100.0, "y": 100.0}))

    query = Case(case_id="q", features={"x": 1.5, "y": 1.5})
    results = cb.retrieve_similar(query, k=2)
    assert len(results) == 2
    # c1 and c2 should be more similar to query than c3
    result_ids = [case.case_id for case, _ in results]
    assert "c3" not in result_ids


# --- ModelManager Tests ---


@pytest.mark.unit
def test_model_manager_create_and_get():
    """ModelManager creates and retrieves models by name."""
    mm = ModelManager()
    model = mm.create_model("m1", "bayesian", {"param": 42})
    assert model.name == "m1"
    assert model.model_type == "bayesian"
    retrieved = mm.get_model("m1")
    assert retrieved is model


@pytest.mark.unit
def test_model_manager_duplicate_raises():
    """ModelManager raises ModelError when creating a duplicate model."""
    mm = ModelManager()
    mm.create_model("m1", "bayesian")
    with pytest.raises(ModelError):
        mm.create_model("m1", "bayesian")


@pytest.mark.unit
def test_model_manager_remove_and_list():
    """ModelManager removes models and lists remaining."""
    mm = ModelManager()
    mm.create_model("m1", "type_a")
    mm.create_model("m2", "type_b")
    assert set(mm.list_models()) == {"m1", "m2"}
    mm.remove_model("m1")
    assert mm.list_models() == ["m2"]


# --- CerebrumConfig Tests ---


@pytest.mark.unit
def test_config_defaults():
    """CerebrumConfig has sensible defaults."""
    config = CerebrumConfig()
    assert config.case_similarity_threshold == 0.7
    assert config.max_retrieved_cases == 10
    assert config.learning_rate == 0.01
    assert config.inference_method == "variable_elimination"


@pytest.mark.unit
def test_config_serialization():
    """CerebrumConfig serializes to dict and back."""
    config = CerebrumConfig(learning_rate=0.05, debug_mode=True)
    d = config.to_dict()
    assert d["learning_rate"] == 0.05
    assert d["debug_mode"] is True


# --- CerebrumEngine Tests ---


@pytest.mark.unit
def test_engine_initialization():
    """CerebrumEngine initializes with default config and empty state."""
    engine = CerebrumEngine()
    assert engine.case_base is not None
    assert engine.model_manager is not None
    assert engine.case_base.size() == 0


@pytest.mark.unit
def test_engine_add_case_and_reason():
    """CerebrumEngine adds cases and performs reasoning."""
    engine = CerebrumEngine()
    c1 = Case(case_id="train1", features={"x": 1.0, "y": 2.0}, outcome=10.0)
    c2 = Case(case_id="train2", features={"x": 1.5, "y": 2.5}, outcome=12.0)
    engine.add_case(c1)
    engine.add_case(c2)
    assert engine.case_base.size() == 2

    query = Case(case_id="q", features={"x": 1.2, "y": 2.2})
    result = engine.reason(query)
    assert isinstance(result, ReasoningResult)
    assert result.confidence >= 0.0


# --- Utility Function Tests ---


@pytest.mark.unit
def test_compute_hash_deterministic():
    """compute_hash returns consistent output for same input."""
    h1 = compute_hash({"key": "value"})
    h2 = compute_hash({"key": "value"})
    assert h1 == h2
    assert isinstance(h1, str)
    assert len(h1) == 64  # SHA-256 hex length


@pytest.mark.unit
def test_normalize_features_numeric():
    """normalize_features maps numeric values to (-1, 1) range using v/(1+|v|)."""
    result = normalize_features({"a": 5.0, "b": -3.0})
    # v / (1 + |v|): 5/(1+5)=0.833, -3/(1+3)=-0.75
    assert 0.0 < result["a"] < 1.0
    assert -1.0 < result["b"] < 0.0


@pytest.mark.unit
def test_euclidean_distance_identical():
    """Euclidean distance between identical vectors is 0."""
    vec = {"a": 1.0, "b": 2.0}
    assert compute_euclidean_distance(vec, vec) == 0.0


@pytest.mark.unit
def test_cosine_similarity_same_direction():
    """Cosine similarity of a vector with itself is high."""
    vec = {"a": 3.0, "b": 4.0}
    sim = compute_cosine_similarity(vec, vec)
    assert sim > 0.9


@pytest.mark.unit
def test_softmax_sums_to_one():
    """Softmax output sums to approximately 1."""
    probs = softmax([1.0, 2.0, 3.0])
    assert abs(sum(probs) - 1.0) < 1e-6


@pytest.mark.unit
def test_softmax_empty():
    """Softmax of empty list returns empty list."""
    assert softmax([]) == []


# --- TransformationManager Tests ---


@pytest.mark.unit
def test_transformation_manager_register_and_transform():
    """TransformationManager dispatches to registered transformers."""
    tm = TransformationManager()
    tm.register_transformer("adaptation", AdaptationTransformer(adaptation_rate=0.2))
    model = Model(name="test_model", model_type="cognitive", parameters={"feature_x": 5.0})
    case = Case(case_id="adapt_case", features={"x": 10.0})
    adapted = tm.transform(model, "adapt_to_case", transformer_name="adaptation", case=case)
    assert adapted.name == "test_model_adapted"


@pytest.mark.unit
def test_learning_transformer_feedback():
    """LearningTransformer updates model from feedback."""
    lt = LearningTransformer(learning_rate=0.1)
    model = Model(name="learn_model", model_type="nn", parameters={"weight": 1.0})
    learned = lt.learn_from_feedback(model, {"error": 0.5})
    assert learned.name == "learn_model_learned"
    assert learned.parameters["weight"] != model.parameters["weight"]
