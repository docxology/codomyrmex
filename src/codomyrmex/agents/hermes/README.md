# Hermes Agent Module

**Version**: v2.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Hermes Agent Module integrates NousResearch's Hermes capabilities deeply into the Codomyrmex ecosystem. Designed for maximum reliability and local-first execution, it provides dual-backend scaling, persistent multi-turn chat, and specialized prompt templating.

## Core Features

1. **Dual-Backend Auto-Detection**: 
   The module seamlessly targets either the official `hermes` CLI binary or a local `ollama` instance (defaulting to the `hermes3` model). This fallback ensures the agent is strictly available on local developer machines even without the custom CLI.

2. **Persistent Stateful Chat**:
   Using `SQLiteSessionStore`, the module tracks multi-turn conversational history natively. Both local Python scripts and remote MCP agents can append to ongoing conversational threads without needing to juggle context windows manually.

3. **Evolutionary Submodule**:
   The `evolution/` directory contains the `hermes-agent-self-evolution` submodule, implementing DSPy-based Genetic-Pareto (GEPA) optimization to continuously harden and improve the agent's prompts and skills based on real execution traces.

4. **MCP Tool Suite**:
   Provides 9 comprehensive Model Context Protocol tools, granting Claude and other swarm agents full capability to invoke, manage, and trace Hermes operations.

## Directory Structure

- `hermes_client.py`: The `HermesClient` concrete agent subclass.
- `session.py`: Persistent SQLite tracking (`HermesSession`, `SQLiteSessionStore`).
- `mcp_tools.py`: Model Context Protocol tools, e.g., `hermes_chat_session`.
- `templates/`: Built-in template registries (System Prompts, Debugging, Code Review).
- `scripts/`: Operational scripts (`run_hermes.py`).
- `evolution/`: Genetic self-improvement subsystem.

## Navigation
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
