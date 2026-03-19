# Codomyrmex Agents — src/codomyrmex/agents/hermes

**Version**: v2.4.0 | **Status**: Active | **Last Updated**: March 2026 (Sprint 34)

## Purpose

This document coordinates operations for the Hermes agent module within the Codomyrmex ecosystem. The `hermes` module provides dual-backend scaled execution (CLI + Ollama fallback), provider-agnostic routing, context compression, and stateful, multi-turn conversational persistence — now extended in v2.4.0 with **Knowledge Codification** (KI extraction / search / dedup), **Swarm Orchestration** (capability-based agent spawning, DAG topologies), and **P2P agent messaging** via `IntegrationBus`.

## Upstream Repositories

Codomyrmex draws on the following upstream projects for the Hermes layer:

| Repo | Role | URL |
| :--- | :--- | :--- |
| **outsourc-e/hermes-workspace** | Reference web UI frontend (Next.js PWA) — chat, memory, skills, files, terminal | [github.com/outsourc-e/hermes-workspace](https://github.com/outsourc-e/hermes-workspace) |
| **outsourc-e/hermes-agent** | Backend fork adding `hermes webapi` (FastAPI + SSE on port 8642) | [github.com/outsourc-e/hermes-agent](https://github.com/outsourc-e/hermes-agent) |
| **NousResearch/hermes-agent** | Upstream baseline CLI agent | [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) |
| **NousResearch/hermes-agent-self-evolution** | DSPy GEPA evolution submodule | [github.com/NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) |

When the `hermes webapi` backend is running (port 8642), the `hermes-workspace` PWA provides a full browser-based command center for Hermes sessions — complementing Codomyrmex's MCP-based headless agent access.

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
- **MCP Bridge** (`mcp_tools.py`): **41+ MCP tools** exposed to Claude and swarm orchestrators, including Sprint 34 knowledge codification and swarm orchestration tools. Execute/stream/batch/sampling/chat_session accept optional `hermes_skill` / `hermes_skills` (CLI `chat -s` preload; persisted on sessions).
- **Session Engine** (`session.py`): `InMemorySessionStore`, `SQLiteSessionStore` (FTS5 BM25), session `close()` KI lifecycle hook.
- **Knowledge Codification** (Sprint 34): `hermes_build_memory_graph`, `hermes_extract_ki`, `hermes_search_knowledge_items`, `hermes_deduplicate_ki`, `hermes_archive_sessions`.
- **Swarm Orchestration** (Sprint 34): `hermes_spawn_agent` (capability profile routing), backed by `AgentOrchestrator.spawn_agent` + `filter_tools`.
- **Template Library** (`templates/`): Parameterized prompt templates for code review, debugging, documentation, and task decomposition.
- **Evolution Engine** (`evolution/`): Linked Git submodule containing DSPy GEPA optimization logic for prompt mutations.
- **Discord Gateway** (`gateway/`): Native voice gateway with RTP capture, Opus decoding, and DAVE E2EE support.

## Agent Workflows

When coordinating with Hermes via MCP:

- Swarm agents should prefer `hermes_chat_session` when dealing with multi-step logical operations (to retain contextual thread history without re-submitting large texts).
- For third-party Hermes skill packs installed under `$HERMES_HOME/skills/`, pass `hermes_skill` or `hermes_skills` on the first `hermes_chat_session` turn (or on each `hermes_execute`) so the CLI receives `hermes chat -s …`; confirm names with `hermes_skills_list`. See [docs/agents/hermes/skills.md](../../../../docs/agents/hermes/skills.md).
- Swarm agents must use `hermes_status` before attempting CLI-specific tools to determine if the system runs on binaries or the Ollama fallback.
- Use `hermes_session_fork` to branch long-running tasks into isolated sub-threads without polluting the primary session.
- Use `hermes_session_export_md` for human-readable handoffs or archiving long-running complex traces.
- Use `hermes_batch_execute` for massive parallel data processing or unit test generation swarms.
- Use `hermes_session_stats` to monitor disk usage and trigger `hermes_archive_sessions` when the SQLite file grows over the configured threshold.
- Use `hermes_session_merge` to consolidate multiple research sessions into a single context for final synthesis.
- Use `hermes_rotation_status` to check the health of free LLM providers and monitor cooldown windows.
- **Knowledge Codification** (Sprint 34): use `hermes_extract_ki(session_id)` after high-quality sessions to persist insights; use `hermes_search_knowledge_items(topic)` to recall; use `hermes_deduplicate_ki()` periodically to keep the KI store clean; use `hermes_build_memory_graph()` to visualise concept relationships.
- **Swarm Orchestration** (Sprint 34): use `hermes_spawn_agent(role, task, capability_profile)` to dispatch tasks to specialist agents; combine with `orchestrator_run_dag` for Fan-Out / Fan-In / Pipeline / Broadcast topologies; use `events_send_to_agent` / `events_agent_inbox` for direct P2P messaging between agents.

## Dependencies

- Relies on global logging framework (`codomyrmex.logging_monitoring`).
- Relies on global configuration (`codomyrmex.agents.core.config`).
- Discord Voice requires `libopus` and `nacl` native dependencies.
- Web workspace UI requires the [`outsourc-e/hermes-agent`](https://github.com/outsourc-e/hermes-agent) fork (`hermes webapi`) and the [`outsourc-e/hermes-workspace`](https://github.com/outsourc-e/hermes-workspace) frontend (Node.js 22+ + pnpm).

## Navigation Links

- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
- **🌐 Upstream Web UI**: [outsourc-e/hermes-workspace](https://github.com/outsourc-e/hermes-workspace)
- **🔧 Upstream Backend Fork**: [outsourc-e/hermes-agent](https://github.com/outsourc-e/hermes-agent)
