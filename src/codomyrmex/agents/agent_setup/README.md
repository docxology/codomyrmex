# Agent Setup

Interactive configuration and health-check module for all Codomyrmex agents.

## Quick Start

```bash
# Run the interactive setup wizard
uv run python -m codomyrmex.agents.agent_setup

# Status-only (no prompts)
uv run python -m codomyrmex.agents.agent_setup --status-only

# Custom config path
uv run python -m codomyrmex.agents.agent_setup --config /path/to/agents.yaml
```

## Features

| Feature | Description |
|---------|-------------|
| **Agent Registry** | Declarative catalog of all 11 agents (API, CLI, local) |
| **Live Probing** | Real health checks — env vars, `shutil.which`, HTTP to Ollama |
| **Setup Wizard** | Interactive terminal guide: scan → configure → save |
| **YAML Config** | Persist API keys/paths to `~/.codomyrmex/agents.yaml` (0o600 perms) |

## Agent Types

- **API** (5): Claude, Codex, O1, DeepSeek, Qwen — requires API keys
- **CLI** (5): Jules, OpenCode, Gemini, Mistral Vibe, Every Code — requires binary on PATH
- **Local** (1): Ollama — requires server at `localhost:11434`

## Programmatic Usage

```python
from codomyrmex.agents.agent_setup import AgentRegistry, load_config

# Probe all agents
registry = AgentRegistry()
for result in registry.probe_all():
    print(f"{result.name}: {result.status} — {result.detail}")

# Get only operative agents
operative = registry.get_operative()

# Load/save YAML config
config = load_config()
```

## Config File Format

```yaml
agents:
  claude:
    api_key: sk-ant-...
    model: claude-3-opus-20240229
  deepseek:
    api_key: sk-...
  ollama:
    base_url: http://localhost:11434
    default_model: llama3.2
```

## Dependencies

- `pyyaml` — for config file support
- Standard library only for probes (`urllib`, `shutil`, `subprocess`)
