# Codomyrmex Agents — src/codomyrmex/serialization

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Unified data serialization/deserialization with support for JSON, YAML, TOML, MessagePack, and other formats. Provides format-agnostic serialization interface with automatic format detection and custom serializer registration.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `serialization_manager.py` – Manager for serialization operations
- `serializer.py` – Base serializer interface and implementations

## Key Classes and Functions

### Serializer (`serializer.py`)
- `Serializer(format: str = "json")` – Initialize serializer with specified format (json, yaml, toml, msgpack)
- `serialize(obj: Any) -> Union[str, bytes]` – Serialize an object to string or bytes
- `deserialize(data: Union[str, bytes], format: Optional[str] = None) -> Any` – Deserialize data to an object
- `detect_format(data: Union[str, bytes]) -> Optional[str]` – Detect serialization format from data
- `register_serializer(format_name: str, serializer: callable, deserializer: Optional[callable] = None) -> None` – Register a custom serializer
- `_serialize_json(obj: Any) -> str` – Internal JSON serialization
- `_deserialize_json(data: Union[str, bytes]) -> Any` – Internal JSON deserialization
- `_serialize_yaml(obj: Any) -> str` – Internal YAML serialization
- `_deserialize_yaml(data: Union[str, bytes]) -> Any` – Internal YAML deserialization
- `_serialize_toml(obj: Any) -> str` – Internal TOML serialization
- `_deserialize_toml(data: Union[str, bytes]) -> Any` – Internal TOML deserialization
- `_serialize_msgpack(obj: Any) -> bytes` – Internal MessagePack serialization
- `_deserialize_msgpack(data: Union[str, bytes]) -> Any` – Internal MessagePack deserialization

### SerializationManager (`serialization_manager.py`)
- `SerializationManager()` – Manager for serialization operations
- `get_serializer(format: str = "json") -> Serializer` – Get a serializer for a format
- `serialize(obj: Any, format: str = "json") -> Union[str, bytes]` – Serialize an object
- `deserialize(data: Union[str, bytes], format: Optional[str] = None) -> Any` – Deserialize data (auto-detects format if None)

### Module Functions (`__init__.py`)
- `serialize(obj: Any, format: str = "json") -> Union[str, bytes]` – Serialize an object to string or bytes
- `deserialize(data: Union[str, bytes], format: Optional[str] = None) -> Any` – Deserialize data to an object
- `detect_format(data: Union[str, bytes]) -> Optional[str]` – Detect serialization format from data

### Exceptions
- `SerializationError` – Raised when serialization operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation