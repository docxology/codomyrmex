# PAI Access Matrix - Hermes Agent

Provides interactive and autonomous task execution via NousResearch Hermes. Supports dual backends: Hermes CLI and Ollama (hermes3). v2.2.0 adds Discord voice support and advanced session orchestration. Draws on [`outsourc-e/hermes-workspace`](https://github.com/outsourc-e/hermes-workspace) as the upstream browser-based workspace frontend (NextJS PWA, port 3000) backed by the [`outsourc-e/hermes-agent`](https://github.com/outsourc-e/hermes-agent) WebAPI fork (FastAPI, port 8642).

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
| :--- | :--- | :--- | :--- |
| **Engineer** | Full | `hermes_execute` (optional `hermes_skill` / `hermes_skills`), `hermes_chat_session`, `hermes_batch_execute`, `hermes_session_fork`, `hermes_status` | TRUSTED |
| **Architect** | Read + Config | `hermes_status`, `hermes_session_stats`, `hermes_insights` | OBSERVED |
| **QATester** | Tests | `hermes_execute`, `hermes_session_detail` | OBSERVED |
| **Researcher** | Read-only | `hermes_status`, `hermes_session_search`, `hermes_skills_list` | OBSERVED |

## Configuration

| Key | Default | Description |
| :--- | :--- | :--- |
| `hermes_backend` | `auto` | `auto` / `cli` / `ollama` |
| `hermes_model` | `hermes3` | Ollama model name |
| `hermes_timeout` | `120` | Subprocess timeout (s) |
| `hermes_session_db` | `~/.codomyrmex/hermes_sessions.db` | Session database path |
| `hermes_webapi_url` | `http://127.0.0.1:8642` | WebAPI backend URL (hermes-workspace upstream) |

## Use Cases

- **Autonomous Workflows**: Multi-turn task execution with auto-heal loops.
- **Discord Voice**: Real-time RTP listening and TTS in voice channels.
- **Deep Session Recall**: FTS5 search and Markdown export of long conversations.
- **Swarm Coordination**: Exposing 40+ MCP tools to sibling agents (Claude, Jules).
- **CLI skill preload**: Third-party Hermes packs under `$HERMES_HOME/skills/` (e.g. [PrediHermes](https://github.com/nativ3ai/hermes-geopolitical-market-sim)) via MCP `hermes_skill` / `hermes_skills`; see [skills.md](../../../../docs/agents/hermes/skills.md) (Codomyrmex MCP section).
- **Git Isolation**: Automated Git worktrees for isolated session execution.
- **Evolutionary Tuning**: Self-improvement via GEPA and DSPy submodules.
- **Browser Workspace**: Full web UI via [`outsourc-e/hermes-workspace`](https://github.com/outsourc-e/hermes-workspace) — chat, memory, skills, file browser, and PTY terminal in a PWA on `localhost:3000`. Requires `hermes webapi` running from the [`outsourc-e/hermes-agent`](https://github.com/outsourc-e/hermes-agent) fork.
