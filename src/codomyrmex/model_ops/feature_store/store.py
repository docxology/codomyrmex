"""
Feature Store Backends

Storage backends for feature data.
"""

import threading
from abc import ABC, abstractmethod
from typing import Any

from .models import FeatureDefinition, FeatureValue, FeatureVector


class FeatureStore(ABC):
    """Base class for feature storage backends."""

    @abstractmethod
    def register_feature(self, definition: FeatureDefinition) -> None:
        """Register a feature definition."""
        pass

    @abstractmethod
    def get_feature_definition(self, name: str) -> FeatureDefinition | None:
        """Get feature definition by name."""
        pass

    @abstractmethod
    def set_value(self, feature_name: str, entity_id: str, value: Any) -> None:
        """Set a feature value for an entity."""
        pass

    @abstractmethod
    def get_value(self, feature_name: str, entity_id: str) -> FeatureValue | None:
        """Get a feature value for an entity."""
        pass

    @abstractmethod
    def get_vector(self, entity_id: str, feature_names: list[str]) -> FeatureVector:
        """Get multiple features for an entity."""
        pass


class InMemoryFeatureStore(FeatureStore):
    """
    In-memory feature store for development and testing.

    Usage:
        store = InMemoryFeatureStore()

        # Register features
        store.register_feature(FeatureDefinition(
            name="user_age",
            feature_type=FeatureType.NUMERIC,
            value_type=ValueType.INT,
        ))

        # Set values
        store.set_value("user_age", "user_123", 25)

        # Get values
        value = store.get_value("user_age", "user_123")
        print(value.value)  # 25
    """

    def __init__(self):
        """Initialize this instance."""
        self._definitions: dict[str, FeatureDefinition] = {}
        self._values: dict[str, dict[str, FeatureValue]] = {}  # feature_name -> entity_id -> value
        self._lock = threading.Lock()

    def register_feature(self, definition: FeatureDefinition) -> None:
        """Register a feature definition."""
        with self._lock:
            self._definitions[definition.name] = definition
            if definition.name not in self._values:
                self._values[definition.name] = {}

    def get_feature_definition(self, name: str) -> FeatureDefinition | None:
        """Get feature definition by name."""
        return self._definitions.get(name)

    def set_value(self, feature_name: str, entity_id: str, value: Any) -> None:
        """Set a feature value for an entity."""
        with self._lock:
            if feature_name not in self._values:
                self._values[feature_name] = {}

            existing = self._values[feature_name].get(entity_id)
            version = (existing.version + 1) if existing else 1

            self._values[feature_name][entity_id] = FeatureValue(
                feature_name=feature_name,
                entity_id=entity_id,
                value=value,
                version=version,
            )

    def get_value(self, feature_name: str, entity_id: str) -> FeatureValue | None:
        """Get a feature value for an entity."""
        if feature_name not in self._values:
            return None
        return self._values[feature_name].get(entity_id)

    def get_vector(self, entity_id: str, feature_names: list[str]) -> FeatureVector:
        """Get multiple features for an entity."""
        features = {}
        for name in feature_names:
            value = self.get_value(name, entity_id)
            if value:
                features[name] = value.value
            else:
                # Use default if defined
                definition = self.get_feature_definition(name)
                if definition and definition.default_value is not None:
                    features[name] = definition.default_value

        return FeatureVector(entity_id=entity_id, features=features)

    def list_features(self) -> list[FeatureDefinition]:
        """List all registered features."""
        return list(self._definitions.values())

    def delete_value(self, feature_name: str, entity_id: str) -> bool:
        """Delete a feature value."""
        with self._lock:
            if feature_name in self._values and entity_id in self._values[feature_name]:
                del self._values[feature_name][entity_id]
                return True
        return False
