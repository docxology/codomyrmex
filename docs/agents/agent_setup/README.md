# Agent Setup

**Module**: `codomyrmex.agents.agent_setup` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Environment validation and agent discovery infrastructure. Validates binary availability, API keys, config files, and backend capabilities for all agent frameworks.

## Key Classes

| Class | Purpose |
|:---|:---|
| `AgentSetupValidator` | Environment validation for agent dependencies |
| `AgentDiscovery` | Auto-discovery of available agent backends |

## Usage

```python
from codomyrmex.agents.agent_setup import AgentSetupValidator

client = AgentSetupValidator()
```

## Source Module

Source: [`src/codomyrmex/agents/agent_setup/`](../../../../src/codomyrmex/agents/agent_setup/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/agent_setup/](../../../../src/codomyrmex/agents/agent_setup/)
- **Project Root**: [README.md](../../../README.md)
