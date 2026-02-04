# serialization - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The serialization module provides data serialization and deserialization utilities supporting JSON, YAML, TOML, pickle, and MessagePack formats.

## Classes

### Serializer

Multi-format data serializer.

```python
from codomyrmex.serialization import Serializer
```

#### Constructor

```python
Serializer(format: str = "json")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | `str` | `"json"` | Serialization format: `"json"`, `"yaml"`, `"toml"`, `"pickle"`, `"msgpack"` |

#### Methods

##### serialize

```python
def serialize(data: Any) -> bytes
```

Serialize data to bytes.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `Any` | Data to serialize |

**Returns**: `bytes` - Serialized data

**Raises**: `SerializationError` if serialization fails

##### deserialize

```python
def deserialize(data: bytes) -> Any
```

Deserialize bytes to data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `bytes` | Serialized data |

**Returns**: `Any` - Deserialized data

**Raises**: `SerializationError` if deserialization fails

##### serialize_to_file

```python
def serialize_to_file(data: Any, path: str) -> bool
```

Serialize data and write to file.

##### deserialize_from_file

```python
def deserialize_from_file(path: str) -> Any
```

Read file and deserialize.

---

### SerializationManager

High-level serialization management with format detection.

```python
from codomyrmex.serialization import SerializationManager
```

#### Methods

##### detect_format

```python
def detect_format(path: str) -> str
```

Detect serialization format from file extension.

##### auto_serialize

```python
def auto_serialize(data: Any, path: str) -> bool
```

Automatically serialize based on file extension.

##### auto_deserialize

```python
def auto_deserialize(path: str) -> Any
```

Automatically deserialize based on file extension.

---

## Exceptions

### SerializationError

```python
from codomyrmex.serialization import SerializationError
```

Raised when serialization operations fail. Inherits from `CodomyrmexError`.

---

## Usage Examples

### JSON Serialization

```python
from codomyrmex.serialization import Serializer

serializer = Serializer("json")

data = {"name": "example", "values": [1, 2, 3]}
serialized = serializer.serialize(data)

restored = serializer.deserialize(serialized)
assert restored == data
```

### YAML Serialization

```python
from codomyrmex.serialization import Serializer

serializer = Serializer("yaml")

config = {
    "database": {"host": "localhost", "port": 5432},
    "debug": True
}

serializer.serialize_to_file(config, "config.yaml")
loaded = serializer.deserialize_from_file("config.yaml")
```

### Auto-Detection

```python
from codomyrmex.serialization import SerializationManager

manager = SerializationManager()

# Automatically uses YAML format based on extension
manager.auto_serialize(data, "output.yaml")

# Automatically detects format and deserializes
data = manager.auto_deserialize("config.toml")
```

---

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| JSON | `.json` | JavaScript Object Notation |
| YAML | `.yaml`, `.yml` | YAML Ain't Markup Language |
| TOML | `.toml` | Tom's Obvious Minimal Language |
| Pickle | `.pkl`, `.pickle` | Python object serialization |
| MessagePack | `.msgpack`, `.mp` | Binary JSON alternative |

---

## Integration

### Dependencies
- Python standard library (`json`, `pickle`)
- `pyyaml` - YAML support
- `toml` - TOML support (optional)
- `msgpack` - MessagePack support (optional)
- `codomyrmex.logging_monitoring` for logging
- `codomyrmex.exceptions` for error handling

### Related Modules
- [`config_management`](../config_management/API_SPECIFICATION.md) - Configuration files
- [`documents`](../documents/API_SPECIFICATION.md) - Document handling
- [`cache`](../cache/API_SPECIFICATION.md) - Cache serialization

---

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent**: [codomyrmex](../AGENTS.md)
