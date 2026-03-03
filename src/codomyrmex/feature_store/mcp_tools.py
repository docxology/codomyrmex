"""Feature Store MCP Tools.

Model Context Protocol tools for managing ML features.
"""

from typing import Any

from codomyrmex.feature_store.exceptions import (
    FeatureNotFoundError,
    FeatureValidationError,
)
from codomyrmex.feature_store.models import (
    FeatureDefinition,
    FeatureGroup,
    FeatureType,
    ValueType,
)
from codomyrmex.feature_store.service import FeatureService
from codomyrmex.feature_store.store import InMemoryFeatureStore
from codomyrmex.model_context_protocol.decorators import mcp_tool

# Global service instance for MCP tools
_store = InMemoryFeatureStore()
_service = FeatureService(store=_store)

# Pre-populate some basic feature types for demonstration
_service.register_feature(FeatureDefinition("user_age", FeatureType.NUMERIC, ValueType.INT, "User age in years"))
_service.register_feature(FeatureDefinition("user_segment", FeatureType.CATEGORICAL, ValueType.STRING, "User marketing segment"))
_service.register_feature(FeatureDefinition("is_active", FeatureType.BOOLEAN, ValueType.BOOL, "Whether user is active"))

_user_features = FeatureGroup(
    name="user_profile",
    features=[
        _store.get_feature_definition("user_age"),
        _store.get_feature_definition("user_segment"),
        _store.get_feature_definition("is_active"),
    ],
    entity_type="user"
)
_service.register_group(_user_features)


@mcp_tool(
    name="fs_list_groups",
    category="Feature Store",
    description="List all registered feature groups."
)
def fs_list_groups() -> list[str]:
    """List all registered feature groups."""
    return _service.list_groups()


@mcp_tool(
    name="fs_list_features",
    category="Feature Store",
    description="List all registered features, optionally filtered by a specific group."
)
def fs_list_features(group_name: str | None = None) -> list[dict[str, Any]]:
    """
    List all registered features.

    Args:
        group_name: Optional group name to filter features.

    Returns:
        List of feature definition dictionaries.
    """
    if group_name:
        group = _service._groups.get(group_name)
        if not group:
            return []
        return [f.to_dict() for f in group.features]

    return [f.to_dict() for f in _service.store.list_features()]


@mcp_tool(
    name="fs_get_features",
    category="Feature Store",
    description="Get feature values for a specific entity."
)
def fs_get_features(
    entity_id: str,
    feature_names: list[str] | None = None,
    group_name: str | None = None,
) -> dict[str, Any]:
    """
    Get feature values for an entity.

    Args:
        entity_id: The ID of the entity.
        feature_names: Optional list of specific feature names to retrieve.
        group_name: Optional group name to retrieve all features for that group.

    Returns:
        Dictionary mapping feature names to values.
    """
    if group_name:
        vector = _service.get_group_features(entity_id, group_name)
    elif feature_names:
        vector = _service.get_features(entity_id, feature_names)
    else:
        # If neither is provided, try to return all registered features
        all_features = [f.name for f in _service.store.list_features()]
        vector = _service.get_features(entity_id, all_features)

    return vector.features


@mcp_tool(
    name="fs_ingest_features",
    category="Feature Store",
    description="Ingest feature values for a specific entity."
)
def fs_ingest_features(entity_id: str, features: dict[str, Any]) -> str:
    """
    Ingest feature values for an entity.

    Args:
        entity_id: The ID of the entity.
        features: Dictionary mapping feature names to values.

    Returns:
        Success message or error.
    """
    try:
        _service.ingest(features, entity_id)
        return f"Successfully ingested {len(features)} features for entity '{entity_id}'."
    except FeatureNotFoundError as e:
        return f"Error: Feature not found - {str(e)}"
    except FeatureValidationError as e:
        return f"Error: Validation failed - {str(e)}"
    except Exception as e:
        return f"Error ingesting features: {str(e)}"
