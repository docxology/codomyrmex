# Hermes Documentation — Agent Coordination

**Module**: `docs/agents/hermes/` | **Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

## Purpose

Agent coordination document for the Hermes documentation subfolder. Guides AI agents navigating Hermes-related documentation and scripts.

## Documentation files (29)

Twenty-eight topical Markdown files in this folder plus **`assets/README.md`** (optional diagram exports; primary diagrams are Mermaid in the guides below). Hermes doc suite version **v0.4.0** applies to this folder; Copilot ACP is documented under `copilot_acp.md` at that same suite revision unless upstream release notes say otherwise.

### Index

| File | Description |
| :--- | :--- |
| `README.md` | Overview, quick start, documentation map |
| `AGENTS.md` | This coordination file |

### Getting started

| File | Description |
| :--- | :--- |
| `setup_guide.md` | New-instance setup (aligned with official docs) |
| `cli_reference.md` | CLI and slash commands |

### Architecture and configuration

| File | Description |
| :--- | :--- |
| `architecture.md` | Agent loop, components, LLM backends |
| `copilot_acp.md` | GitHub Copilot ACP backend |
| `codomyrmex_integration.md` | Codomyrmex interfaces and MCP |
| `configuration.md` | `config.yaml`, YAML pitfalls |
| `environment.md` | `HERMES_HOME`, `.env`, API keys |
| `models.md` | Model selection, providers, limits |
| `personalities.md` | Personas |

### Platform integration

| File | Description |
| :--- | :--- |
| `gateway.md` | Gateway daemon and adapters |
| `telegram.md` | Telegram setup and 409 Conflict |
| `launchd.md` | macOS `launchd` |
| `multi_instance.md` | Multiple bots on one host |

### Agent capabilities

| File | Description |
| :--- | :--- |
| `sessions.md` | Sessions, `state.db`, FTS5 |
| `skills.md` | Skills + Codomyrmex registry, profile, MCP merge |
| `tools.md` | Tool registry, MCP |
| `cron.md` | Scheduled jobs, proactive messaging |

### Plugins, @-context, and cache

| File | Description |
| :--- | :--- |
| `plugins.md` | Plugins from Git, hooks |
| `context-references.md` | `@` references |
| `agent-cache.md` | Agent cache |

### Operations

| File | Description |
| :--- | :--- |
| `troubleshooting.md` | Common failures and fixes |
| `security.md` | Keys, access control |
| `gotchas.md` | Operational lessons |

### Instance management

| File | Description |
| :--- | :--- |
| `instance_templates.md` | Templates and spawn workflow |
| `instances.md` | Active instances |
| `new_instance_questionnaire.md` | New-instance checklist |

### Assets

| File | Description |
| :--- | :--- |
| `assets/README.md` | Optional static diagram exports |

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
