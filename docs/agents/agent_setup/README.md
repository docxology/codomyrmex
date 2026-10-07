# Agent Setup

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.agent_setup` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Environment validation and agent discovery infrastructure. Validates binary availability, API keys, config files, and backend capabilities for all agent frameworks.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `AgentRegistry` | Catalog of known agents with live availability probes |
| `AgentDescriptor` | Declarative description of one agent (type, credential env var, default model) |
| `ProbeResult` | Outcome of probing one agent (`operative`, `key_missing`, `unreachable`, `unavailable`) |
| `load_config` / `save_config` / `merge_with_env` | Read, write, and merge the `~/.codomyrmex/agents.yaml` config |

## Usage

```python
from codomyrmex.agents.agent_setup import AgentRegistry, load_config

registry = AgentRegistry()
for result in registry.probe_all():
    print(f"{result.name}: {result.status} ({result.detail})")

print(registry.get_operative())  # names of agents that are ready to use
config = load_config()  # ~/.codomyrmex/agents.yaml by default
```

## Source Module

Source: [`src/codomyrmex/agents/agent_setup/`](../../../src/codomyrmex/agents/agent_setup/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/agent_setup/](../../../src/codomyrmex/agents/agent_setup/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
