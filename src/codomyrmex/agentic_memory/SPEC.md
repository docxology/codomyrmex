# Agentic Memory — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provides persistent, structured memory for AI agents with key-value storage, search, and user profiling. Central to the PAI Algorithm's LEARN phase.

## Functional Requirements

### Memory Operations

| Operation | Signature | Description |
|-----------|-----------|-------------|
| **Put** | `memory_put(key: str, value: Any) → None` | Store a key-value pair |
| **Get** | `memory_get(key: str) → Any` | Retrieve value by key; raises `KeyError` if missing |
| **Search** | `memory_search(query: str, limit: int) → list` | Search memories by pattern |
| **List** | `memory_list() → list[str]` | Return all stored keys |

### Storage Backends

| Backend | Persistence | Performance | Thread-Safe |
|---------|-------------|-------------|-------------|
| `InMemoryStore` | Session only | O(1) get/put | Yes |
| `JSONFileStore` | Disk-backed | O(1) get, O(n) search | Yes (file locks) |

### User Profile

| Method | Description |
|--------|-------------|
| `UserProfile()` | Initialize or load user preference tracking |
| Profile fields | Coding style, interaction patterns, preferred models |

## Non-Functional Requirements

- **Latency**: `memory_get` < 1ms (in-memory), < 10ms (file-backed)
- **Capacity**: Up to 100,000 entries per store
- **Durability**: `JSONFileStore` flushes on every write
- **Concurrency**: Thread-safe via locking primitives

## Architecture

- Depends on: `serialization/` (JSON persistence), `logging_monitoring/` (audit logging)
- Consumed by: All agent modules, MCP server (`store_memory`, `recall_memory`, `list_memories`)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
