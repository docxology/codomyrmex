# Codomyrmex Agents -- src/codomyrmex/agents/history

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides conversation and context persistence for agent sessions. The module defines message and conversation data models, three interchangeable storage backends (in-memory, JSON file, SQLite), and a high-level `ConversationManager` that tracks an active conversation, enforces message limits, and delegates persistence to a pluggable store.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `MessageRole` | Enum defining conversation roles: SYSTEM, USER, ASSISTANT, TOOL, FUNCTION |
| `models.py` | `HistoryMessage` | Dataclass for a single message with SHA-256-based auto-ID, token count, and metadata |
| `models.py` | `Conversation` | Ordered message collection with `add_message`, `truncate`, `get_messages_for_api`, and dict serialization |
| `stores.py` | `InMemoryHistoryStore` | Dict-backed ephemeral store with save/load/delete/list/search |
| `stores.py` | `FileHistoryStore` | One-JSON-file-per-conversation persistence under a configurable directory |
| `stores.py` | `SQLiteHistoryStore` | SQLite-backed store with indexed message table and LIKE-based search |
| `manager.py` | `ConversationManager` | High-level facade: creates conversations, auto-truncates on save, manages active conversation state |

## Operating Contracts

- All three store backends share the same interface: `save`, `load`, `delete`, `list_conversations`, `search`.
- `Conversation.truncate()` always preserves SYSTEM-role messages while trimming oldest non-system messages.
- `ConversationManager.save()` enforces `max_messages_per_conversation` by calling `truncate` before delegating to the store.
- Message IDs are deterministic SHA-256 hashes of role + content + timestamp; collisions are possible but unlikely at the 16-hex-char prefix length.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`hashlib`, `json`, `sqlite3`, `dataclasses`, `datetime`, `pathlib`)
- **Used by**: `codomyrmex.agents.core` session management, any agent requiring multi-turn conversation state

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [codomyrmex](../../../../README.md)
