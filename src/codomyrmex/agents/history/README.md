# history

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Conversation and context persistence for agent sessions. Provides data models for messages and conversations, three pluggable storage backends (in-memory, file-based JSON, SQLite), and a high-level `ConversationManager` that handles creation, truncation, search, and active-conversation tracking.

## Key Exports

- **`MessageRole`** -- Enum of standard conversation roles (system, user, assistant, tool, function)
- **`HistoryMessage`** -- Dataclass representing a single message with role, content, auto-generated ID via SHA-256, timestamp, token count, and metadata
- **`Conversation`** -- Dataclass for a full conversation with message list, add/truncate helpers, API-compatible message export, and dict serialization
- **`InMemoryHistoryStore`** -- In-memory conversation storage with save, load, delete, list (sorted by updated_at), and content search
- **`FileHistoryStore`** -- File-based JSON conversation storage with one JSON file per conversation on disk
- **`SQLiteHistoryStore`** -- SQLite-backed conversation storage with conversations and messages tables, indexed by conversation_id
- **`ConversationManager`** -- High-level manager that wraps any store, supports active-conversation tracking, auto-truncation at configurable message limits, and search

## Directory Contents

- `__init__.py` - All history logic: message/conversation models, three storage backends, conversation manager
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
