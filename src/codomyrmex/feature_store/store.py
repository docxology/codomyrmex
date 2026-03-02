"""
Feature Store Backends

Storage backends for feature data.
"""

import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import FeatureDefinition, FeatureValue, FeatureVector
from .exceptions import FeatureNotFoundError, FeatureRegistrationError, FeatureValidationError


class FeatureStore(ABC):
    """Base class for feature storage backends."""

    @abstractmethod
    def register_feature(self, definition: FeatureDefinition) -> None:
        """Register a feature definition."""
        pass

    @abstractmethod
    def get_feature_definition(self, name: str) -> Optional[FeatureDefinition]:
        """Get feature definition by name."""
        pass

    @abstractmethod
    def set_value(self, feature_name: str, entity_id: str, value: Any) -> None:
        """Set a feature value for an entity."""
        pass

    @abstractmethod
    def get_value(self, feature_name: str, entity_id: str) -> Optional[FeatureValue]:
        """Get a feature value for an entity."""
        pass

    @abstractmethod
    def get_vector(self, entity_id: str, feature_names: List[str]) -> FeatureVector:
        """Get multiple features for an entity."""
        pass

    @abstractmethod
    def list_features(self) -> List[FeatureDefinition]:
        """List all registered features."""
        pass

    @abstractmethod
    def delete_value(self, feature_name: str, entity_id: str) -> bool:
        """Delete a feature value."""
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
        self._definitions: Dict[str, FeatureDefinition] = {}
        self._values: Dict[str, Dict[str, FeatureValue]] = {}  # feature_name -> entity_id -> value
        self._lock = threading.Lock()

    def register_feature(self, definition: FeatureDefinition) -> None:
        """
        Register a feature definition.
        
        Args:
            definition: The feature definition to register.
            
        Raises:
            FeatureRegistrationError: If definition is invalid.
        """
        if not definition or not definition.name:
            raise FeatureRegistrationError("Invalid feature definition: name is required")
            
        with self._lock:
            self._definitions[definition.name] = definition
            if definition.name not in self._values:
                self._values[definition.name] = {}

    def get_feature_definition(self, name: str) -> Optional[FeatureDefinition]:
        """Get feature definition by name."""
        return self._definitions.get(name)

    def set_value(self, feature_name: str, entity_id: str, value: Any) -> None:
        """
        Set a feature value for an entity.
        
        Args:
            feature_name: Name of the feature.
            entity_id: ID of the entity.
            value: Feature value.
            
        Raises:
            FeatureNotFoundError: If feature is not registered.
            FeatureValidationError: If value does not match feature definition.
        """
        definition = self.get_feature_definition(feature_name)
        if not definition:
            raise FeatureNotFoundError(f"Feature '{feature_name}' not registered")
            
        if not definition.validate_value(value):
            raise FeatureValidationError(
                f"Value {value} is not valid for feature '{feature_name}' (type: {definition.value_type.value})"
            )

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

    def get_value(self, feature_name: str, entity_id: str) -> Optional[FeatureValue]:
        """Get a feature value for an entity."""
        if feature_name not in self._values:
            return None
        return self._values[feature_name].get(entity_id)

    def get_vector(self, entity_id: str, feature_names: List[str]) -> FeatureVector:
        """
        Get multiple features for an entity.
        
        Args:
            entity_id: ID of the entity.
            feature_names: List of feature names to retrieve.
            
        Returns:
            FeatureVector containing the requested features.
        """
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

    def list_features(self) -> List[FeatureDefinition]:
        """List all registered features."""
        return list(self._definitions.values())

    def delete_value(self, feature_name: str, entity_id: str) -> bool:
        """Delete a feature value."""
        with self._lock:
            if feature_name in self._values and entity_id in self._values[feature_name]:
                del self._values[feature_name][entity_id]
                return True
        return False
