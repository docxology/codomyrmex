# llm/memory

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Conversation memory management for LLMs. Provides different memory strategies for maintaining context across conversations, ranging from simple full-history buffers to sliding windows, running summaries, and entity-tracking approaches.

## Key Exports

### Enums

- **`MemoryType`** -- Memory strategy types: `BUFFER`, `WINDOW`, `SUMMARY`, `VECTOR`, `ENTITY`

### Data Class

- **`MemoryMessage`** -- A message stored in memory with role, content, timestamp, metadata, and optional token count. Supports `to_dict()` and `from_dict()` serialization

### Abstract Base Class

- **`Memory`** -- ABC for conversation memory with auto-generated session IDs, `add_message()`, `get_messages()` (LLM API format), `clear()`, and convenience methods `add_user_message()`, `add_assistant_message()`, `add_system_message()`. Includes `to_json()` serialization and `message_count` property

### Memory Implementations

- **`BufferMemory`** -- Stores all messages with optional `max_messages` cap. When capacity is exceeded, preserves system messages and removes oldest non-system messages
- **`WindowMemory`** -- Sliding window keeping the last N messages (configurable `window_size`, default 10). System messages are stored separately and always included in output
- **`SummaryMemory`** -- Maintains a running summary of conversation history. Accumulates recent messages until a threshold is reached, then invokes a configurable `summarizer` callback to compress history. Returns the summary as a system message plus recent unsummarized messages
- **`EntityMemory`** -- Tracks named entities mentioned in conversations with mention counts and metadata. Manages capacity via `max_entities` (default 50), evicting least-mentioned entities. Prepends entity context as a system message and includes the last 10 conversation messages

### Factory Function

- **`create_memory()`** -- Create a memory instance by `MemoryType` enum with keyword arguments forwarded to the constructor

## Directory Contents

- `__init__.py` - Memory ABC, four implementations, message model, and factory function (310 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
