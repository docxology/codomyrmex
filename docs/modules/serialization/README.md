# Serialization Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Data serialization: JSON, YAML, msgpack, protobuf.

## Key Features

- **Multi-Format** — JSON, YAML, msgpack
- **Custom Encoders** — Handle complex types
- **Validation** — Schema validation
- **Streaming** — Large data streaming

## Quick Start

```python
from codomyrmex.serialization import serialize, deserialize

data = {"name": "test", "count": 42}
json_bytes = serialize(data, format="json")
back = deserialize(json_bytes, format="json")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/serialization/](../../../src/codomyrmex/serialization/)
- **Parent**: [Modules](../README.md)
