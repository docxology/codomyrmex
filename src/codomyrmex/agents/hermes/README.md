# Hermes Agent Module

**Version**: v2.2.1 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Hermes Agent Module integrates NousResearch's Hermes capabilities deeply into the Codomyrmex ecosystem. Designed for maximum reliability and local-first execution, it provides dual-backend scaling, persistent multi-turn chat, provider-agnostic routing, context compression, and specialized prompt templating. v2.2.1 adds LLM rotation for free models, cooldown tracking, and advanced session merging.

## Core Features

1. **Dual-Backend Auto-Detection**:
   The module seamlessly targets either the official `hermes` CLI binary or a local `ollama` instance (defaulting to the `hermes3` model). This fallback ensures the agent is strictly available on local developer machines even without the custom CLI.

2. **Persistent Stateful Chat**:
   Using `SQLiteSessionStore`, the module tracks multi-turn conversational history natively. v2.2.1 adds advanced orchestration: session forking, session merging, rich metrics, search via FTS5, and automated lifecycle management.

3. **Discord Voice Support**:
   Native gateway runner with RTP capture, Opus decoding, and DAVE E2EE decryption for real-time interaction in Discord voice channels via `/voice` commands.

4. **Batch Execution**:
   A robust sequential or parallel multi-prompt execution engine with `HermesClient.batch_execute()`, allowing for massive swarm-scale data processing.

5. **Free LLM Rotation**:
   A robust non-git-tracked model rotation strategy for free OpenRouter models (Gemini, DeepSeek, Llama). Includes persistent cooldown tracking on rate limits (429) for maximum uptime.

6. **Provider Router**:
   `ProviderRouter` provides a unified `call_llm()` abstraction across multiple providers (OpenRouter, Ollama, Anthropic, OpenAI, z.ai, Nous). Credentials are auto-resolved from environment and `~/.hermes/.env`.

7. **Context Compression**:
   `ContextCompressor` auto-compresses conversation context when it exceeds token limits using progressive deduplication, summarization, and truncation strategies.

8. **Cross-Session User Model**:
   `UserModel` persists user preferences, coding style observations, and session summaries across sessions — enabling contextual continuity.

9. **Git Worktree Isolation**:
   Create isolated git worktrees per session for parallel agent execution without branch conflicts.

10. **Evolutionary Submodule**:
    The `evolution/` directory contains the `hermes-agent-self-evolution` submodule, implementing DSPy-based Genetic-Pareto (GEPA) optimization.

11. **MCP Tool Suite**:
    48 `@mcp_tool` definitions in `mcp_tools.py` (see [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)); unified skill registry in `skill_registry.py` + `data/skills_registry.yaml`.

## Directory Structure

- `hermes_client.py`: The `HermesClient` concrete agent subclass (dual-backend, sessions, worktrees, CLI flags, batch execution).
- `_provider_router.py`: `ProviderRouter`, `UserModel`, `ContextCompressor`, `MCPBridgeManager`.
- `session.py`: Persistent SQLite tracking (`HermesSession`, `SQLiteSessionStore`) with FTS5 and archiving.
- `mcp_tools.py`: Model Context Protocol tools (`MCP_TOOL_SPECIFICATION.md`).
- `templates/`: Built-in template registries (code review, debugging, documentation, task decomposition, and rotation).
- `scripts/`: Operational scripts (`run_chat.py`, `run_batch.py`, `run_session_export.py`, `run_prune.py`, `run_health.py`, etc.).
- `evolution/`: Genetic self-improvement subsystem.
- `gateway/`: Discord voice gateway integration.

## Navigation

- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
