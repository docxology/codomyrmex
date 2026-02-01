"""
Feature Store Module

ML feature management, storage, and retrieval.
"""

__version__ = "0.1.0"

import hashlib
import json
import time
from typing import Optional, List, Dict, Any, Callable, TypeVar, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import threading


T = TypeVar('T')


class FeatureType(Enum):
    """Types of features."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    EMBEDDING = "embedding"
    TEXT = "text"
    TIMESTAMP = "timestamp"
    BOOLEAN = "boolean"


class ValueType(Enum):
    """Data types for feature values."""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"


@dataclass
class FeatureDefinition:
    """Definition of a feature."""
    name: str
    feature_type: FeatureType
    value_type: ValueType
    description: str = ""
    default_value: Any = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def full_name(self) -> str:
        """Get fully qualified name."""
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "feature_type": self.feature_type.value,
            "value_type": self.value_type.value,
            "description": self.description,
            "default_value": self.default_value,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class FeatureValue:
    """A feature value with metadata."""
    feature_name: str
    entity_id: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    @property
    def age_seconds(self) -> float:
        """Get age of this value in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class FeatureVector:
    """A collection of feature values for an entity."""
    entity_id: str
    features: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, feature_name: str, default: Any = None) -> Any:
        """Get a feature value."""
        return self.features.get(feature_name, default)
    
    def to_list(self, feature_names: List[str]) -> List[Any]:
        """Convert to list in specified order."""
        return [self.features.get(name) for name in feature_names]


@dataclass
class FeatureGroup:
    """A group of related features."""
    name: str
    features: List[FeatureDefinition]
    description: str = ""
    entity_type: str = "default"
    tags: List[str] = field(default_factory=list)
    
    @property
    def feature_names(self) -> List[str]:
        """Get list of feature names."""
        return [f.name for f in self.features]
    
    def get_feature(self, name: str) -> Optional[FeatureDefinition]:
        """Get feature by name."""
        for f in self.features:
            if f.name == name:
                return f
        return None


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
        """Register a feature definition."""
        with self._lock:
            self._definitions[definition.name] = definition
            if definition.name not in self._values:
                self._values[definition.name] = {}
    
    def get_feature_definition(self, name: str) -> Optional[FeatureDefinition]:
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
    
    def get_value(self, feature_name: str, entity_id: str) -> Optional[FeatureValue]:
        """Get a feature value for an entity."""
        if feature_name not in self._values:
            return None
        return self._values[feature_name].get(entity_id)
    
    def get_vector(self, entity_id: str, feature_names: List[str]) -> FeatureVector:
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
        self._transforms: Dict[str, Callable[[Any], Any]] = {}
    
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
        store: Optional[FeatureStore] = None,
        transform: Optional[FeatureTransform] = None,
    ):
        self.store = store or InMemoryFeatureStore()
        self.transform = transform
        self._groups: Dict[str, FeatureGroup] = {}
    
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
        features: Dict[str, Any],
        entity_id: str,
    ) -> None:
        """Ingest feature values for an entity."""
        for name, value in features.items():
            self.store.set_value(name, entity_id, value)
    
    def ingest_batch(
        self,
        batch: List[Dict[str, Any]],
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
        feature_names: List[str],
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
    
    def list_groups(self) -> List[str]:
        """List registered feature groups."""
        return list(self._groups.keys())


# Common feature definitions
USER_ID_FEATURE = FeatureDefinition(
    name="user_id",
    feature_type=FeatureType.CATEGORICAL,
    value_type=ValueType.STRING,
    description="User identifier",
)

TIMESTAMP_FEATURE = FeatureDefinition(
    name="event_timestamp",
    feature_type=FeatureType.TIMESTAMP,
    value_type=ValueType.STRING,
    description="Event timestamp",
)


__all__ = [
    # Enums
    "FeatureType",
    "ValueType",
    # Data classes
    "FeatureDefinition",
    "FeatureValue",
    "FeatureVector",
    "FeatureGroup",
    # Stores
    "FeatureStore",
    "InMemoryFeatureStore",
    # Transforms
    "FeatureTransform",
    # Service
    "FeatureService",
    # Common features
    "USER_ID_FEATURE",
    "TIMESTAMP_FEATURE",
]
