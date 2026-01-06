# src/codomyrmex/serialization

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Overview

Serialization module providing unified data serialization/deserialization with support for JSON, YAML, TOML, MessagePack, and other formats for the Codomyrmex platform. This module integrates with `documents` and `config_management` modules.

The serialization module serves as the serialization layer, providing format-agnostic serialization interfaces with support for multiple data formats.

## Key Features

- **Multiple Formats**: Support for JSON, YAML, TOML, MessagePack, and other formats
- **Format Detection**: Automatic format detection from data
- **Type Preservation**: Preserve types where possible during serialization
- **Custom Serializers**: Register custom serialization logic
- **Error Handling**: Comprehensive error handling for invalid data

## Integration Points

- **documents/** - Document serialization
- **config_management/** - Configuration serialization
- **cache/** - Cache value serialization

## Usage Examples

```python
from codomyrmex.serialization import Serializer, SerializationManager

# Initialize serializer
serializer = Serializer(format="json")

# Serialize data
data = {"key": "value", "number": 42}
serialized = serializer.serialize(data)

# Deserialize data
deserialized = serializer.deserialize(serialized)

# Format detection
detected_format = serializer.detect_format(serialized)

# Serialization manager
manager = SerializationManager()
json_data = manager.serialize(data, format="json")
yaml_data = manager.serialize(data, format="yaml")
```

## Navigation

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related Modules**:
    - [documents](../documents/README.md) - Document handling
    - [config_management](../config_management/README.md) - Configuration management

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.serialization import Serializer, SerializationManager

serializer = Serializer()
# Use serializer for data serialization/deserialization
```

## Contributing

We welcome contributions! Please ensure you:
1. Follow the project coding standards.
2. Add tests for new functionality.
3. Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

