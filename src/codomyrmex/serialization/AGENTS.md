# Agent Guidelines - Serialization

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Multi-format data serialization and deserialization supporting JSON, YAML, msgpack, protobuf, and
custom formats. Provides `Serializer` for format-agnostic round-trips with custom encoder
registration, `YAMLSerializer` with enforced safe loading, and `ProtobufSerializer` for typed binary
encoding. Three MCP tools expose the full serialize/deserialize lifecycle to PAI agents without
requiring Python imports.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `Serializer`, `JSONSerializer`, `YAMLSerializer`, `ProtobufSerializer`, `serialize`, `deserialize` |
| `serializer.py` | Base `Serializer` with encoder registration and format dispatch |
| `json_serializer.py` | JSON with custom encoder/decoder support |
| `yaml_serializer.py` | YAML with safe_load enforcement |
| `protobuf_serializer.py` | Protocol Buffers serialization |
| `mcp_tools.py` | MCP tools: `serialize_data`, `deserialize_data`, `serialization_list_formats` |

## Key Classes

- **Serializer** — Multi-format serialization with custom encoder registration
- **JSONSerializer** — JSON with custom encoders and decoders
- **YAMLSerializer** — YAML with `safe_load` enforcement (no arbitrary Python objects)
- **ProtobufSerializer** — Protocol Buffers serialization

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `serialize_data` | Serialize a Python dict to a named format (json, yaml, msgpack) | SAFE |
| `deserialize_data` | Deserialize bytes or a string back to a Python dict | SAFE |
| `serialization_list_formats` | List all supported serialization format names | SAFE |

## Agent Instructions

1. **Use appropriate format** — JSON for APIs, msgpack for speed, YAML for config files
2. **Handle dates** — Use ISO format for datetime serialization
3. **Safe loading** — `YAMLSerializer` enforces `safe_load`; never bypass this
4. **Version schemas** — Include a `version` field in serialized payloads
5. **Validate on deserialize** — Check structure after loading untrusted data

## Operating Contracts

- `YAMLSerializer` always uses `safe_load` — arbitrary Python objects will not deserialize
- `Serializer.register_encoder(type, fn)` is not thread-safe; register before concurrent use
- `serialize_data` MCP tool accepts only JSON-serializable dicts as input
- Round-trip fidelity: `deserialize(serialize(data, fmt), fmt) == data` for JSON and YAML
- **DO NOT** pass raw file bytes to `deserialize` without specifying a format

## Common Patterns

```python
from codomyrmex.serialization import (
    Serializer, JSONSerializer, serialize, deserialize
)

# Auto-detect format round-trip
data = {"name": "test", "count": 42}
json_bytes = serialize(data, format="json")
back = deserialize(json_bytes, format="json")
assert back == data

# Custom encoder for datetime
from datetime import datetime
serializer = Serializer()
serializer.register_encoder(datetime, lambda d: d.isoformat())
output = serializer.dumps({"created": datetime.now()})
```

## Testing Patterns

```python
# Verify JSON round-trip
data = {"key": "value", "num": 123}
encoded = serialize(data, format="json")
decoded = deserialize(encoded, format="json")
assert decoded == data

# Verify YAML round-trip
encoded = serialize(data, format="yaml")
decoded = deserialize(encoded, format="yaml")
assert decoded == data
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `serialize_data`, `deserialize_data`, `serialization_list_formats` | TRUSTED |
| **Architect** | Read + Design | `serialization_list_formats` — format selection and schema design review | OBSERVED |
| **QATester** | Validation | `serialize_data`, `deserialize_data`, `serialization_list_formats` — round-trip fidelity verification | OBSERVED |
| **Researcher** | Read-only | `serialization_list_formats`, `serialize_data` — format inspection for research analysis | SAFE |

### Engineer Agent
**Use Cases**: Serializing inter-module data payloads during BUILD/EXECUTE, registering custom encoders, format conversion pipelines.

### Architect Agent
**Use Cases**: Designing serialization schemas, reviewing format selection trade-offs (JSON vs msgpack vs YAML), planning versioned schema migration strategies.

### QATester Agent
**Use Cases**: Validating round-trip serialization fidelity across all formats, verifying format auto-detection, testing edge cases.

### Researcher Agent
**Use Cases**: Inspecting supported format catalog and serializing research data structures during analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/serialization.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/serialization.cursorrules)
