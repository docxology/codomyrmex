# serialization

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Unified data serialization/deserialization with support for JSON, YAML, TOML, MessagePack, and other formats. Provides format-agnostic serialization interface with automatic format detection and custom serializer registration.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `serialization_manager.py` – File
- `serializer.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.serialization import serialize, deserialize, Serializer, SerializationManager

# Basic serialization
data = {"name": "Alice", "age": 30}
json_str = serialize(data, format="json")
yaml_str = serialize(data, format="yaml")

# Deserialization with auto-detection
obj = deserialize(json_str)  # Auto-detects JSON
obj = deserialize(yaml_str, format="yaml")  # Explicit format

# Using Serializer directly
serializer = Serializer(format="json")
json_data = serializer.serialize(data)
obj = serializer.deserialize(json_data)

# Using SerializationManager
manager = SerializationManager()
json_str = manager.serialize(data, format="json")
obj = manager.deserialize(json_str)  # Auto-detects format
```

