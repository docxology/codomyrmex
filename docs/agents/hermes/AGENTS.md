# Hermes Documentation — Agent Coordination

**Module**: `docs/agents/hermes/` | **Version**: v0.2.0 | **Last Updated**: March 2026

## Purpose

Agent coordination document for the Hermes documentation subfolder. Guides AI agents navigating Hermes-related documentation and scripts.

## Documentation Files (19)

### Getting Started
| File | Description |
|:---|:---|
| `README.md` | Index, overview, and quick start |
| `setup_guide.md` | Complete new-instance setup (from official docs) |
| `cli_reference.md` | All CLI commands and slash commands |

### Architecture & Configuration
| File | Description |
|:---|:---|
| `architecture.md` | Core agent loop, components, structured reasoning |
| `configuration.md` | config.yaml reference, YAML pitfalls |
| `environment.md` | HERMES_HOME, .env, API key management |
| `models.md` | Model selection, OpenRouter, providers |
| `personalities.md` | Personality system and custom personas |

### Platform Integration
| File | Description |
|:---|:---|
| `gateway.md` | Gateway daemon, platform adapters |
| `telegram.md` | Telegram bot setup, 409 Conflict fixes |
| `launchd.md` | macOS launchd service management |
| `multi_instance.md` | Multi-bot deployment patterns |

### Agent Capabilities
| File | Description |
|:---|:---|
| `sessions.md` | Session lifecycle, state.db, FTS5 |
| `skills.md` | Self-improving skills, agentskills.io |
| `tools.md` | Tool registry, MCP integration |
| `cron.md` | Scheduled jobs, proactive messaging |

### Operations
| File | Description |
|:---|:---|
| `troubleshooting.md` | 9 issue patterns with diagnosis/fixes |
| `security.md` | API key hygiene, access control |

## Scripts (`scripts/agents/hermes/`)

| Script | Purpose |
|:---|:---|
| `new_instance.py` | Create fully-configured new Hermes instances |
| `setup_hermes.py` | Validate environment, config, backends |
| `run_hermes.py` | Send prompt, get response |
| `dispatch_hermes.py` | Sweep-and-dispatch orchestrator |
| `observe_hermes.py` | Session observability |
| `evaluate_orchestrators.py` | Thin orchestrator evaluation |
| `prompt_context.py` | Project-aware context builder |

## Operating Contracts

1. **Official Source of Truth**: [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)
2. **HERMES_HOME Isolation**: Each instance must have its own `HERMES_HOME` directory
3. **Secret Hygiene**: API keys in `.env` only, `chmod 600`, never commit
4. **Zero Duplicate YAML Keys**: `config.yaml` must never have duplicate top-level keys
5. **`--replace` Flag**: Always use in launchd plists for PID management

## Navigation

- **Parent**: [docs/agents/AGENTS.md](../AGENTS.md)
- **Source**: [src/codomyrmex/agents/hermes/AGENTS.md](../../../src/codomyrmex/agents/hermes/AGENTS.md)
- **Project Root**: [AGENTS.md](../../../AGENTS.md)
