# Personal AI Infrastructure — Serialization Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Serialization module provides unified multi-format object serialization and
deserialization. It supports JSON, YAML, pickle, MessagePack, Avro, and Parquet formats
for data persistence, inter-module communication, and streaming large datasets.

The module is a **Foundation Layer** utility — consumed by `agentic_memory/`, `cache/`,
`config_management/`, and `events/` for all durable data storage and cross-module data
exchange. It does not expose MCP tools; agents use it as a Python library.

## PAI Capabilities

### Python API (no MCP tools — use direct Python import)

**Serialize and deserialize with the manager:**

```python
from codomyrmex.serialization import SerializationManager

mgr = SerializationManager()

# Serialize to JSON
payload = mgr.serialize({"key": "value", "count": 42}, format="json")
# payload: str | bytes

# Deserialize back
data = mgr.deserialize(payload, format="json")
assert data["count"] == 42
```

**Use a specific format serializer:**

```python
from codomyrmex.serialization import MsgpackSerializer, AvroSerializer

# High-performance binary encoding
serializer = MsgpackSerializer()
packed = serializer.serialize({"records": [1, 2, 3]})  # bytes
unpacked = serializer.deserialize(packed)
```

**Streaming for large datasets:**

```python
from pathlib import Path

from codomyrmex.serialization.streaming import stream_jsonl_read, stream_jsonl_write

count = stream_jsonl_write(Path("output.jsonl"), iter(large_dataset))
for record in stream_jsonl_read(Path("output.jsonl")):
    ...
```

### Supported Formats

| Format | Class | Best For |
| --- | --- | --- |
| JSON | `Serializer(SerializationFormat.JSON)` | Human-readable config, API responses |
| YAML | `Serializer(SerializationFormat.YAML)` | Configuration files |
| Pickle | `Serializer(SerializationFormat.PICKLE)` | Trusted, Python-only object snapshots |
| MessagePack | `MsgpackSerializer` | High-performance binary inter-module data |
| Avro | `AvroSerializer` | Schema-enforced big data pipelines |
| Parquet | `ParquetSerializer` | Columnar analytics storage |

## Key Exports

| Export | Type | Purpose |
| --- | --- | --- |
| `SerializationManager` | Class | Unified encode/decode with format selection |
| `Serializer` | Class | Format-specific base serializer |
| `SerializationFormat` | Enum | `JSON`, `YAML`, `PICKLE` |
| `MsgpackSerializer` | Class | High-performance binary encoding |
| `AvroSerializer` | Class | Schema-enforced Avro encoding |
| `ParquetSerializer` | Class | Columnar Parquet encoding |
| `SerializationError` | Exception | Base serialization failure |
| `DeserializationError` | Exception | Decode failure |
| `SchemaValidationError` | Exception | Schema mismatch during (de)serialization |
| `FormatNotSupportedError` | Exception | Requested format not available |

## PAI Algorithm Phase Mapping

| Phase | Serialization Contribution | Key Classes |
| --- | --- | --- |
| **BUILD** (4/7) | Encode module output for storage or passing to next module | `SerializationManager` |
| **EXECUTE** (5/7) | Serialize/deserialize data across module boundaries at runtime | `Serializer`, `MsgpackSerializer` |
| **VERIFY** (6/7) | Decode stored artifacts and confirm round-trip fidelity | `SerializationManager.deserialize` |
| **LEARN** (7/7) | Persist PAI agent state, memory, and reflections to durable storage | `streaming.stream_jsonl_write`, `AvroSerializer` |

### Concrete PAI Usage Pattern

In a LEARN phase ISC criterion "Agent memory persisted to durable storage":

```python
from pathlib import Path

from codomyrmex.serialization import SerializationManager

mgr = SerializationManager()
agent_state = {"iteration": 42, "criteria": ["ISC-C1", "ISC-C2"], "passed": 2}
state_file = Path("~/.codomyrmex/agent_state.json").expanduser()

# Persist
encoded = mgr.serialize(agent_state, format="json")
state_file.write_bytes(encoded if isinstance(encoded, bytes) else encoded.encode())

# Recover on next session
recovered = mgr.deserialize(state_file.read_bytes(), format="json")
assert recovered["iteration"] == 42
```

## Architecture Role

**Foundation Layer** — Cross-cutting data encoding utility. No upstream codomyrmex
dependencies (except optional `validation.schemas` for `Result`/`ResultStatus` types).
Consumed by `agentic_memory/`, `cache/`, `config_management/`, and `events/`.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:

- Direct Python import: `from codomyrmex.serialization import ...`
- CLI: `codomyrmex serialization <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
