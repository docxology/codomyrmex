# PAI Access Matrix - Hermes Agent

Provides interactive and autonomous task execution via NousResearch Hermes. Supports dual backends: Hermes CLI and Ollama (hermes3). v2.2.0 adds Discord voice support and advanced session orchestration.

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
| :--- | :--- | :--- | :--- |
| **Engineer** | Full | `hermes_execute`, `hermes_chat_session`, `hermes_batch_execute`, `hermes_session_fork`, `hermes_status` | TRUSTED |
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

## Use Cases

- **Autonomous Workflows**: Multi-turn task execution with auto-heal loops.
- **Discord Voice**: Real-time RTP listening and TTS in voice channels.
- **Deep Session Recall**: FTS5 search and Markdown export of long conversations.
- **Swarm Coordination**: Exposing 34+ tools to brother agents (Claude, Jules).
- **Git Isolation**: Automated Git worktrees for isolated session execution.
- **Evolutionary Tuning**: Self-improvement via GEPA and DSPy submodules.
