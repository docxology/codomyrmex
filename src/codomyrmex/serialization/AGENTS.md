# Agent Guidelines - Serialization

## Module Overview

Data serialization: JSON, YAML, msgpack, protobuf, and custom formats.

## Key Classes

- **Serializer** — Multi-format serialization
- **JSONSerializer** — JSON with custom encoders
- **YAMLSerializer** — YAML with safe loading
- **ProtobufSerializer** — Protocol Buffers

## Agent Instructions

1. **Use appropriate format** — JSON for APIs, msgpack for speed
2. **Handle dates** — Use ISO format for datetime
3. **Safe loading** — Use safe_load for YAML
4. **Version schemas** — Include version in format
5. **Validate on deserialize** — Check structure after load

## Common Patterns

```python
from codomyrmex.serialization import (
    Serializer, JSONSerializer, serialize, deserialize
)

# Auto-detect format
data = {"name": "test", "count": 42}
json_bytes = serialize(data, format="json")
back = deserialize(json_bytes, format="json")

# Custom serializer
serializer = Serializer()
serializer.register_encoder(datetime, lambda d: d.isoformat())
output = serializer.dumps({"created": datetime.now()})

# With validation
from codomyrmex.serialization import deserialize_validated
data = deserialize_validated(raw, schema=MySchema)
```

## Testing Patterns

```python
# Verify round-trip
data = {"key": "value", "num": 123}
encoded = serialize(data, format="json")
decoded = deserialize(encoded, format="json")
assert decoded == data

# Verify format detection
assert detect_format(b'{"a":1}') == "json"
assert detect_format(b'a: 1') == "yaml"
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
