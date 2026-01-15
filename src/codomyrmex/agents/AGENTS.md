# Codomyrmex Agents — src/codomyrmex/agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Agent integration framework providing unified interfaces for CLI-based (Jules, Gemini, OpenCode, Mistral Vibe, Every Code) and API-based (Claude, Codex) AI agents. Includes base classes, orchestration, and Codomyrmex module adapters.

## Active Components
- `AGENT_COMPARISON.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `ai_code_editing/` – Directory containing ai_code_editing components
- `claude/` – Directory containing claude components
- `cli/` – Directory containing CLI handlers and utilities
- `codex/` – Directory containing codex components
- `core/` – Directory containing core agent logic (formerly core.py, config.py)
- `droid/` – Directory containing droid components
- `every_code/` – Directory containing every_code components
- `gemini/` – Directory containing gemini components
- `generic/` – Directory containing generic components
- `jules/` – Directory containing jules components
- `mistral_vibe/` – Directory containing mistral_vibe components
- `opencode/` – Directory containing opencode components
- `theory/` – Directory containing theory components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation
