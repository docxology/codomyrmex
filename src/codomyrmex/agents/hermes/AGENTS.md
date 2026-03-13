# Codomyrmex Agents — src/codomyrmex/agents/hermes

**Version**: v2.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
This document coordinates operations for the Hermes agent module within the Codomyrmex ecosystem. The `hermes` module provides dual-backend scaled execution (CLI + Ollama fallback), provider-agnostic routing, context compression, and stateful, multi-turn conversational persistence for the NousResearch Hermes architecture.

## Operating Contracts

Universal protocols specific to this module:
1. **Zero-Mock Conformance**: This module is rigorously tested using real subprocess execution. Tests must either check availability and skip gracefully, or bypass binary requirements gracefully via valid bin proxies (like `echo`) without Python-level `MagicMock` patches.
2. **Dual-Backend Parity**: Features mapped to `HermesClient` must gracefully handle the capabilities of both the `hermes` CLI and the `ollama` CLI.
3. **Session Immutability**: Sessions stored via `SQLiteSessionStore` maintain append-only message sequences.
4. **MCP Alignment**: All new integrations must be mapped securely into `mcp_tools.py` using standard `@mcp_tool` abstractions and robust error catching.
5. **Provider Resilience**: `ProviderRouter` must resolve credentials from environment → `.env` → auto-discovery, with fallback on failure.

## Key Sub-components

- **Client Engine** (`hermes_client.py`): Auto-backend detection, prompt formulation, CLI flag support (`--yolo`, `--continue`, `--pass-session-id`), context compression integration.
- **Provider Router** (`_provider_router.py`): Unified `call_llm()` abstraction across 6 providers, with automatic credential resolution and fallback.
- **Context Compressor** (`_provider_router.py`): Progressive conversation compression (deduplication → summarization → truncation) triggered at configurable token thresholds.
- **User Model** (`_provider_router.py`): Cross-session user context persistence — preferences, observations, session summaries backed by JSON.
- **MCP Bridge** (`_provider_router.py`): Hot-reload MCP server configuration without session restart.
- **Database Engine** (`session.py`): `InMemorySessionStore` and `SQLiteSessionStore` for persistent chat memory, named sessions, session search, and fork lineage.
- **Protocol Bridge** (`mcp_tools.py`): 20 MCP tools exposed to Claude and swarm orchestrators.
- **Template Library** (`templates/`): Parameterized prompt templates for code review, debugging, documentation, and task decomposition.
- **Evolution Engine** (`evolution/`): Linked Git submodule containing DSPy GEPA optimization logic for prompt mutations.

## Agent Workflows

When coordinating with Hermes via MCP:
- Swarm agents should prefer `hermes_chat_session` when dealing with multi-step logical operations (to retain contextual thread history without re-submitting large texts).
- Swarm agents must use `hermes_status` heavily before attempting to use CLI-specific tools (`hermes_skills_list`), to determine if the local system is functioning on the standard binaries or the Ollama fallback.
- Use `hermes_provider_status` to check available providers before making provider-specific calls.
- Use `hermes_session_search` to find sessions by name instead of iterating `hermes_session_list`.
- Use `hermes_honcho_status` to verify Honcho memory integration before relying on cross-session context.

## Dependencies
- Relies on global logging framework (`codomyrmex.logging_monitoring`).
- Relies on global configuration (`codomyrmex.agents.core.config`).

## Navigation Links
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
