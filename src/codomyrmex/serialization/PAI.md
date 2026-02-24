# Personal AI Infrastructure — Serialization Module

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Serialization module provides unified multi-format object serialization and
deserialization. It supports JSON, YAML, TOML, MessagePack, Avro, and Parquet formats
for data persistence, inter-module communication, and streaming large datasets.

The module is a **Foundation Layer** utility — consumed by `agentic_memory/`, `cache/`,
`config_management/`, and `events/` for all durable data storage and cross-module data
exchange. It does not expose MCP tools; agents use it as a Python library.

## PAI Capabilities

### Python API (no MCP tools — use direct Python import)

**Serialize and deserialize with the manager:**

```python
from codomyrmex.serialization import SerializationManager, SerializationFormat

mgr = SerializationManager()

# Serialize to JSON
payload = mgr.serialize({"key": "value", "count": 42}, fmt=SerializationFormat.JSON)
# payload: bytes

# Deserialize back
data = mgr.deserialize(payload, fmt=SerializationFormat.JSON)
assert data["count"] == 42
```

**Use a specific format serializer:**

```python
from codomyrmex.serialization import MsgpackSerializer, AvroSerializer

# High-performance binary encoding
serializer = MsgpackSerializer()
packed = serializer.encode({"records": [1, 2, 3]})
unpacked = serializer.decode(packed)
```

**Streaming for large datasets:**

```python
from codomyrmex.serialization.streaming import StreamingSerializer

streamer = StreamingSerializer(fmt=SerializationFormat.JSON)
with open("output.jsonl", "wb") as f:
    for record in large_dataset:
        f.write(streamer.encode_one(record))
```

### Supported Formats

| Format | Class | Best For |
|--------|-------|---------|
| JSON | `Serializer(SerializationFormat.JSON)` | Human-readable config, API responses |
| YAML | `Serializer(SerializationFormat.YAML)` | Configuration files |
| TOML | `Serializer(SerializationFormat.TOML)` | Project config (pyproject.toml) |
| MessagePack | `MsgpackSerializer` | High-performance binary inter-module data |
| Avro | `AvroSerializer` | Schema-enforced big data pipelines |
| Parquet | `ParquetSerializer` | Columnar analytics storage |

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `SerializationManager` | Class | Unified encode/decode with format selection |
| `Serializer` | Class | Format-specific base serializer |
| `SerializationFormat` | Enum | `JSON`, `YAML`, `TOML`, `MSGPACK`, `AVRO`, `PARQUET` |
| `MsgpackSerializer` | Class | High-performance binary encoding |
| `AvroSerializer` | Class | Schema-enforced Avro encoding |
| `ParquetSerializer` | Class | Columnar Parquet encoding |
| `SerializationError` | Exception | Base serialization failure |
| `DeserializationError` | Exception | Decode failure |
| `SchemaValidationError` | Exception | Schema mismatch during (de)serialization |
| `FormatNotSupportedError` | Exception | Requested format not available |

## PAI Algorithm Phase Mapping

| Phase | Serialization Contribution | Key Classes |
|-------|---------------------------|-------------|
| **BUILD** (4/7) | Encode module output for storage or passing to next module | `SerializationManager` |
| **EXECUTE** (5/7) | Serialize/deserialize data across module boundaries at runtime | `Serializer`, `MsgpackSerializer` |
| **VERIFY** (6/7) | Decode stored artifacts and confirm round-trip fidelity | `SerializationManager.deserialize` |
| **LEARN** (7/7) | Persist PAI agent state, memory, and reflections to durable storage | `StreamingSerializer`, `AvroSerializer` |

### Concrete PAI Usage Pattern

In a LEARN phase ISC criterion "Agent memory persisted to durable storage":

```python
from codomyrmex.serialization import SerializationManager, SerializationFormat

mgr = SerializationManager()
agent_state = {"iteration": 42, "criteria": ["ISC-C1", "ISC-C2"], "passed": 2}

# Persist
encoded = mgr.serialize(agent_state, fmt=SerializationFormat.JSON)
Path("~/.codomyrmex/agent_state.json").write_bytes(encoded)

# Recover on next session
recovered = mgr.deserialize(Path("~/.codomyrmex/agent_state.json").read_bytes(), fmt=SerializationFormat.JSON)
assert recovered["iteration"] == 42
```

## Architecture Role

**Foundation Layer** — Cross-cutting data encoding utility. No upstream codomyrmex
dependencies (except optional `validation.schemas` for `Result`/`ResultStatus` types).
Consumed by `agentic_memory/`, `cache/`, `config_management/`, and `events/`.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
