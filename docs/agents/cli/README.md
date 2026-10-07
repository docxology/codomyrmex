# CLI Handler Framework

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.cli` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Command handlers behind the `codomyrmex` agent CLI commands. Each handler takes a parsed-arguments object, builds an `AgentRequest`, runs the matching agent client, prints formatted output, and returns `True` on success.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `handle_info` | Print agents module information and configuration |
| `handle_<agent>_execute` / `handle_<agent>_stream` | Run a prompt through an agent (`claude`, `codex`, `gemini`, `jules`, `opencode`) |
| `handle_<agent>_check` | Report whether an agent is configured (API key or CLI binary) |
| `handle_agent_setup` / `handle_agent_test` | Set up or connection-test an arbitrary agent client class |

## Usage

```python
from argparse import Namespace

from codomyrmex.agents.cli import handle_claude_check, handle_info

handle_info(Namespace(format="json"))
configured = handle_claude_check(Namespace())  # False when ANTHROPIC_API_KEY is unset
```

## Source Module

Source: [`src/codomyrmex/agents/cli/`](../../../src/codomyrmex/agents/cli/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/cli/](../../../src/codomyrmex/agents/cli/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
