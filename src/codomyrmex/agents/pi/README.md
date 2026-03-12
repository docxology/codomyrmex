# Pi Coding Agent — Codomyrmex Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

A Codomyrmex agent wrapper for [pi](https://pi.dev/), a minimal terminal-based AI coding agent by Mario Zechner. Pi supports 15+ LLM providers, tree-structured sessions, context engineering via `AGENTS.md`/`SYSTEM.md`, and an extensible TypeScript plugin system.

This module provides:
- **Python RPC client** (`PiClient`) communicating via JSONL stdin/stdout
- **6 MCP tools** for swarm orchestration
- **Print-mode helper** for simple one-shot queries

## Key Features

| Feature | Description |
| :--- | :--- |
| **15+ providers** | Anthropic, OpenAI, Google, Azure, Bedrock, Mistral, Groq, Cerebras, xAI, Ollama, etc. |
| **4 modes** | Interactive TUI, Print (`-p`), JSON stream, RPC (JSONL) |
| **Tree sessions** | Branch/navigate history; export to HTML or GitHub Gist |
| **Context files** | `AGENTS.md`, `SYSTEM.md` loaded from `~/.pi/agent/`, parent dirs, cwd |
| **Extensible** | TypeScript extensions, skills, prompt templates, themes, pi packages |
| **Tools** | `read`, `bash`, `edit`, `write`, `grep`, `find`, `ls` |

## Structure

```
pi/
├── __init__.py              # Module exports
├── pi_client.py             # Python RPC client (stdlib only)
├── mcp_tools.py             # 6 MCP tools
├── README.md                # This file
├── AGENTS.md                # Agent coordination
├── SPEC.md                  # Functional specification
├── PAI.md                   # PAI access matrix
├── API_SPECIFICATION.md     # Client API reference
└── MCP_TOOL_SPECIFICATION.md # MCP tool spec
```

## Quick Start

```python
from codomyrmex.agents.pi import PiClient, PiConfig

# One-shot query (non-interactive)
client = PiClient(PiConfig(provider="anthropic"))
output = client.run_print("List all Python files in src/")
print(output)

# Multi-turn RPC session
with PiClient(PiConfig(provider="google", no_session=True)) as client:
    for event in client.prompt("What files are in the current directory?"):
        if event.get("type") == "message_update":
            ae = event.get("assistantMessageEvent", {})
            if ae.get("type") == "text_delta":
                print(ae["delta"], end="", flush=True)
```

## Installation

```bash
npm install -g @mariozechner/pi-coding-agent
pi --version  # Should show 0.57.x+
```

## Tech Stack

- **Runtime**: Node.js (pi CLI)
- **Client**: Python 3.11+ (stdlib only — subprocess, json, threading)
- **Protocol**: JSONL over stdin/stdout (RPC mode)
- **Upstream**: [github.com/badlogic/pi-mono](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent)
