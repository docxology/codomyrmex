# Codomyrmex Agents — src/codomyrmex/cache/serializers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Pluggable cache serialization layer providing six serializer implementations and two composable wrappers. Supports JSON, pickle, string, and typed serialization with optional zlib compression and base64 encoding. A factory function creates serializers by name.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `CacheSerializer` (ABC) | Abstract base with `serialize(value) -> bytes` and `deserialize(data) -> Any` |
| `__init__.py` | `JSONSerializer` | JSON serialization with configurable indent |
| `__init__.py` | `PickleSerializer` | Pickle serialization (trusted data only) with configurable protocol |
| `__init__.py` | `StringSerializer` | Simple `str()` encoding with configurable character set |
| `__init__.py` | `TypedSerializer` | Preserves Python type information (`_type`, `_value`) via JSON wrapper |
| `__init__.py` | `CompressedSerializer` | Composable wrapper adding zlib compression (configurable level) |
| `__init__.py` | `Base64Serializer` | Composable wrapper adding base64 encoding |
| `__init__.py` | `create_serializer` | Factory: `create_serializer("json", compress=True)` |

## Operating Contracts

- `PickleSerializer` warning: can execute arbitrary code on deserialization; use only with trusted data.
- `CompressedSerializer` and `Base64Serializer` are wrappers that compose with any base serializer.
- `TypedSerializer` preserves type for `int`, `float`, `bool`, `str`, `list`, `dict`; other types are `str()`-ified.
- `create_serializer` accepts `"json"`, `"pickle"`, `"string"`, `"typed"` with optional `compress=True`.
- Errors must be logged before re-raising.

## Integration Points

- **Depends on**: Standard library only (`json`, `pickle`, `zlib`, `base64`, `logging`)
- **Used by**: `cache` parent module, `cache.cache_manager`, external cache backends

## Navigation

- **Parent**: [cache](../README.md)
- **Root**: [Root](../../../../README.md)
