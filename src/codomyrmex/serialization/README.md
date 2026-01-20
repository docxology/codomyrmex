# serialization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

The `serialization` module provides a unified framework for data transformation and persistence. It supports multiple formats (JSON, YAML, Msgpack, Avro, Parquet) and handles complex object graphs with circular references.

## Key Features

- **Multi-Format Support**: Unified interface for text and binary serialization formats.
- **Binary Efficiency**: High-performance serialization using Msgpack, Avro, and Parquet.
- **Manager Orchestration**: `SerializationManager` for managing multiple serializers and formats.
- **Deep Serialization**: Support for complex Python objects, including recursive references.

## Module Structure

- `serializer.py` – Abstract base class and core contract definitions.
- `binary_formats.py` – Implementations for Msgpack, Avro, and Parquet.
- `serialization_manager.py` – Global registry and orchestration of serializers.

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
