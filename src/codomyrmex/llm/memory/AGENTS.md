# Codomyrmex Agents — src/codomyrmex/llm/memory

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Conversation memory management for LLM interactions. Provides pluggable memory strategies (buffer, sliding window, summary, entity) that maintain context across turns and serialize messages into the format expected by LLM APIs.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `MemoryType` | Enum: BUFFER, WINDOW, SUMMARY, VECTOR, ENTITY |
| `__init__.py` | `MemoryMessage` | Dataclass for a stored message (role, content, timestamp, metadata, token_count) |
| `__init__.py` | `Memory` | Abstract base class with `add_message`, `get_messages`, `clear`, JSON serialization |
| `__init__.py` | `BufferMemory` | Stores all messages up to optional `max_messages` limit; preserves system messages on eviction |
| `__init__.py` | `WindowMemory` | Sliding window keeping last N non-system messages; system messages stored separately |
| `__init__.py` | `SummaryMemory` | Maintains a running summary via a `summarizer` callable; flushes after `summary_threshold` messages |
| `__init__.py` | `EntityMemory` | Tracks named entities from message metadata; evicts least-mentioned when `max_entities` exceeded |
| `__init__.py` | `create_memory` | Factory function mapping `MemoryType` to concrete memory class |

## Operating Contracts

- `get_messages()` returns `list[dict[str, str]]` with `role` and `content` keys, compatible with OpenAI/Anthropic APIs.
- `BufferMemory` preserves system messages when trimming to `max_messages`.
- `SummaryMemory` requires an external `summarizer: Callable` -- it is not called if the summarizer is `None`.
- `EntityMemory` expects entity data in `metadata["entities"]` dict when calling `add_message`.
- Session IDs are auto-generated via SHA-256 hash of current timestamp if not provided.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`hashlib`, `json`, `abc`, `dataclasses`, `datetime`, `enum`)
- **Used by**: `codomyrmex.llm` parent module, agent conversation loops, `codomyrmex.agents.memory`

## Navigation

- **Parent**: [llm](../README.md)
- **Root**: [Root](../../../../README.md)
