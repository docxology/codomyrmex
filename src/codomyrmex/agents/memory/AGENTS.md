# Codomyrmex Agents -- src/codomyrmex/agents/memory

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides three complementary memory primitives for agent sessions: turn-based conversation history with summarization (`ConversationHistory`), a learning journal with pattern detection (`LearningJournal`), and a TTL-aware key-value memory store (`MemoryStore`). Together they enable agents to track dialogue context, accumulate insights, and cache runtime data with automatic expiration.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `conversation.py` | `Turn` | Dataclass for a single conversation turn: role, content, timestamp, metadata, word count |
| `conversation.py` | `ConversationHistory` | Multi-turn tracker with `add`, `last`, `by_role`, `summary`, and LLM-compatible `to_messages` export |
| `journal.py` | `JournalEntry` | Dataclass: topic, insight, source, confidence (0-1), tags, timestamp |
| `journal.py` | `LearningJournal` | Append-only journal with `record`, `by_topic`, `by_tag`, `detect_patterns`, `high_confidence` |
| `store.py` | `MemoryEntry` | Dataclass: key, value, created_at, expires_at, tags, access_count with `is_expired` property |
| `store.py` | `MemoryStore` | Key-value store with `put` (TTL support), `get` (auto-evicts expired), `delete`, `has`, `search_by_tag` |

## Operating Contracts

- `ConversationHistory` enforces `max_turns` by slicing to the most recent N turns on each `add` call.
- `MemoryStore.get` lazily evicts expired entries on access; `search_by_tag`, `size`, and `keys` batch-clean expired entries first.
- `LearningJournal.detect_patterns` returns top-5 topics and tags via `Counter.most_common` plus average confidence.
- All three classes use `time.time()` for timestamps; `Turn` and `JournalEntry` auto-set timestamp in `__post_init__`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (`get_logger`)
- **Used by**: `codomyrmex.agents.core` session management, agent reflection pipelines, runtime caching

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [codomyrmex](../../../../README.md)
