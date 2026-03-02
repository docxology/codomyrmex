# Transport — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Portable agent state serialization, HMAC-verified deserialization, wire-format messaging protocol, and durable checkpoint persistence. Enables agent state to be saved, transmitted, verified, and restored across process boundaries.

## Architecture

Four-component design:

1. **Serializer**: `AgentSerializer` captures agent state into `AgentSnapshot` dataclasses and serializes to deterministic JSON bytes
2. **Deserializer**: `AgentDeserializer` reconstructs snapshots and optionally verifies HMAC-SHA256 integrity signatures
3. **Protocol**: `TransportMessage` provides the wire-format envelope with typed headers and signed payloads
4. **Checkpoint**: `Checkpoint` wraps snapshots with disk persistence and diff-based state comparison

## Key Classes

### `AgentSerializer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `snapshot` | `agent_id`, `agent_type`, `config`, `traces`, `memory`, `metadata` | `AgentSnapshot` | Create point-in-time state capture |
| `serialize` | `snapshot: AgentSnapshot` | `bytes` | Compact sorted JSON bytes |
| `deserialize_snapshot` | `data: bytes` | `AgentSnapshot` | Reconstruct from JSON bytes |
| `compact_size` | `snapshot: AgentSnapshot` | `int` | Serialized size in bytes |

### `AgentDeserializer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `deserialize` | `data: bytes` | `AgentSnapshot` | Reconstruct snapshot from bytes |
| `sign` | `data: bytes`, `key: str` | `str` | Compute HMAC-SHA256 hex digest |
| `verify_signed` | `data: bytes`, `signature: str`, `key: str` | `bool` | Verify HMAC; raises `IntegrityError` on mismatch |
| `deserialize_verified` | `data`, `signature`, `key` | `AgentSnapshot` | Deserialize with mandatory HMAC verification |

### `TransportMessage`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `to_bytes` | -- | `bytes` | Serialize full message (header + payload + signature) |
| `from_bytes` | `data: bytes` | `TransportMessage` | Deserialize from JSON bytes |
| `sign` | `key: str` | `None` | Sign payload with HMAC-SHA256 |
| `verify` | `key: str` | `bool` | Timing-safe signature verification |
| `size_bytes` | (property) | `int` | Wire size |

### `Checkpoint`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `save` | `path: str or Path` | `None` | Write checkpoint to JSON file |
| `load` | `path: str or Path` | `Checkpoint` | Restore checkpoint from JSON file |
| `diff` | `other: Checkpoint` | `StateDelta` | Compute config, trace, and memory differences |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (via package init)
- **External**: Standard library only (`json`, `hashlib`, `hmac`, `uuid`, `time`, `pathlib`, `dataclasses`, `enum`)

## Constraints

- JSON serialization uses `sort_keys=True` and minimal separators for deterministic byte output.
- HMAC uses SHA-256 exclusively; `hmac.compare_digest` for timing-safe comparison.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `IntegrityError` raised when `verify_signed()` detects HMAC mismatch, with truncated digests in the error message.
- `Checkpoint.load()` propagates `json.JSONDecodeError` and `OSError` from file operations.
- `TransportMessage.from_bytes()` propagates `json.JSONDecodeError` and `KeyError` for malformed messages.
