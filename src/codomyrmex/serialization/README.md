# serialization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Unified data serialization and deserialization module supporting multiple formats including JSON, YAML, TOML, MessagePack, Avro, and Parquet. Provides both a low-level `Serializer` class with format-specific encoding and a higher-level `SerializationManager` for managing serialization workflows. Includes comprehensive error handling with typed exceptions for schema validation, encoding, circular references, and format compatibility issues.

## Key Exports

### Core Classes

- **`Serializer`** -- Low-level serializer that converts objects to/from bytes in a specified format
- **`SerializationManager`** -- Higher-level manager for coordinating serialization workflows
- **`SerializationFormat`** -- Enum of supported serialization formats (json, yaml, toml, msgpack, etc.)

### Binary Format Serializers

- **`MsgpackSerializer`** -- MessagePack binary serialization for compact, fast encoding
- **`AvroSerializer`** -- Apache Avro serialization with schema support
- **`ParquetSerializer`** -- Apache Parquet columnar format serialization

### Convenience Functions

- **`serialize()`** -- Serialize an object to bytes in a given format (defaults to JSON)
- **`deserialize()`** -- Deserialize bytes back to an object in a given format (defaults to JSON)

### Exceptions

- **`SerializationError`** -- Base exception for serialization failures
- **`DeserializationError`** -- Error during deserialization of data
- **`SchemaValidationError`** -- Data does not conform to expected schema
- **`EncodingError`** -- Character encoding or binary encoding issues
- **`FormatNotSupportedError`** -- Requested format is not available
- **`CircularReferenceError`** -- Circular reference detected during serialization
- **`TypeConversionError`** -- Type cannot be converted to target format
- **`BinaryFormatError`** -- Error specific to binary format operations

## Directory Contents

- `__init__.py` - Module entry point with convenience serialize/deserialize functions
- `serializer.py` - Core `Serializer` class and `SerializationFormat` enum
- `serialization_manager.py` - `SerializationManager` for workflow-level serialization
- `binary_formats.py` - MsgpackSerializer, AvroSerializer, and ParquetSerializer implementations
- `exceptions.py` - Full exception hierarchy for serialization errors

## Navigation

- **Full Documentation**: [docs/modules/serialization/](../../../docs/modules/serialization/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
