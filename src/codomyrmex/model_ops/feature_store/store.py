"""Feature Store Backends — re-exports from canonical feature_store module."""

from codomyrmex.feature_store.store import FeatureStore, InMemoryFeatureStore

__all__ = ["FeatureStore", "InMemoryFeatureStore"]
