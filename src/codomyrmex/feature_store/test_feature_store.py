"""
Tests for Feature Store Module
"""

import pytest
from codomyrmex.feature_store import (
    FeatureType,
    ValueType,
    FeatureDefinition,
    FeatureValue,
    FeatureVector,
    FeatureGroup,
    InMemoryFeatureStore,
    FeatureTransform,
    FeatureService,
)


class TestFeatureDefinition:
    """Tests for FeatureDefinition."""
    
    def test_create(self):
        """Should create feature definition."""
        f = FeatureDefinition(
            name="age",
            feature_type=FeatureType.NUMERIC,
            value_type=ValueType.INT,
        )
        assert f.name == "age"
        assert f.full_name == "age"
    
    def test_to_dict(self):
        """Should convert to dict."""
        f = FeatureDefinition(
            name="city",
            feature_type=FeatureType.CATEGORICAL,
            value_type=ValueType.STRING,
        )
        d = f.to_dict()
        assert d["name"] == "city"
        assert d["feature_type"] == "categorical"


class TestFeatureVector:
    """Tests for FeatureVector."""
    
    def test_get(self):
        """Should get feature value."""
        v = FeatureVector(entity_id="user1", features={"age": 25, "city": "NYC"})
        assert v.get("age") == 25
        assert v.get("missing") is None
        assert v.get("missing", "default") == "default"
    
    def test_to_list(self):
        """Should convert to list."""
        v = FeatureVector(entity_id="user1", features={"a": 1, "b": 2, "c": 3})
        assert v.to_list(["a", "c"]) == [1, 3]


class TestFeatureGroup:
    """Tests for FeatureGroup."""
    
    def test_feature_names(self):
        """Should list feature names."""
        g = FeatureGroup(
            name="user_features",
            features=[
                FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT),
                FeatureDefinition("city", FeatureType.CATEGORICAL, ValueType.STRING),
            ],
        )
        assert g.feature_names == ["age", "city"]
    
    def test_get_feature(self):
        """Should get feature by name."""
        g = FeatureGroup(
            name="test",
            features=[FeatureDefinition("f1", FeatureType.NUMERIC, ValueType.FLOAT)],
        )
        assert g.get_feature("f1").name == "f1"
        assert g.get_feature("missing") is None


class TestInMemoryFeatureStore:
    """Tests for InMemoryFeatureStore."""
    
    def test_register_and_get_definition(self):
        """Should register and retrieve definition."""
        store = InMemoryFeatureStore()
        f = FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT)
        store.register_feature(f)
        
        retrieved = store.get_feature_definition("age")
        assert retrieved.name == "age"
    
    def test_set_and_get_value(self):
        """Should set and get values."""
        store = InMemoryFeatureStore()
        store.set_value("age", "user1", 30)
        
        value = store.get_value("age", "user1")
        assert value.value == 30
        assert value.entity_id == "user1"
    
    def test_get_vector(self):
        """Should get feature vector."""
        store = InMemoryFeatureStore()
        store.set_value("age", "user1", 25)
        store.set_value("score", "user1", 0.95)
        
        vector = store.get_vector("user1", ["age", "score"])
        assert vector.features["age"] == 25
        assert vector.features["score"] == 0.95
    
    def test_version_tracking(self):
        """Should track versions."""
        store = InMemoryFeatureStore()
        store.set_value("age", "user1", 25)
        store.set_value("age", "user1", 26)
        
        value = store.get_value("age", "user1")
        assert value.value == 26
        assert value.version == 2
    
    def test_list_features(self):
        """Should list all features."""
        store = InMemoryFeatureStore()
        store.register_feature(FeatureDefinition("f1", FeatureType.NUMERIC, ValueType.INT))
        store.register_feature(FeatureDefinition("f2", FeatureType.CATEGORICAL, ValueType.STRING))
        
        features = store.list_features()
        assert len(features) == 2


class TestFeatureTransform:
    """Tests for FeatureTransform."""
    
    def test_apply_transform(self):
        """Should apply transform."""
        transform = FeatureTransform()
        transform.add("age", lambda v: v / 100)
        
        vector = FeatureVector(entity_id="user1", features={"age": 50, "name": "test"})
        transformed = transform.apply(vector)
        
        assert transformed.features["age"] == 0.5
        assert transformed.features["name"] == "test"
    
    def test_chain_add(self):
        """Should support chaining."""
        transform = (FeatureTransform()
            .add("a", lambda v: v * 2)
            .add("b", lambda v: v + 1))
        
        vector = FeatureVector(entity_id="e1", features={"a": 5, "b": 10})
        result = transform.apply(vector)
        
        assert result.features["a"] == 10
        assert result.features["b"] == 11


class TestFeatureService:
    """Tests for FeatureService."""
    
    def test_register_group(self):
        """Should register feature group."""
        service = FeatureService()
        group = FeatureGroup(
            name="user_features",
            features=[
                FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT),
            ],
        )
        service.register_group(group)
        
        assert "user_features" in service.list_groups()
    
    def test_ingest(self):
        """Should ingest features."""
        service = FeatureService()
        service.ingest({"age": 30, "score": 0.8}, entity_id="user1")
        
        vector = service.get_features("user1", ["age", "score"])
        assert vector.features["age"] == 30
    
    def test_ingest_batch(self):
        """Should ingest batch."""
        service = FeatureService()
        batch = [
            {"entity_id": "u1", "age": 25},
            {"entity_id": "u2", "age": 30},
        ]
        count = service.ingest_batch(batch)
        
        assert count == 2
        assert service.get_features("u1", ["age"]).features["age"] == 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
