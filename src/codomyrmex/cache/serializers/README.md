# cache/serializers

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cache serialization utilities. Provides a family of serializers for converting cache values to and from bytes. Includes JSON, pickle, string, and typed serializers as core implementations, plus composable wrappers for compression (zlib) and base64 encoding. All serializers implement a common `CacheSerializer` ABC with `serialize(value) -> bytes` and `deserialize(data) -> Any`.

## Key Exports

### Abstract Base

- **`CacheSerializer`** -- ABC defining `serialize(value)` and `deserialize(data)` interface

### Core Serializers

- **`JSONSerializer`** -- JSON serialization with optional indent; uses `default=str` for non-serializable types
- **`PickleSerializer`** -- Python pickle serialization with configurable protocol version
- **`StringSerializer`** -- Simple string serialization with configurable encoding (default UTF-8)
- **`TypedSerializer`** -- Wraps values with type metadata (`_type`, `_value`) to preserve type information across serialization boundaries

### Composable Wrappers

- **`CompressedSerializer`** -- Wraps any serializer with zlib compression at configurable level
- **`Base64Serializer`** -- Wraps any serializer with base64 encoding for text-safe transport

### Factory

- **`create_serializer()`** -- Factory function accepting serializer_type ("json", "pickle", "string", "typed") and optional `compress=True` flag

## Directory Contents

- `__init__.py` - Package init; contains all serializer classes inline (single-file module)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [cache](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
