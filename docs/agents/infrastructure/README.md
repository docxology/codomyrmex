# Infrastructure Management

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.infrastructure` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Cloud infrastructure agent. `InfrastructureAgent` dispatches JSON commands (`{"service": ..., "action": ...}`) to configured cloud clients (compute, storage, network, DNS, …), runs them through an optional security pipeline, and can expose every client method as a tool.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `InfrastructureAgent` | `BaseAgent` subclass that executes cloud service actions from JSON prompts |
| `CloudToolFactory` | Generates tool registry entries from cloud client methods |

## Usage

```python
import json

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.infrastructure import InfrastructureAgent

# Builds Infomaniak clients from INFOMANIAK_* environment variables.
agent = InfrastructureAgent.from_env()
print(agent.available_services())

request = AgentRequest(prompt=json.dumps({"service": "compute", "action": "list_instances"}))
response = agent.execute(request)
print(response.content or response.error)
```

## Source Module

Source: [`src/codomyrmex/agents/infrastructure/`](../../../src/codomyrmex/agents/infrastructure/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/infrastructure/](../../../src/codomyrmex/agents/infrastructure/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
