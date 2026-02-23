# Agent Setup — SPEC.md

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provide a single entry point for discovering, validating, and configuring all
agent integrations in the Codomyrmex ecosystem.

## Architecture

```
agent_setup/
├── __init__.py          # Public exports
├── __main__.py          # CLI entry: python -m codomyrmex.agents.agent_setup
├── registry.py          # AgentDescriptor, ProbeResult, AgentRegistry
├── config_file.py       # YAML load/save/merge
├── setup_wizard.py      # Interactive terminal wizard
├── README.md
├── AGENTS.md
└── SPEC.md
```

## Data Model

### AgentDescriptor

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique identifier (e.g. `"claude"`) |
| `display_name` | `str` | Human-readable name |
| `agent_type` | `str` | `"api"` \| `"cli"` \| `"local"` |
| `env_var` | `str` | Primary env var |
| `config_key` | `str` | AgentConfig field name |
| `default_model` | `str` | Default model string |
| `probe` | `Callable` | Function returning `ProbeResult` |

### ProbeResult

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Agent name |
| `status` | `str` | `"operative"` \| `"key_missing"` \| `"unreachable"` \| `"unavailable"` |
| `detail` | `str` | Human-readable explanation |
| `latency_ms` | `float \| None` | Probe response time |

## Probe Strategy

| Type | Method |
|------|--------|
| API | Check env var for API key presence |
| CLI | `shutil.which()` to find binary on PATH |
| Local | HTTP GET to `{ollama_base_url}/api/tags` |

## Config File

- Location: `~/.codomyrmex/agents.yaml`
- Permissions: `0o600` (owner-only read/write)
- Format: YAML with `agents:` top-level key
