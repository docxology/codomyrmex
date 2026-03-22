# Codomyrmex Agents — src/codomyrmex/agents/hermes

**Version**: v2.5.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

This document coordinates operations for the Hermes agent module within the Codomyrmex ecosystem. The `hermes` module provides dual-backend scaled execution (CLI + Ollama fallback), provider-agnostic routing, context compression, and stateful, multi-turn conversational persistence. v2.5.0 adds a **Plugin System** (`hermes plugins`), **@ Context References** for inline file/git/URL injection, a **Gateway Agent Cache** for per-session AIAgent reuse, **Mattermost** messaging integration, and optional **meme-generation** and **bioinformatics** skills.

## Operating Contracts

Universal protocols specific to this module:

1. **Zero-Mock Conformance**: This module is rigorously tested using real subprocess execution. Tests must either check availability and skip gracefully, or bypass binary requirements gracefully via valid bin proxies (like `echo`) without Python-level `MagicMock` patches.
2. **Dual-Backend Parity**: Features mapped to `HermesClient` must gracefully handle the capabilities of both the `hermes` CLI and the `ollama` CLI.
3. **Session Immutability**: Sessions stored via `SQLiteSessionStore` maintain append-only message sequences.
4. **MCP Alignment**: All new integrations must be mapped securely into `mcp_tools.py` using standard `@mcp_tool` abstractions and robust error catching.
5. **Provider Resilience**: `ProviderRouter` must resolve credentials from environment → `.env` → auto-discovery, with fallback on failure.
6. **Discord Voice Security**: Native `VoiceReceiver` handles RTP DAVE E2EE per-user keys securely.

## Key Sub-components

- **Client Engine** (`hermes_client.py`): Auto-backend detection, prompt formulation, CLI flag support (`--yolo`, `--continue`, `--pass-session-id`), context compression integration, batch execution.
- **Provider Router** (`_provider_router.py`): Unified `call_llm()` abstraction across 6 providers, with automatic credential resolution and fallback.
- **Context Compressor** (`_provider_router.py`): Progressive conversation compression triggered at configurable token thresholds.
- **User Model** (`_provider_router.py`): Cross-session user context persistence — preferences, observations, session summaries backed by JSON.
- **MCP Bridge** (`mcp_tools.py`): **50** `@mcp_tool` entries; skill-interop tools carry `tags` for PAI manifest indexing (`skills`, `cli_preload`, `interop`).
- **Plugin Manager** (`hermes_cli/plugins_cmd.py`, v2.5.0): `hermes plugins install/update/remove/list` manages Git-sourced plugins in `~/.hermes/plugins/`. Reads `plugin.yaml` manifest, validates `manifest_version`, copies `.example` files, renders `after-install.md` via Rich. Path traversal protection enforced.
- **@ Context References** (`agent/context_references.py`, v2.5.0): Parses `@file:`, `@folder:`, `@diff`, `@staged`, `@git:N`, `@url:` tokens from messages and expands them to attached context blocks. Token budget enforced (50% hard, 25% soft). Async-safe (sync wrapper for CLI, thread pool for gateway).
- **Gateway Agent Cache** (`gateway/run.py`, v2.5.0): `GatewayRunner` caches `AIAgent` per session via config signature (MD5 of model + provider + toolsets + system_prompt). Same-config reuse freezes system prompt. `reasoning_config` and callbacks update in-place. Thread-safe via `_agent_cache_lock`.
- **Unified skill registry** (`skill_registry.py`, `data/skills_registry.yaml`): stable `skill_ids` → Hermes `-s` names; project profile `.codomyrmex/hermes_skills_profile.yaml`; optional `CODOMYRMEX_SKILLS_REGISTRY` overlay.
- **Session Engine** (`session.py`): `InMemorySessionStore`, `SQLiteSessionStore` (FTS5 BM25), session `close()` KI lifecycle hook.
- **Knowledge Codification** (Sprint 34): `hermes_build_memory_graph`, `hermes_extract_ki`, `hermes_search_knowledge_items`, `hermes_deduplicate_ki`, `hermes_archive_sessions`.
- **Swarm Orchestration** (Sprint 34): `hermes_spawn_agent` (capability profile routing), backed by `AgentOrchestrator.spawn_agent` + `filter_tools`.
- **Template Library** (`templates/`): Parameterized prompt templates for code review, debugging, documentation, and task decomposition.
- **Instance Templates** (`instance_templates/`): Config template, `.env.example`, `SOUL.md` persona, and `hermes_example.py`.
- **Spawn Script** (`scripts/spawn_instance.sh`): One-shot instance creation script.
- **Evolution Engine** (`evolution/`): DSPy GEPA optimization for prompt mutations.
- **Multi-Platform Gateway** (`gateway/`): Telegram, Discord (voice/text), WhatsApp, Mattermost (v2.5.0). Native RTP/DAVE E2EE for Discord voice.

## Agent Workflows

When coordinating with Hermes via MCP:

- Prefer `hermes_chat_session` for multi-step logical operations (retains contextual thread history).
- Use `hermes_status` before CLI-specific tools to determine backend (binary vs. Ollama).
- Use `hermes_session_fork` to branch long-running tasks into isolated sub-threads.
- Use `hermes_session_export_md` for human-readable handoffs or archiving.
- Use `hermes_batch_execute` for parallel data processing or test generation swarms.
- Use `hermes_session_stats` to monitor disk usage; trigger `hermes_archive_sessions` when SQLite grows large.
- Use `hermes_session_merge` to consolidate multiple research sessions into one context.
- Use `hermes_rotation_status` to check free LLM provider health and cooldown windows.
- **Plugins (v2.5.0)**: use `hermes_plugins_install(identifier)` to add a plugin; `hermes_plugins_list()` to see installed plugins. Restart the gateway after install: `hermes gateway restart`.
- **@ Context References (v2.5.0)**: in gateway messages, use `@file:src/main.py` to attach full file, `@file:path:10-50` for line ranges, `@diff` for unstaged changes, `@url:https://docs.example.com/api` to inject web content. Stay under 25% of context window to avoid warnings, 50% to avoid blocking.
- **Knowledge Codification** (Sprint 34): use `hermes_extract_ki(session_id)` after high-quality sessions; `hermes_search_knowledge_items(topic)` to recall; `hermes_deduplicate_ki()` periodically; `hermes_build_memory_graph()` to visualise.
- **Swarm Orchestration** (Sprint 34): use `hermes_spawn_agent(role, task, capability_profile)` to dispatch; combine with `orchestrator_run_dag` for Fan-Out/Fan-In/Pipeline topologies; use `events_send_to_agent` / `events_agent_inbox` for P2P messaging.

## Dependencies

- Relies on global logging framework (`codomyrmex.logging_monitoring`).
- Relies on global configuration (`codomyrmex.agents.core.config`).
- Discord Voice requires `libopus` and `nacl` native dependencies.

## Navigation Links

- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) — MCP surface and tags
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
