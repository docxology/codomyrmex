# Codomyrmex Agents — src/codomyrmex/agents/transport

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent state serialization, wire-format protocol, HMAC-verified deserialization, and durable checkpointing. Provides the portable transport layer for saving, restoring, and transmitting agent state between processes or across a network.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `serializer.py` | `AgentSerializer` | Creates `AgentSnapshot` objects and serializes them to compact JSON bytes |
| `serializer.py` | `AgentSnapshot` | Point-in-time capture: agent_id, agent_type, config, traces, memory, metadata, version |
| `deserializer.py` | `AgentDeserializer` | Reconstructs `AgentSnapshot` from bytes; supports HMAC-SHA256 verification |
| `deserializer.py` | `IntegrityError` | Raised when HMAC signature verification fails |
| `protocol.py` | `TransportMessage` | Wire-format envelope with header, JSON payload, and optional HMAC-SHA256 signature |
| `protocol.py` | `MessageHeader` | Message metadata: id, type, version, correlation_id, timestamp, source, destination |
| `protocol.py` | `MessageType` | Enum: SNAPSHOT, CHECKPOINT, TASK_REQUEST, TASK_RESULT, HEARTBEAT, CONTROL |
| `checkpoint.py` | `Checkpoint` | Durable persistence wrapper around `AgentSnapshot` with save/load to JSON files |
| `checkpoint.py` | `StateDelta` | Diff between two checkpoints: config changes, traces added, memory keys added/removed/modified |

## Operating Contracts

- `AgentSerializer.serialize()` produces compact JSON bytes with sorted keys and minimal separators for deterministic output.
- `TransportMessage.sign(key)` computes HMAC-SHA256 over the sorted, compact JSON payload. `verify(key)` uses `hmac.compare_digest` for timing-safe comparison.
- `AgentDeserializer.verify_signed()` raises `IntegrityError` if the HMAC does not match, preventing deserialization of tampered data.
- `Checkpoint.save(path)` creates parent directories as needed and writes pretty-printed JSON. `Checkpoint.load(path)` restores the full snapshot.
- `Checkpoint.diff(other)` compares config, trace count, and memory key sets to produce a `StateDelta`.
- Protocol version defaults to `"1.0"`; snapshot format version defaults to `"1.0"`.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (indirectly via `__init__.py`)
- **Used by**: Agent orchestration for state persistence, distributed agent communication, checkpoint/restore workflows

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)
