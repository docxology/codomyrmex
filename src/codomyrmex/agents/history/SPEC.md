# Technical Specification - History

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.history`  
**Last Updated**: 2026-01-29

## 1. Purpose

Conversation and context persistence for stateful interactions

## 2. Architecture

### 2.1 Components

```
history/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `agents`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.agents.history
from codomyrmex.agents.history import (
    MessageRole,           # Enum: SYSTEM, USER, ASSISTANT, TOOL, FUNCTION
    HistoryMessage,        # Dataclass: single message with role, content, tokens, metadata
    Conversation,          # Dataclass: ordered list of messages with truncation and API export
    InMemoryHistoryStore,  # Store: dict-backed ephemeral conversation storage
    FileHistoryStore,      # Store: JSON-file-per-conversation persistence
    SQLiteHistoryStore,    # Store: SQLite-backed conversation persistence with full-text search
    ConversationManager,   # High-level manager: create, save, search, set_active conversation
)

# Key class signatures:
class Conversation:
    def add_message(self, role: MessageRole, content: str, **kwargs) -> HistoryMessage: ...
    def add_user_message(self, content: str, **kwargs) -> HistoryMessage: ...
    def add_assistant_message(self, content: str, **kwargs) -> HistoryMessage: ...
    def get_messages_for_api(self, include_system: bool = True) -> list[dict[str, str]]: ...
    def truncate(self, max_messages: int) -> list[HistoryMessage]: ...

class ConversationManager:
    def __init__(self, store: InMemoryHistoryStore | None = None, max_messages_per_conversation: int = 100): ...
    def create_conversation(self, title: str = "", system_prompt: str | None = None, **metadata) -> Conversation: ...
    def get_conversation(self, conversation_id: str) -> Conversation | None: ...
    def save(self, conversation: Conversation | None = None) -> None: ...
    def list_recent(self, limit: int = 20) -> list[Conversation]: ...
    def search(self, query: str) -> list[Conversation]: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Three-tier storage backends**: `InMemoryHistoryStore` for tests and ephemeral sessions, `FileHistoryStore` for simple persistence, `SQLiteHistoryStore` for indexed full-text search at scale -- all share the same save/load/delete/list/search interface.
2. **SHA-256 message IDs**: Each `HistoryMessage` auto-generates a deterministic 16-char hex ID from role + content + timestamp, ensuring uniqueness without UUID dependencies.
3. **System-message-aware truncation**: `Conversation.truncate()` preserves system messages while trimming the oldest non-system messages, preventing loss of agent instructions.

### 4.2 Limitations

- `FileHistoryStore.search` loads all conversations into memory before filtering; not suitable for large archives
- `SQLiteHistoryStore` uses LIKE-based search rather than FTS5; query performance degrades on large corpora

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/history/
```

## 6. Future Considerations

- FTS5 full-text search index for `SQLiteHistoryStore`
- Token-budget-aware truncation (trim by token count, not message count)
