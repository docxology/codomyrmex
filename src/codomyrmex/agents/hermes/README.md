# Hermes Agent Module

**Version**: v2.2.1 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Hermes Agent Module integrates NousResearch's Hermes capabilities deeply into the Codomyrmex ecosystem. Designed for maximum reliability and local-first execution, it provides dual-backend scaling, persistent multi-turn chat, provider-agnostic routing, context compression, and specialized prompt templating. v2.2.1 adds LLM rotation for free models, cooldown tracking, and advanced session merging.

> **Upstream**: [`outsourc-e/hermes-workspace`](https://github.com/outsourc-e/hermes-workspace) is the reference web workspace frontend for Hermes. Codomyrmex draws on it as the upstream for the web UI layer — chat, memory browser, skills explorer, file browser, and terminal — backed by the [`outsourc-e/hermes-agent`](https://github.com/outsourc-e/hermes-agent) fork that adds the WebAPI (`hermes webapi`, FastAPI on port 8642).

## Core Features

1. **Dual-Backend Auto-Detection**:
   The module seamlessly targets either the official `hermes` CLI binary or a local `ollama` instance (defaulting to the `hermes3` model). This fallback ensures the agent is strictly available on local developer machines even without the custom CLI.

2. **Persistent Stateful Chat**:
   Using `SQLiteSessionStore`, the module tracks multi-turn conversational history natively. v2.2.1 adds advanced orchestration: session forking, session merging, rich metrics, search via FTS5, and automated lifecycle management.

3. **Discord Voice Support**:
   Native gateway runner with RTP capture, Opus decoding, and DAVE E2EE decryption for real-time interaction in Discord voice channels via `/voice` commands.

4. **Batch Execution**:
   A robust sequential or parallel multi-prompt execution engine with `HermesClient.batch_execute()`, allowing for massive swarm-scale data processing.

5. **CLI skill preload**:
   Optional `hermes_skill` / `hermes_skills` on MCP tools (`hermes_execute`, `hermes_stream`, `hermes_chat_session`, `hermes_batch_execute`, `hermes_sampling`) map to `hermes chat -s` (comma-separated names). Stateful sessions persist the list in metadata. No effect when the active backend is Ollama.

6. **Free LLM Rotation**:
   A robust non-git-tracked model rotation strategy for free OpenRouter models (Gemini, DeepSeek, Llama). Includes persistent cooldown tracking on rate limits (429) for maximum uptime.

7. **Provider Router**:
   `ProviderRouter` provides a unified `call_llm()` abstraction across multiple providers (OpenRouter, Ollama, Anthropic, OpenAI, z.ai, Nous). Credentials are auto-resolved from environment and `~/.hermes/.env`.

8. **Context Compression**:
   `ContextCompressor` auto-compresses conversation context when it exceeds token limits using progressive deduplication, summarization, and truncation strategies.

9. **Cross-Session User Model**:
   `UserModel` persists user preferences, coding style observations, and session summaries across sessions — enabling contextual continuity.

10. **Git Worktree Isolation**:
   Create isolated git worktrees per session for parallel agent execution without branch conflicts.

11. **Evolutionary Submodule**:
    The `evolution/` directory contains the `hermes-agent-self-evolution` submodule, implementing DSPy-based Genetic-Pareto (GEPA) optimization.

12. **MCP Tool Suite**:
    Provides 37+ comprehensive Model Context Protocol tools — mapping core, session, diagnostic, and administration features to the swarm.

## Directory Structure

- `hermes_client.py`: The `HermesClient` concrete agent subclass (dual-backend, sessions, worktrees, CLI flags, batch execution).
- `_provider_router.py`: `ProviderRouter`, `UserModel`, `ContextCompressor`, `MCPBridgeManager`.
- `session.py`: Persistent SQLite tracking (`HermesSession`, `SQLiteSessionStore`) with FTS5 and archiving.
- `mcp_tools.py`: 37+ Model Context Protocol tools.
- `templates/`: Built-in template registries (code review, debugging, documentation, task decomposition, and rotation).
- `scripts/`: Operational scripts (`run_chat.py`, `run_batch.py`, `run_session_export.py`, `run_prune.py`, `run_health.py`, etc.).
- `evolution/`: Genetic self-improvement subsystem.
- `gateway/`: Discord voice gateway integration.

## Web Workspace (hermes-workspace upstream)

[`outsourc-e/hermes-workspace`](https://github.com/outsourc-e/hermes-workspace) is the upstream reference web UI for the Hermes Agent. It is a Next.js PWA that connects to the Hermes WebAPI backend on `http://localhost:8642`.

### Features (upstream)

| Feature | Description |
| :--- | :--- |
| **💬 Chat** | Real-time SSE streaming, multi-session management, markdown + syntax highlighting |
| **🧠 Memory** | Browse and edit agent memory files; search across entries |
| **🧩 Skills** | Browse 2,000+ skills from the registry; per-session management |
| **📁 Files** | Full workspace file browser; Monaco editor integration |
| **💻 Terminal** | Full PTY terminal with persistent shell sessions |
| **🎨 Themes** | 8 themes (Official, Classic, Slate, Mono — light and dark variants each) |
| **🔒 Security** | Auth middleware, CSP headers, path traversal prevention, rate limiting |
| **📱 Mobile PWA** | Full feature parity via Tailscale on iOS/Android |

### Quick Start (connecting hermes-workspace)

```bash
# 1. Start the Hermes WebAPI backend (requires outsourc-e/hermes-agent fork)
hermes webapi        # FastAPI on http://localhost:8642

# 2. Clone and run the workspace frontend
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace && pnpm install
cp .env.example .env
printf '\nHERMES_API_URL=http://127.0.0.1:8642\n' >> .env
pnpm dev             # http://localhost:3000
```

### Backend Fork Relationship

```text
NousResearch/hermes-agent        ← upstream baseline (CLI only)
        └── outsourc-e/hermes-agent   ← fork adding `hermes webapi` (FastAPI + SSE)
                └── outsourc-e/hermes-workspace ← frontend PWA consuming the WebAPI
                        └── Codomyrmex Hermes module ← draws on both as upstream
```

The `HermesClient` wraps the CLI backend; the WebAPI layer enables the web workspace UI. Environment variables shared: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY` in `~/.hermes/.env`.

## Navigation

- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
- **Upstream Web UI**: [outsourc-e/hermes-workspace](https://github.com/outsourc-e/hermes-workspace)
- **Upstream Backend Fork**: [outsourc-e/hermes-agent](https://github.com/outsourc-e/hermes-agent)
