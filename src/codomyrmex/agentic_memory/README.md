# agentic_memory

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Long-term memory system for AI agents with retrieval, persistence, and automatic pruning. Supports four memory types (episodic, semantic, procedural, working) with importance-weighted storage, keyword and embedding-based retrieval ranked by a combined relevance/recency/importance score, and multiple storage backends. Includes specialized memory subclasses for conversation history and knowledge/fact storage.

## Key Exports

### Enums

- **`MemoryType`** -- Memory classification: EPISODIC (specific experiences), SEMANTIC (general knowledge), PROCEDURAL (skills/procedures), WORKING (short-term active)
- **`MemoryImportance`** -- Importance levels: LOW (1), MEDIUM (2), HIGH (3), CRITICAL (4)

### Data Classes

- **`Memory`** -- A single memory unit with content, type, importance, optional embedding vector, metadata, timestamps, access count, age/recency scoring, and dict serialization/deserialization
- **`RetrievalResult`** -- Result of memory retrieval containing the memory, relevance score, recency score, importance score, and a weighted combined score (40% relevance, 30% recency, 30% importance)

### Storage Backends

- **`MemoryStore`** -- Abstract base class for memory storage; defines save, get, delete, and list_all operations
- **`InMemoryStore`** -- Thread-safe in-memory dictionary storage backend
- **`JSONFileStore`** -- Persistent JSON file storage backend that loads on init and saves on every write

### Core

- **`AgentMemory`** -- Main memory system with `remember()` to store memories, `recall()` to retrieve by query with optional type/importance filters, `forget()` to delete, and `get_context()` to format relevant memories for LLM prompts; supports keyword matching and cosine-similarity embedding search with automatic pruning when memory count exceeds limit
- **`ConversationMemory`** -- Specialized AgentMemory optimized for conversation history with `add_turn()` for role-based dialogue tracking
- **`KnowledgeMemory`** -- Specialized AgentMemory optimized for factual knowledge with `add_fact()` supporting source attribution and confidence scores

## Directory Contents

- `__init__.py` - Module definition with all memory classes, stores, and enums
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Detailed API documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/agentic_memory/](../../../docs/modules/agentic_memory/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
