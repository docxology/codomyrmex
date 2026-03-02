# Conversation Memory -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pluggable memory strategies for maintaining LLM conversation context. Each strategy implements a different trade-off between completeness, token efficiency, and semantic richness.

## Architecture

Template method pattern: `Memory` (ABC) defines the interface (`add_message`, `get_messages`, `clear`). Four concrete implementations provide different retention strategies. A factory function `create_memory(MemoryType, **kwargs)` selects the right class.

## Key Classes

### `MemoryMessage`

| Field | Type | Description |
|-------|------|-------------|
| `role` | `str` | Message role (user, assistant, system) |
| `content` | `str` | Message text |
| `timestamp` | `datetime` | When the message was created |
| `metadata` | `dict[str, Any]` | Arbitrary metadata (e.g., entities) |
| `token_count` | `int \| None` | Optional pre-computed token count |

### `BufferMemory`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_message` | `role: str, content: str, **metadata` | `None` | Appends message; trims oldest non-system messages if `max_messages` exceeded |
| `get_messages` | -- | `list[dict[str, str]]` | All messages as `{role, content}` dicts |
| `clear` | -- | `None` | Resets message list |

### `WindowMemory`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_message` | `role: str, content: str, **metadata` | `None` | System messages stored separately; non-system messages capped at `window_size` |
| `get_messages` | -- | `list[dict[str, str]]` | System messages + window of recent messages |

### `SummaryMemory`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_message` | `role: str, content: str, **metadata` | `None` | Appends to recent; triggers `_update_summary` when threshold reached |
| `get_messages` | -- | `list[dict[str, str]]` | Summary as system message + recent unsummarized messages |

### `EntityMemory`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_message` | `role: str, content: str, **metadata` | `None` | Extracts entities from `metadata["entities"]` and tracks mention counts |
| `get_entity` | `name: str` | `dict \| None` | Looks up entity data by name |
| `get_messages` | -- | `list[dict[str, str]]` | Entity summary as system message + last 10 messages |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`hashlib`, `json`, `abc`, `dataclasses`, `datetime`, `enum`)

## Constraints

- All memories expose `to_json()` for serialization; no persistent storage built-in.
- `SummaryMemory._update_summary` is a no-op if `summarizer` is `None`.
- `EntityMemory` evicts the least-mentioned entity when `max_entities` is reached.
- Zero-mock: real data only; `NotImplementedError` for unimplemented paths.

## Error Handling

- `create_memory` raises `ValueError` for unsupported `MemoryType` values.
- All errors logged before propagation.
