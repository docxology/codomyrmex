"""
Feature Service

High-level feature service including transforms and batch operations.
"""

from typing import Any
from collections.abc import Callable

from .models import FeatureDefinition, FeatureGroup, FeatureVector
from .store import FeatureStore, InMemoryFeatureStore


class FeatureTransform:
    """
    Transform features before serving.

    Usage:
        transform = FeatureTransform()
        transform.add("age", lambda v: v / 100)  # Normalize
        transform.add("income", lambda v: math.log(v + 1))  # Log transform

        transformed = transform.apply(vector)
    """

    def __init__(self):
        """Execute   Init   operations natively."""
        self._transforms: dict[str, Callable[[Any], Any]] = {}

    def add(self, feature_name: str, func: Callable[[Any], Any]) -> "FeatureTransform":
        """Add a transform for a feature."""
        self._transforms[feature_name] = func
        return self

    def apply(self, vector: FeatureVector) -> FeatureVector:
        """Apply transforms to a feature vector."""
        transformed = {}
        for name, value in vector.features.items():
            if name in self._transforms and value is not None:
                transformed[name] = self._transforms[name](value)
            else:
                transformed[name] = value

        return FeatureVector(
            entity_id=vector.entity_id,
            features=transformed,
            timestamp=vector.timestamp,
            metadata=vector.metadata,
        )


class FeatureService:
    """
    High-level feature service for ML applications.

    Usage:
        service = FeatureService(store=InMemoryFeatureStore())

        # Register feature group
        user_features = FeatureGroup(
            name="user_features",
            features=[
                FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT),
                FeatureDefinition("city", FeatureType.CATEGORICAL, ValueType.STRING),
            ],
        )
        service.register_group(user_features)

        # Ingest features
        service.ingest({"age": 25, "city": "NYC"}, entity_id="user_123")

        # Get features for inference
        vector = service.get_features("user_123", ["age", "city"])
    """

    def __init__(
        self,
        store: FeatureStore | None = None,
        transform: FeatureTransform | None = None,
    ):
        """Execute   Init   operations natively."""
        self.store = store or InMemoryFeatureStore()
        self.transform = transform
        self._groups: dict[str, FeatureGroup] = {}

    def register_group(self, group: FeatureGroup) -> None:
        """Register a feature group."""
        self._groups[group.name] = group
        for feature in group.features:
            self.store.register_feature(feature)

    def register_feature(self, definition: FeatureDefinition) -> None:
        """Register a single feature."""
        self.store.register_feature(definition)

    def ingest(
        self,
        features: dict[str, Any],
        entity_id: str,
    ) -> None:
        """Ingest feature values for an entity."""
        for name, value in features.items():
            self.store.set_value(name, entity_id, value)

    def ingest_batch(
        self,
        batch: list[dict[str, Any]],
        entity_id_field: str = "entity_id",
    ) -> int:
        """Ingest batch of feature values."""
        count = 0
        for record in batch:
            entity_id = record.get(entity_id_field)
            if entity_id:
                features = {k: v for k, v in record.items() if k != entity_id_field}
                self.ingest(features, entity_id)
                count += 1
        return count

    def get_features(
        self,
        entity_id: str,
        feature_names: list[str],
        apply_transform: bool = True,
    ) -> FeatureVector:
        """Get features for an entity."""
        vector = self.store.get_vector(entity_id, feature_names)

        if apply_transform and self.transform:
            vector = self.transform.apply(vector)

        return vector

    def get_group_features(
        self,
        entity_id: str,
        group_name: str,
    ) -> FeatureVector:
        """Get all features in a group for an entity."""
        group = self._groups.get(group_name)
        if not group:
            return FeatureVector(entity_id=entity_id, features={})

        return self.get_features(entity_id, group.feature_names)

    def list_groups(self) -> list[str]:
        """List registered feature groups."""
        return list(self._groups.keys())
