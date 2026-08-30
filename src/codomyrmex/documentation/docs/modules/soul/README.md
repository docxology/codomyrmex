<!-- readme: generated -->

# soul

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/soul/`

## Overview

soul — Persistent markdown-memory LLM agent integration (soul.py wrapper).

Wraps the ``soul-agent`` library (https://github.com/menonpg/soul.py) for use
within Codomyrmex.  Agents maintain identity in SOUL.md and conversation
history in MEMORY.md — no database or server required.

Providers: anthropic, openai, openai-compatible (Ollama, any HTTP endpoint)

Optional dependency::

    uv sync --extra soul

Quick start::

    from codomyrmex.soul import SoulAgent

    agent = SoulAgent(provider="anthropic")
    reply = agent.ask("Hello! My name is Ada.")
    print(reply)

    # Memory persists — a new instance can recall the name.
    agent2 = SoulAgent(provider="anthropic")
    print(agent2.ask("What is my name?"))

## Public Exports

`soul` exports 7 public symbols via `__all__`:

`HAS_SOUL`, `SoulAgent`, `SoulError`, `SoulImportError`, `SoulMemoryError`, `SoulProviderError`, `__version__`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../soul/](../../../../soul/)
