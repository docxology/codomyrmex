# feature_store

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

ML feature management, storage, and retrieval for machine learning applications. Provides feature registration with type definitions, entity-keyed value storage with versioning, feature grouping, batch ingestion, and pluggable transformation pipelines. Designed for both online (low-latency serving) and offline (batch processing) feature access patterns.

## Key Exports

### Enums

- **`FeatureType`** -- Semantic types for features: NUMERIC, CATEGORICAL, EMBEDDING, TEXT, TIMESTAMP, BOOLEAN
- **`ValueType`** -- Data types for feature values: INT, FLOAT, STRING, BOOL, LIST, DICT

### Data Classes

- **`FeatureDefinition`** -- Definition of a feature including name, type, value type, description, default value, tags, and metadata
- **`FeatureValue`** -- A stored feature value for a specific entity with timestamp and version tracking; includes `age_seconds` property
- **`FeatureVector`** -- A collection of feature values for an entity; supports dictionary access via `get()` and ordered list conversion via `to_list()`
- **`FeatureGroup`** -- A named group of related feature definitions with entity type and tag support; provides `feature_names` listing and lookup by name

### Storage

- **`FeatureStore`** -- Abstract base class for feature storage backends with register, set, get, and vector retrieval methods
- **`InMemoryFeatureStore`** -- Thread-safe in-memory implementation with auto-versioning on value updates, feature listing, and deletion support

### Transforms

- **`FeatureTransform`** -- Applies registered per-feature transformation functions to feature vectors; supports method chaining for adding transforms

### Services

- **`FeatureService`** -- High-level feature service for ML applications; manages feature groups, supports single and batch ingestion, retrieves feature vectors with optional transforms, and serves features by group name

### Constants

- **`USER_ID_FEATURE`** -- Pre-defined categorical feature definition for user identifiers
- **`TIMESTAMP_FEATURE`** -- Pre-defined timestamp feature definition for event timestamps

## Directory Contents

- `__init__.py` -- Module implementation with store, service, transform, and data models
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Navigation

- **Full Documentation**: [docs/modules/feature_store/](../../../docs/modules/feature_store/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
