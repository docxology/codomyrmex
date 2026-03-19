# Hermes Documentation — Agent Coordination

**Module**: `docs/agents/hermes/` | **Version**: v0.3.0 | **Last Updated**: March 2026 (73-commit update)

## Purpose

Agent coordination document for the Hermes documentation subfolder. Guides AI agents navigating Hermes-related documentation and scripts.

## Documentation Files (22)

Includes **`assets/README.md`** for optional static diagram exports (primary diagrams are Mermaid blocks in the Markdown files below).

### Getting Started

| File               | Description                                      |
| :----------------- | :----------------------------------------------- |
| `README.md`        | Index, overview, and quick start                 |
| `setup_guide.md`   | Complete new-instance setup (from official docs) |
| `cli_reference.md` | All CLI commands and slash commands              |

### Architecture & Configuration

| File                        | Description                                        |
| :-------------------------- | :------------------------------------------------- |
| `architecture.md`           | Core agent loop, components, LLM provider backends |
| `codomyrmex_integration.md` | Deep dive into Codomyrmex interfaces and MCP       |
| `configuration.md`          | config.yaml reference, YAML pitfalls               |
| `copilot_acp.md`            | GitHub Copilot ACP backend (v0.3.0)                |
| `environment.md`            | HERMES_HOME, .env, API key management              |
| `models.md`                 | Model selection, OpenRouter, providers             |
| `personalities.md`          | Personality system and custom personas             |

### Platform Integration

| File                | Description                            |
| :------------------ | :------------------------------------- |
| `gateway.md`        | Gateway daemon, platform adapters      |
| `telegram.md`       | Telegram bot setup, 409 Conflict fixes |
| `launchd.md`        | macOS launchd service management       |
| `multi_instance.md` | Multi-bot deployment patterns          |

### Agent Capabilities

| File          | Description                           |
| :------------ | :------------------------------------ |
| `sessions.md` | Session lifecycle, state.db, FTS5     |
| `skills.md`   | Hermes skills + Codomyrmex unified registry, profile, MCP merge |
| `tools.md`    | Tool registry, MCP integration        |
| `cron.md`     | Scheduled jobs, proactive messaging   |

### Operations

| File                 | Description                           |
| :------------------- | :------------------------------------ |
| `troubleshooting.md` | 9 issue patterns with diagnosis/fixes |
| `security.md`        | API key hygiene, access control       |

## Scripts (`scripts/agents/hermes/`)

| Script                      | Purpose                                      |
| :-------------------------- | :------------------------------------------- |
| `new_instance.py`           | Create fully-configured new Hermes instances |
| `setup_hermes.py`           | Validate environment, config, backends       |
| `run_hermes.py`             | Send prompt, get response                    |
| `dispatch_hermes.py`        | Sweep-and-dispatch orchestrator              |
| `observe_hermes.py`         | Session observability                        |
| `evaluate_orchestrators.py` | Thin orchestrator evaluation                 |
| `prompt_context.py`         | Project-aware context builder                |

## Diagram conventions (Mermaid)

Hermes docs use **flowchart** / **graph** / **sequenceDiagram** blocks. Prefer `subgraph graphId [Visible label]` (explicit id + bracket label), avoid reserved-looking node ids such as `end`, avoid hard-coded `classDef` / theme colors so diagrams stay readable in light and dark themes, and wire **named nodes** only (do not reference a subgraph alias as if it were a node).

## Operating Contracts

1. **Official Source of Truth**: [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)
2. **HERMES_HOME Isolation**: Each instance must have its own `HERMES_HOME` directory
3. **Unique Bot Tokens**: Each Telegram/Discord/WhatsApp gateway must use a unique token
4. **Secret Hygiene**: API keys in `.env` only, `chmod 600`, never commit
5. **Zero Duplicate YAML Keys**: `config.yaml` must never have duplicate top-level keys
6. **`--replace` Flag**: Always use in launchd plists for PID management
7. **`security.redact_secrets: true`**: Always set in production
8. **Tirith Policy Engine**: Enable `tirith_enabled: true` for production deployments
9. **Codomyrmex skill preload**: Project defaults come from `.codomyrmex/hermes_skills_profile.yaml` (cwd walk), optional `CODOMYRMEX_SKILLS_REGISTRY`, and `HermesClient` config — see [skills.md](skills.md); **Ollama** fallback does not load Hermes skill packs

## Navigation

- **Parent**: [docs/agents/AGENTS.md](../AGENTS.md)
- **Source**: [src/codomyrmex/agents/hermes/AGENTS.md](../../../src/codomyrmex/agents/hermes/AGENTS.md)
- **Project Root**: [AGENTS.md](../../../AGENTS.md)
