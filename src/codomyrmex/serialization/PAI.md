# Personal AI Infrastructure — Serialization Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Serialization module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.serialization import Serializer, SerializationManager, SerializationFormat, serialize, deserialize
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Serializer` | Class | Serializer |
| `SerializationManager` | Class | Serializationmanager |
| `SerializationFormat` | Class | Serializationformat |
| `MsgpackSerializer` | Class | Msgpackserializer |
| `AvroSerializer` | Class | Avroserializer |
| `ParquetSerializer` | Class | Parquetserializer |
| `serialize` | Function/Constant | Serialize |
| `deserialize` | Function/Constant | Deserialize |
| `SerializationError` | Class | Serializationerror |
| `DeserializationError` | Class | Deserializationerror |
| `SchemaValidationError` | Class | Schemavalidationerror |
| `EncodingError` | Class | Encodingerror |
| `FormatNotSupportedError` | Class | Formatnotsupportederror |
| `CircularReferenceError` | Class | Circularreferenceerror |
| `TypeConversionError` | Class | Typeconversionerror |

*Plus 2 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Serialization Contribution |
|-------|------------------------------|
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
