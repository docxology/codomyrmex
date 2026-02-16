"""
Feature Store Models

Data classes and enums for feature management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        """Get fully qualified name."""
        return self.name

    def to_dict(self) -> dict[str, Any]:
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
    features: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, feature_name: str, default: Any = None) -> Any:
        """Get a feature value."""
        return self.features.get(feature_name, default)

    def to_list(self, feature_names: list[str]) -> list[Any]:
        """Convert to list in specified order."""
        return [self.features.get(name) for name in feature_names]


@dataclass
class FeatureGroup:
    """A group of related features."""
    name: str
    features: list[FeatureDefinition]
    description: str = ""
    entity_type: str = "default"
    tags: list[str] = field(default_factory=list)

    @property
    def feature_names(self) -> list[str]:
        """Get list of feature names."""
        return [f.name for f in self.features]

    def get_feature(self, name: str) -> FeatureDefinition | None:
        """Get feature by name."""
        for f in self.features:
            if f.name == name:
                return f
        return None


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
