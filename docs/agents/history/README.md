# Interaction History

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.history` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Conversation history for agent sessions. Stores messages per conversation, supports search and truncation, and persists to memory, JSON files, or SQLite.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `ConversationManager` | Create, save, search, and retrieve conversations |
| `Conversation` / `HistoryMessage` / `MessageRole` | Conversation and message models |
| `InMemoryHistoryStore`, `FileHistoryStore`, `SQLiteHistoryStore` | Storage backends |

## Usage

```python
from codomyrmex.agents.history import ConversationManager, SQLiteHistoryStore

manager = ConversationManager(store=SQLiteHistoryStore("history.db"))
conv = manager.create_conversation("Code Review Session")
conv.add_user_message("Review this code...")
conv.add_assistant_message("Here's my review...")
manager.save(conv)

print(manager.get_conversation(conv.conversation_id).message_count)
```

## Source Module

Source: [`src/codomyrmex/agents/history/`](../../../src/codomyrmex/agents/history/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/history/](../../../src/codomyrmex/agents/history/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
