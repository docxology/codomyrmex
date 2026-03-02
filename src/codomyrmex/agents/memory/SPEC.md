# Memory -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent memory module providing three complementary storage primitives: conversation history tracking, a learning journal with pattern detection, and a TTL-aware key-value store. Each component is self-contained and uses `codomyrmex.logging_monitoring` for structured logging.

## Architecture

Three independent classes, each following a simple append/query model with no external persistence (in-memory only). `ConversationHistory` models multi-turn dialogue, `LearningJournal` accumulates tagged insights, and `MemoryStore` provides TTL-expiring key-value storage.

## Key Classes

### `Turn`

| Field | Type | Description |
|-------|------|-------------|
| `role` | `str` | Speaker role (user, assistant, system) |
| `content` | `str` | Message content |
| `timestamp` | `float` | Unix timestamp, auto-set via `time.time()` |
| `metadata` | `dict[str, Any]` | Arbitrary extra data |
| `word_count` | `int` (property) | Word count derived from `content.split()` |

### `ConversationHistory`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `max_turns: int = 1000` | `None` | Sets turn limit |
| `add` | `role: str`, `content: str`, `metadata: dict \| None` | `Turn` | Appends turn, trims to `max_turns` |
| `last` | `n: int = 1` | `list[Turn]` | Returns last N turns |
| `by_role` | `role: str` | `list[Turn]` | Filters turns by role |
| `summary` | -- | `dict[str, Any]` | Returns turn count, total words, per-role counts |
| `to_messages` | -- | `list[dict[str, str]]` | Exports as LLM-compatible `[{"role", "content"}]` |
| `clear` | -- | `None` | Removes all turns |

### `JournalEntry`

| Field | Type | Description |
|-------|------|-------------|
| `topic` | `str` | Subject of the learning |
| `insight` | `str` | The lesson or observation |
| `source` | `str` | Where the insight came from |
| `confidence` | `float` | Confidence level, 0.0 to 1.0 |
| `tags` | `list[str]` | Categorization tags |
| `timestamp` | `float` | Unix timestamp, auto-set |

### `LearningJournal`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `record` | `topic, insight, source, confidence, tags` | `JournalEntry` | Appends a new journal entry |
| `by_topic` | `topic: str` | `list[JournalEntry]` | Filters entries by topic |
| `by_tag` | `tag: str` | `list[JournalEntry]` | Filters entries containing the tag |
| `detect_patterns` | -- | `dict[str, Any]` | Returns top-5 topics, top-5 tags, total entries, avg confidence |
| `recent` | `n: int = 10` | `list[JournalEntry]` | Returns last N entries |
| `high_confidence` | `threshold: float = 0.8` | `list[JournalEntry]` | Filters entries above confidence threshold |

### `MemoryEntry`

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Memory key |
| `value` | `Any` | Stored value |
| `created_at` | `float` | Creation timestamp, auto-set |
| `expires_at` | `float` | Expiry timestamp (0 = never expires) |
| `tags` | `list[str]` | Searchable tags |
| `access_count` | `int` | Number of successful reads |
| `is_expired` | `bool` (property) | True when `time.time() > expires_at` and `expires_at > 0` |

### `MemoryStore`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `put` | `key: str`, `value: Any`, `ttl: float = 0`, `tags: list \| None` | `None` | Stores value; ttl > 0 sets expiry |
| `get` | `key: str`, `default: Any = None` | `Any` | Returns value or default; evicts if expired |
| `delete` | `key: str` | `bool` | Removes entry, returns True if existed |
| `has` | `key: str` | `bool` | Checks existence; evicts if expired |
| `search_by_tag` | `tag: str` | `list[MemoryEntry]` | Returns entries matching tag after cleanup |
| `keys` | -- | `list[str]` | Returns all non-expired keys |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (`get_logger`)
- **External**: Standard library only (`time`, `dataclasses`, `collections`)

## Constraints

- All storage is in-memory only; no persistence across process restarts.
- TTL expiration is lazy (checked on access), not proactive; entries may remain in memory until next access or batch cleanup.
- `ConversationHistory` trims from the front (oldest turns removed first) when `max_turns` is exceeded.
- `LearningJournal.detect_patterns` divides by `self.size` which is safe (guarded by `if self.size > 0`).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- No custom exceptions defined; errors propagate from standard library operations.
- All classes use `codomyrmex.logging_monitoring.get_logger` for structured logging.
- All errors logged before propagation.
