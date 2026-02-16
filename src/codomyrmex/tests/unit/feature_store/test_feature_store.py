"""Unit tests for feature_store module."""
import pytest


@pytest.mark.unit
class TestFeatureStoreImports:
    """Test suite for feature_store module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex.model_ops import feature_store
        assert feature_store is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.model_ops.feature_store import __all__
        expected_exports = [
            "FeatureType",
            "ValueType",
            "FeatureDefinition",
            "FeatureValue",
            "FeatureVector",
            "FeatureGroup",
            "FeatureStore",
            "InMemoryFeatureStore",
            "FeatureTransform",
            "FeatureService",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestFeatureType:
    """Test suite for FeatureType enum."""

    def test_feature_type_values(self):
        """Verify all feature types are available."""
        from codomyrmex.model_ops.feature_store import FeatureType

        assert FeatureType.NUMERIC.value == "numeric"
        assert FeatureType.CATEGORICAL.value == "categorical"
        assert FeatureType.EMBEDDING.value == "embedding"
        assert FeatureType.TEXT.value == "text"
        assert FeatureType.TIMESTAMP.value == "timestamp"
        assert FeatureType.BOOLEAN.value == "boolean"


@pytest.mark.unit
class TestValueType:
    """Test suite for ValueType enum."""

    def test_value_type_values(self):
        """Verify all value types are available."""
        from codomyrmex.model_ops.feature_store import ValueType

        assert ValueType.INT.value == "int"
        assert ValueType.FLOAT.value == "float"
        assert ValueType.STRING.value == "string"
        assert ValueType.BOOL.value == "bool"
        assert ValueType.LIST.value == "list"
        assert ValueType.DICT.value == "dict"


@pytest.mark.unit
class TestFeatureDefinition:
    """Test suite for FeatureDefinition dataclass."""

    def test_feature_definition_creation(self):
        """Verify FeatureDefinition can be created."""
        from codomyrmex.model_ops.feature_store import FeatureDefinition, FeatureType, ValueType

        feature = FeatureDefinition(
            name="user_age",
            feature_type=FeatureType.NUMERIC,
            value_type=ValueType.INT,
            description="User age in years",
        )

        assert feature.name == "user_age"
        assert feature.feature_type == FeatureType.NUMERIC
        assert feature.value_type == ValueType.INT

    def test_feature_definition_to_dict(self):
        """Verify feature definition serialization."""
        from codomyrmex.model_ops.feature_store import FeatureDefinition, FeatureType, ValueType

        feature = FeatureDefinition(
            name="city",
            feature_type=FeatureType.CATEGORICAL,
            value_type=ValueType.STRING,
            tags=["location", "demographic"],
        )

        result = feature.to_dict()
        assert result["name"] == "city"
        assert result["feature_type"] == "categorical"
        assert "location" in result["tags"]


@pytest.mark.unit
class TestFeatureValue:
    """Test suite for FeatureValue dataclass."""

    def test_feature_value_creation(self):
        """Verify FeatureValue can be created."""
        from codomyrmex.model_ops.feature_store import FeatureValue

        value = FeatureValue(
            feature_name="user_age",
            entity_id="user_123",
            value=25,
        )

        assert value.feature_name == "user_age"
        assert value.entity_id == "user_123"
        assert value.value == 25
        assert value.version == 1

    def test_feature_value_age(self):
        """Verify age calculation."""
        from codomyrmex.model_ops.feature_store import FeatureValue

        value = FeatureValue(
            feature_name="test",
            entity_id="entity_1",
            value=100,
        )

        # Age should be very small since just created
        assert value.age_seconds >= 0


@pytest.mark.unit
class TestFeatureVector:
    """Test suite for FeatureVector dataclass."""

    def test_feature_vector_creation(self):
        """Verify FeatureVector can be created."""
        from codomyrmex.model_ops.feature_store import FeatureVector

        vector = FeatureVector(
            entity_id="user_123",
            features={"age": 25, "city": "NYC", "active": True},
        )

        assert vector.entity_id == "user_123"
        assert vector.features["age"] == 25

    def test_feature_vector_get(self):
        """Verify feature value retrieval."""
        from codomyrmex.model_ops.feature_store import FeatureVector

        vector = FeatureVector(
            entity_id="test",
            features={"score": 0.95},
        )

        assert vector.get("score") == 0.95
        assert vector.get("missing", default=0.0) == 0.0

    def test_feature_vector_to_list(self):
        """Verify conversion to list."""
        from codomyrmex.model_ops.feature_store import FeatureVector

        vector = FeatureVector(
            entity_id="test",
            features={"a": 1, "b": 2, "c": 3},
        )

        result = vector.to_list(["a", "c"])
        assert result == [1, 3]


@pytest.mark.unit
class TestFeatureGroup:
    """Test suite for FeatureGroup dataclass."""

    def test_feature_group_creation(self):
        """Verify FeatureGroup can be created."""
        from codomyrmex.model_ops.feature_store import (
            FeatureDefinition,
            FeatureGroup,
            FeatureType,
            ValueType,
        )

        group = FeatureGroup(
            name="user_features",
            features=[
                FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT),
                FeatureDefinition("city", FeatureType.CATEGORICAL, ValueType.STRING),
            ],
            entity_type="user",
        )

        assert group.name == "user_features"
        assert len(group.features) == 2

    def test_feature_group_feature_names(self):
        """Verify feature names property."""
        from codomyrmex.model_ops.feature_store import (
            FeatureDefinition,
            FeatureGroup,
            FeatureType,
            ValueType,
        )

        group = FeatureGroup(
            name="test",
            features=[
                FeatureDefinition("f1", FeatureType.NUMERIC, ValueType.FLOAT),
                FeatureDefinition("f2", FeatureType.BOOLEAN, ValueType.BOOL),
            ],
        )

        assert group.feature_names == ["f1", "f2"]

    def test_feature_group_get_feature(self):
        """Verify feature retrieval by name."""
        from codomyrmex.model_ops.feature_store import (
            FeatureDefinition,
            FeatureGroup,
            FeatureType,
            ValueType,
        )

        group = FeatureGroup(
            name="test",
            features=[
                FeatureDefinition("target", FeatureType.NUMERIC, ValueType.FLOAT),
            ],
        )

        feature = group.get_feature("target")
        assert feature is not None
        assert feature.name == "target"

        missing = group.get_feature("nonexistent")
        assert missing is None


@pytest.mark.unit
class TestInMemoryFeatureStore:
    """Test suite for InMemoryFeatureStore."""

    def test_store_register_and_get_definition(self):
        """Verify feature registration and retrieval."""
        from codomyrmex.model_ops.feature_store import (
            FeatureDefinition,
            FeatureType,
            InMemoryFeatureStore,
            ValueType,
        )

        store = InMemoryFeatureStore()

        definition = FeatureDefinition(
            name="test_feature",
            feature_type=FeatureType.NUMERIC,
            value_type=ValueType.FLOAT,
        )

        store.register_feature(definition)
        retrieved = store.get_feature_definition("test_feature")

        assert retrieved is not None
        assert retrieved.name == "test_feature"

    def test_store_set_and_get_value(self):
        """Verify value storage and retrieval."""
        from codomyrmex.model_ops.feature_store import InMemoryFeatureStore

        store = InMemoryFeatureStore()

        store.set_value("score", "entity_1", 0.95)
        value = store.get_value("score", "entity_1")

        assert value is not None
        assert value.value == 0.95
        assert value.version == 1

    def test_store_value_versioning(self):
        """Verify value versioning on updates."""
        from codomyrmex.model_ops.feature_store import InMemoryFeatureStore

        store = InMemoryFeatureStore()

        store.set_value("score", "entity_1", 0.8)
        store.set_value("score", "entity_1", 0.9)

        value = store.get_value("score", "entity_1")
        assert value.version == 2
        assert value.value == 0.9

    def test_store_get_vector(self):
        """Verify vector retrieval."""
        from codomyrmex.model_ops.feature_store import InMemoryFeatureStore

        store = InMemoryFeatureStore()

        store.set_value("age", "user_1", 25)
        store.set_value("score", "user_1", 0.95)

        vector = store.get_vector("user_1", ["age", "score"])

        assert vector.entity_id == "user_1"
        assert vector.features["age"] == 25
        assert vector.features["score"] == 0.95

    def test_store_delete_value(self):
        """Verify value deletion."""
        from codomyrmex.model_ops.feature_store import InMemoryFeatureStore

        store = InMemoryFeatureStore()

        store.set_value("test", "entity_1", 100)
        deleted = store.delete_value("test", "entity_1")

        assert deleted is True
        assert store.get_value("test", "entity_1") is None


@pytest.mark.unit
class TestFeatureTransform:
    """Test suite for FeatureTransform."""

    def test_transform_add_and_apply(self):
        """Verify transforms can be added and applied."""
        from codomyrmex.model_ops.feature_store import FeatureTransform, FeatureVector

        transform = FeatureTransform()
        transform.add("age", lambda v: v / 100)  # Normalize
        transform.add("score", lambda v: v * 2)  # Scale

        vector = FeatureVector(
            entity_id="test",
            features={"age": 50, "score": 0.5, "city": "NYC"},
        )

        result = transform.apply(vector)

        assert result.features["age"] == 0.5
        assert result.features["score"] == 1.0
        assert result.features["city"] == "NYC"  # Unchanged


@pytest.mark.unit
class TestFeatureService:
    """Test suite for FeatureService."""

    def test_service_register_and_ingest(self):
        """Verify feature registration and ingestion."""
        from codomyrmex.model_ops.feature_store import (
            FeatureDefinition,
            FeatureService,
            FeatureType,
            ValueType,
        )

        service = FeatureService()

        service.register_feature(FeatureDefinition(
            name="rating",
            feature_type=FeatureType.NUMERIC,
            value_type=ValueType.FLOAT,
        ))

        service.ingest({"rating": 4.5}, entity_id="item_123")

        vector = service.get_features("item_123", ["rating"])
        assert vector.features["rating"] == 4.5

    def test_service_register_group(self):
        """Verify feature group registration."""
        from codomyrmex.model_ops.feature_store import (
            FeatureDefinition,
            FeatureGroup,
            FeatureService,
            FeatureType,
            ValueType,
        )

        service = FeatureService()

        group = FeatureGroup(
            name="user_features",
            features=[
                FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT),
                FeatureDefinition("city", FeatureType.CATEGORICAL, ValueType.STRING),
            ],
        )

        service.register_group(group)

        assert "user_features" in service.list_groups()

    def test_service_ingest_batch(self):
        """Verify batch ingestion."""
        from codomyrmex.model_ops.feature_store import FeatureService

        service = FeatureService()

        batch = [
            {"entity_id": "user_1", "score": 0.8},
            {"entity_id": "user_2", "score": 0.9},
            {"entity_id": "user_3", "score": 0.7},
        ]

        count = service.ingest_batch(batch)
        assert count == 3

        vector = service.get_features("user_2", ["score"])
        assert vector.features["score"] == 0.9
