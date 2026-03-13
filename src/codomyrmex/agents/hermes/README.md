# Hermes Agent Module

**Version**: v2.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Hermes Agent Module integrates NousResearch's Hermes capabilities deeply into the Codomyrmex ecosystem. Designed for maximum reliability and local-first execution, it provides dual-backend scaling, persistent multi-turn chat, provider-agnostic routing, context compression, and specialized prompt templating.

## Core Features

1. **Dual-Backend Auto-Detection**: 
   The module seamlessly targets either the official `hermes` CLI binary or a local `ollama` instance (defaulting to the `hermes3` model). This fallback ensures the agent is strictly available on local developer machines even without the custom CLI.

2. **Persistent Stateful Chat**:
   Using `SQLiteSessionStore`, the module tracks multi-turn conversational history natively. Both local Python scripts and remote MCP agents can append to ongoing conversational threads without needing to juggle context windows manually.

3. **Provider Router**:
   `ProviderRouter` provides a unified `call_llm()` abstraction across multiple providers (OpenRouter, Ollama, Anthropic, OpenAI, z.ai, Nous). Credentials are auto-resolved from environment and `~/.hermes/.env`.

4. **Context Compression**:
   `ContextCompressor` auto-compresses conversation context when it exceeds token limits using progressive deduplication, summarization, and truncation strategies.

5. **Cross-Session User Model**:
   `UserModel` persists user preferences, coding style observations, and session summaries across sessions — enabling contextual continuity.

6. **MCP Bridge (Hot-Reload)**:
   `MCPBridgeManager` manages MCP server configurations with hot-reload support — no session restart required.

7. **Git Worktree Isolation**:
   Create isolated git worktrees per session for parallel agent execution without branch conflicts.

8. **Evolutionary Submodule**:
   The `evolution/` directory contains the `hermes-agent-self-evolution` submodule, implementing DSPy-based Genetic-Pareto (GEPA) optimization.

9. **MCP Tool Suite**:
   Provides 20 comprehensive Model Context Protocol tools (see SPEC.md for the full inventory).

## Directory Structure

- `hermes_client.py`: The `HermesClient` concrete agent subclass (dual-backend, sessions, worktrees, CLI flags).
- `_provider_router.py`: `ProviderRouter`, `UserModel`, `ContextCompressor`, `MCPBridgeManager`.
- `session.py`: Persistent SQLite tracking (`HermesSession`, `SQLiteSessionStore`).
- `mcp_tools.py`: 20 Model Context Protocol tools.
- `templates/`: Built-in template registries (code review, debugging, documentation, task decomposition).
- `scripts/`: Operational scripts (`run_chat.py`, `run_session.py`, etc.).
- `evolution/`: Genetic self-improvement subsystem.

## Navigation
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
