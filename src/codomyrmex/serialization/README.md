# Serialization Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Serialization module provides unified data serialization and deserialization with support for multiple formats, automatic format detection, and consistent error handling.

## Supported Formats

| Format | Description |
|--------|-------------|
| `json` | JSON (default) - human-readable, widely supported |
| `yaml` | YAML - human-friendly, supports comments |
| `toml` | TOML - configuration-focused format |
| `msgpack` | MessagePack - binary, compact, fast |

## Key Features

- **Multi-Format Support**: JSON, YAML, TOML, MessagePack
- **Auto-Detection**: Detect format from data content
- **Consistent API**: Same interface for all formats
- **Type Preservation**: Maintains Python types where possible

## Quick Start

```python
from codomyrmex.serialization import (
    serialize, deserialize, detect_format,
    Serializer, SerializationManager,
)

# Simple serialization
data = {"name": "Alice", "scores": [95, 87, 92]}

# Serialize to different formats
json_str = serialize(data, format="json")
yaml_str = serialize(data, format="yaml")
msgpack_bytes = serialize(data, format="msgpack")

# Deserialize
restored = deserialize(json_str, format="json")
restored = deserialize(yaml_str, format="yaml")

# Auto-detect format
format_name = detect_format(json_str)  # "json"

# Using the Serializer class
serializer = Serializer(format="yaml")
yaml_output = serializer.serialize(data)
restored = serializer.deserialize(yaml_output)
```

## Core Classes

| Class | Description |
|-------|-------------|
| `Serializer` | Core serialization with format selection |
| `SerializationManager` | Manage multiple serializers |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `serialize(obj, format)` | Serialize object to string/bytes |
| `deserialize(data, format)` | Deserialize to Python object |
| `detect_format(data)` | Auto-detect serialization format |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `SerializationError` | Serialization operations failed |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
