# soul — Persistent Markdown-Memory LLM Agent

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

Wraps [soul.py](https://github.com/menonpg/soul.py) (`soul-agent` PyPI package) to give Codomyrmex agents persistent identity and conversation history stored as plain markdown files — no database, no server required.

| File | Purpose |
|------|---------|
| **SOUL.md** | Agent identity and system prompt |
| **MEMORY.md** | Timestamped conversation log (auto-truncated at 6 000 chars) |

## Installation

```bash
uv sync --extra soul
```

Requires Python ≥ 3.10.

## Quick Start

### Python API

```python
from codomyrmex.soul import SoulAgent

# Create an agent (reads SOUL.md and MEMORY.md if they exist)
agent = SoulAgent(provider="anthropic")
reply = agent.ask("My name is Ada and I work on formal verification.")
print(reply)

# Memory persists — a fresh instance can recall the name
agent2 = SoulAgent(provider="anthropic")
print(agent2.ask("What do you know about me?"))
```

### Providers

```python
# Anthropic Claude (default)
SoulAgent(provider="anthropic")

# OpenAI GPT
SoulAgent(provider="openai", model="gpt-4o")

# Ollama (or any OpenAI-compatible endpoint)
SoulAgent(
    provider="openai-compatible",
    base_url="http://localhost:11434/v1",
    model="llama3",
)
```

API keys are read from environment variables when not passed explicitly:
- Anthropic: `ANTHROPIC_API_KEY`
- OpenAI: `OPENAI_API_KEY`

### MCP Tools

Five MCP tools are auto-discovered and surfaced via the PAI MCP bridge:

```
soul_init     — Create SOUL.md + MEMORY.md for a new agent
soul_ask      — Ask a question (persists exchange to MEMORY.md)
soul_remember — Manually append a note to MEMORY.md
soul_reset    — Clear in-session history (MEMORY.md unchanged)
soul_status   — File statistics for SOUL.md + MEMORY.md
```

Example (no API key required):

```python
from codomyrmex.soul.mcp_tools import soul_init, soul_status

soul_init(soul_path="SOUL.md", memory_path="MEMORY.md", agent_name="Codomyrmex")
print(soul_status())
```

## Key Classes and Functions

| Name | Description |
|------|-------------|
| `SoulAgent` | Primary wrapper class |
| `SoulAgent.ask(question, remember)` | Query the agent; optionally persist |
| `SoulAgent.remember(note)` | Append a note to MEMORY.md |
| `SoulAgent.reset_conversation()` | Clear in-session history |
| `SoulAgent.memory_stats()` | Return file size statistics |
| `HAS_SOUL` | `bool` flag — True when soul-agent is installed |

## Comparison with `agentic_memory`

| | `soul` | `agentic_memory` |
|-|--------|-----------------|
| Storage | Markdown files | Vector database |
| Dependencies | soul-agent (lightweight) | chromadb, embeddings |
| Memory retrieval | LLM reads full file (last 6 000 chars) | Semantic similarity search |
| Best for | Lightweight, git-trackable agents | Large-scale, semantic recall |

## Architecture

- **Core Layer** — depends only on Foundation: `model_context_protocol`, `exceptions`
- `agent.py` — `SoulAgent` wrapper with import guard and env-key resolution
- `mcp_tools.py` — 5 stateless `@mcp_tool` functions (one `SoulAgent` per call)
- `exceptions.py` — `SoulError` hierarchy extending `CodomyrmexError`

## Navigation

- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Agent Capabilities**: [AGENTS.md](AGENTS.md)
- **Technical Spec**: [SPEC.md](SPEC.md)
- **PAI Integration**: [PAI.md](PAI.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent**: [codomyrmex](../README.md)
