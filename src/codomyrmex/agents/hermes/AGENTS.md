# Codomyrmex Agents — src/codomyrmex/agents/hermes

**Version**: v2.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
This document coordinates operations for the Hermes agent module within the Codomyrmex ecosystem. The `hermes` module provides dual-backend scaled execution (CLI + Ollama fallback) and stateful, multi-turn conversational persistence for the NousResearch Hermes architecture.

## Operating Contracts

Universal protocols specific to this module:
1. **Zero-Mock Conformance**: This module is rigorously tested using real subprocess execution. Tests must either check availability and skip gracefully, or bypass binary requirements gracefully via valid bin proxies (like `echo`) without Python-level `MagicMock` patches.
2. **Dual-Backend Parity**: Features mapped to `HermesClient` must gracefully handle the capabilities of both the `hermes` CLI and the `ollama` CLI.
3. **Session Immutability**: Sessions stored via `SQLiteSessionStore` maintain append-only message sequences.
4. **MCP Alignment**: All new integrations must be mapped securely into `mcp_tools.py` using standard `@mcp_tool` abstractions and robust error catching.

## Key Sub-components

- **Client Engine** (`hermes_client.py`): Contains the auto-backend detection and prompt formulation logic. 
- **Database Engine** (`session.py`): Implementation of `InMemorySessionStore` and `SQLiteSessionStore` to offer persistent chat memory.
- **Protocol Bridge** (`mcp_tools.py`): The exposed surface for Claude and swarm orchestrators to manipulate Hermes instances.
- **Evolution Engine** (`evolution/`): Linked Git submodule containing DSPy GEPA optimization logic for prompt mutations.

## Agent Workflows

When coordinating with Hermes via MCP:
- Swarm agents should prefer `hermes_chat_session` when dealing with multi-step logical operations (to retain contextual thread history without re-submitting large texts).
- Swarm agents must use `hermes_status` heavily before attempting to use CLI-specific tools (`hermes_skills_list`), to determine if the local system is functioning on the standard binaries or the Ollama fallback.

## Dependencies
- Relies on global logging framework (`codomyrmex.logging_monitoring`).
- Relies on global configuration (`codomyrmex.agents.core.config`).

## Navigation Links
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
