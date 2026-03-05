"""
MCP Tools for Feature Store.

Provides Model Context Protocol tools for feature store operations.
"""

from collections.abc import Callable
from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .models import FeatureDefinition, FeatureType, ValueType
from .service import FeatureService
from .store import InMemoryFeatureStore

# Global singleton service for MCP tool persistence within the process
_STORE = InMemoryFeatureStore()
_SERVICE = FeatureService(store=_STORE)

# Type → Python type mapping for validation
_VALUE_TYPE_MAP: dict[str, type] = {
    "int": int,
    "float": float,
    "string": str,
    "bool": bool,
    "list": list,
    "dict": dict,
}


def _get_feature_type(type_str: str) -> FeatureType:
    try:
        return FeatureType(type_str.lower())
    except ValueError as e:
        valid = [t.value for t in FeatureType]
        raise ValueError(
            f"Invalid feature type '{type_str}'. Must be one of {valid}"
        ) from e


def _get_value_type(type_str: str) -> ValueType:
    try:
        return ValueType(type_str.lower())
    except ValueError as e:
        valid = [t.value for t in ValueType]
        raise ValueError(
            f"Invalid value type '{type_str}'. Must be one of {valid}"
        ) from e


@mcp_tool(
    category="feature_store",
    description="List all available FeatureType and ValueType enum values.",
)
def feature_store_list_types() -> dict[str, Any]:
    """Return all supported feature types and value types."""
    return {
        "status": "success",
        "feature_types": [t.value for t in FeatureType],
        "value_types": [t.value for t in ValueType],
    }


@mcp_tool(
    category="feature_store",
    description="Register a new feature definition in the feature store.",
)
def feature_store_register_feature(
    name: str,
    feature_type: str,
    value_type: str,
    description: str = "",
    default_value: Any = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Register a new feature definition in the feature store.

    Args:
        name: The name of the feature.
        feature_type: Type of feature (numeric, categorical, embedding, text, timestamp, boolean).
        value_type: Type of the feature value (int, float, string, bool, list, dict).
        description: A brief description of the feature.
        default_value: Optional default value.
        tags: Optional list of tags.
    """
    try:
        ft = _get_feature_type(feature_type)
        vt = _get_value_type(value_type)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    definition = FeatureDefinition(
        name=name,
        feature_type=ft,
        value_type=vt,
        description=description,
        default_value=default_value,
        tags=tags or [],
    )
    _SERVICE.register_feature(definition)

    return {
        "status": "success",
        "message": f"Feature '{name}' registered successfully.",
        "feature": definition.to_dict(),
    }


@mcp_tool(
    category="feature_store",
    description="Validate a value against a named ValueType.",
)
def feature_store_validate_value(
    value: Any,
    value_type: str,
) -> dict[str, Any]:
    """Validate that *value* conforms to *value_type*.

    Args:
        value: The value to validate (None is always valid — represents missing).
        value_type: One of int, float, string, bool, list, dict.
    """
    try:
        _get_value_type(value_type)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    if value is None:
        return {
            "status": "success",
            "valid": True,
            "reason": "null values are always valid",
        }

    expected_type = _VALUE_TYPE_MAP.get(value_type.lower())
    if expected_type is None:
        return {"status": "error", "message": f"Unsupported value_type '{value_type}'"}

    is_valid = isinstance(value, expected_type)
    return {
        "status": "success",
        "valid": is_valid,
        "reason": None
        if is_valid
        else f"Expected {expected_type.__name__}, got {type(value).__name__}",
    }


@mcp_tool(
    category="feature_store",
    description="Ingest feature values for a specific entity into the feature store.",
)
def feature_store_ingest(
    entity_id: str,
    features: dict[str, Any],
) -> dict[str, Any]:
    """
    Ingest feature values for a specific entity into the feature store.

    Args:
        entity_id: The ID of the entity (e.g., user_123).
        features: A dictionary mapping feature names to their values.
    """
    _SERVICE.ingest(features=features, entity_id=entity_id)
    return {
        "status": "success",
        "message": f"Successfully ingested features for entity '{entity_id}'.",
        "features": features,
    }


@mcp_tool(
    category="feature_store",
    description="Retrieve feature values for an entity from the feature store.",
)
def feature_store_get_features(
    entity_id: str,
    feature_names: list[str],
) -> dict[str, Any]:
    """
    Retrieve feature values for an entity from the feature store.

    Args:
        entity_id: The ID of the entity.
        feature_names: A list of feature names to retrieve.
    """
    vector = _SERVICE.get_features(
        entity_id=entity_id, feature_names=feature_names, apply_transform=True
    )
    return {
        "status": "success",
        "entity_id": vector.entity_id,
        "features": vector.features,
        "timestamp": vector.timestamp.isoformat(),
    }


def get_mcp_tools() -> list[Callable[..., Any]]:
    """Return a list of all MCP tools defined in this module."""
    return [
        feature_store_list_types,
        feature_store_register_feature,
        feature_store_validate_value,
        feature_store_ingest,
        feature_store_get_features,
    ]
