# Hermes Agent Submodule

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `hermes` submodule provides a `CLIAgentBase` wrapper for the [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-agent), exposing its single-turn chat (`hermes chat -q`) and skills management functionalities to the Codomyrmex ecosystem.

Hermes Agent is an AI agent harness with tool-calling capabilities, interactive CLI, and comprehensive skills management via the agentskills.io standard.

## Usage

```python
from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes import HermesClient

client = HermesClient()
request = AgentRequest(prompt="List files in the current directory and write the output to a text file.")
response = client.execute(request)

if response.is_success():
    print(response.content)
else:
    print(response.error)
```

## Features

- **Single-Turn Chat**: Send task prompts directly to Hermes via `hermes chat -q`.
- **Skills Management**: Programmatically list or invoke skills through context arguments.
- **Diagnostic Polling**: Run `hermes status` directly.
- **MCP Integration**: Fully exposes `hermes_execute`, `hermes_status`, and `hermes_skills_list` to the MCP host.

## Rules

 Governed by the `agents.cursorrules` module standards requiring Zero-Mock testing and robust exception translation (`HermesError` derived from `AgentError`).
