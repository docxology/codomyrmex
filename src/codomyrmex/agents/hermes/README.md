# Hermes Agent Submodule

**Version**: v2.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `hermes` submodule provides a dual-backend wrapper for the [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-agent), exposing chat completion, tool-calling, and skills management to the Codomyrmex ecosystem.

**Backends** (configurable via `hermes_backend`):

| Backend | Requirement | Priority |
| --- | --- | --- |
| `cli` | `hermes` binary in `$PATH` | Preferred (when available) |
| `ollama` | `ollama` with `hermes3` model | Automatic fallback |
| `auto` | Either of the above | **Default** — uses CLI if found, else Ollama |

## Quick Start

```python
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes import HermesClient

client = HermesClient()  # auto-detects backend
print(f"Using: {client.active_backend}")  # "cli" or "ollama"

request = AgentRequest(prompt="Explain active inference in one sentence.")
response = client.execute(request)

if response.is_success():
    print(response.content)
```

## Configuration

| Key | Default | Description |
| --- | --- | --- |
| `hermes_backend` | `auto` | Backend: `auto`, `cli`, `ollama` |
| `hermes_model` | `hermes3` | Ollama model name |
| `hermes_command` | `hermes` | Path to CLI binary |
| `hermes_timeout` | `120` | Subprocess timeout (s) |
| `hermes_working_dir` | `None` | Working directory for CLI |

## Features

- **Dual-Backend**: Seamlessly switches between Hermes CLI and Ollama
- **Single-Turn Chat**: Send task prompts via CLI (`hermes chat -q`) or Ollama (`ollama run hermes3`)
- **Streaming**: Line-by-line output streaming from either backend
- **Skills Management**: Programmatically list skills (CLI backend only)
- **Diagnostic Polling**: `get_hermes_status()` reports active backend and availability
- **MCP Integration**: Exposes `hermes_execute`, `hermes_status`, `hermes_skills_list`

## Installation

```bash
# Option A: Ollama backend (recommended)
ollama pull hermes3

# Option B: Full Hermes CLI
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

## Rules

Governed by the `agents.cursorrules` module standards requiring Zero-Mock testing and robust exception translation (`HermesError` derived from `AgentError`).
