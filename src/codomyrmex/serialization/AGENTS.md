# Codomyrmex Agents — src/codomyrmex/serialization

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Serialization Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Serialization module providing unified data serialization/deserialization with support for JSON, YAML, TOML, MessagePack, and other formats for the Codomyrmex platform. This module integrates with `documents` and `config_management` modules.

The serialization module serves as the serialization layer, providing format-agnostic serialization interfaces with support for multiple data formats.

## Module Overview

### Key Capabilities
- **Data Serialization**: Convert objects to string/bytes
- **Data Deserialization**: Convert string/bytes to objects
- **Format Detection**: Auto-detect serialization format
- **Type Preservation**: Preserve types where possible
- **Custom Serializers**: Register custom serialization logic

### Key Features
- Format-agnostic serialization interface
- Support for multiple serialization formats
- Automatic format detection
- Type hint support
- Custom serializer registration

## Function Signatures

### Serialization Functions

```python
def serialize(obj: Any) -> str | bytes
```

Serialize an object to string or bytes.

**Parameters:**
- `obj` (Any): Object to serialize

**Returns:** `str | bytes` - Serialized data

**Raises:**
- `SerializationError`: If serialization fails

```python
def deserialize(data: str | bytes) -> Any
```

Deserialize data to an object.

**Parameters:**
- `data` (str | bytes): Serialized data

**Returns:** `Any` - Deserialized object

**Raises:**
- `SerializationError`: If deserialization fails

```python
def detect_format(data: str | bytes) -> Optional[str]
```

Detect the serialization format from data.

**Parameters:**
- `data` (str | bytes): Serialized data

**Returns:** `Optional[str]` - Format name if detected, None otherwise

### Custom Serializer Functions

```python
def register_serializer(format_name: str, serializer: callable) -> None
```

Register a custom serializer for a format.

**Parameters:**
- `format_name` (str): Format name
- `serializer` (callable): Serializer function

```python
def get_serializer(format_name: str) -> Optional[callable]
```

Get a serializer for a format.

**Parameters:**
- `format_name` (str): Format name

**Returns:** `Optional[callable]` - Serializer function if found

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `serializer.py` – Base serializer interface
- `serialization_manager.py` – Serialization manager
- `formats/` – Format-specific implementations
  - `json_serializer.py` – JSON serializer
  - `yaml_serializer.py` – YAML serializer
  - `toml_serializer.py` – TOML serializer
  - `msgpack_serializer.py` – MessagePack serializer

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Serialization Protocols

All serialization operations within the Codomyrmex platform must:

1. **Error Handling** - Handle serialization/deserialization errors gracefully
2. **Format Validation** - Validate formats before processing
3. **Type Safety** - Preserve types where possible
4. **Round-Trip** - Support round-trip serialization/deserialization
5. **Performance** - Optimize for common serialization scenarios

### Integration Guidelines

When integrating with other modules:

1. **Use Documents Module** - Integrate with document handling
2. **Config Integration** - Support config_management for configuration serialization
3. **Cache Integration** - Support cache serialization for value storage
4. **Error Recovery** - Implement fallback when serialization fails

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [documents](../documents/AGENTS.md) - Document handling
    - [config_management](../config_management/AGENTS.md) - Configuration management

