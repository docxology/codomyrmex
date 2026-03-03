# Serialization

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Serialization module for Codomyrmex.

## Architecture Overview

```
serialization/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`Serializer`**
- **`SerializationManager`**
- **`SerializationFormat`**
- **`MsgpackSerializer`**
- **`AvroSerializer`**
- **`ParquetSerializer`**
- **`serialize`**
- **`deserialize`**
- **`SerializationError`**
- **`DeserializationError`**
- **`SchemaValidationError`**
- **`EncodingError`**
- **`FormatNotSupportedError`**
- **`CircularReferenceError`**
- **`TypeConversionError`**

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/serialization/](../../../../src/codomyrmex/serialization/)
- **Parent**: [All Modules](../README.md)
