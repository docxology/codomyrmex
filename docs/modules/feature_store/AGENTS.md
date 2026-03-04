# Feature Store -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides feature management, storage, and serving for ML applications. Defines feature schemas with type validation, supports feature groups and point-in-time retrieval, and includes built-in feature transforms.

## MCP Tools

No MCP tools defined for this module.

## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Register, store, and serve ML features for training and inference |
| OBSERVE | Monitoring Agent | Monitor feature freshness and schema consistency |


## Agent Instructions

1. Register features with FeatureDefinition specifying type, group, and validation constraints
2. Use InMemoryFeatureStore for development; implement FeatureStore interface for production backends


## Navigation

- [Source README](../../src/codomyrmex/feature_store/README.md) | [SPEC.md](SPEC.md)
