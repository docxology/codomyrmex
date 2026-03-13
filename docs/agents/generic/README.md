# Generic Agent Framework

**Module**: `codomyrmex.agents.generic` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Template and boilerplate for creating new agent integrations. Provides the standard structure, base implementations, and extension points for adding new agent providers.

## Purpose

The `generic` submodule provides shared functionality used across all agent implementations. It includes base agent classes, multi-agent orchestration, inter-agent communication, and task planning utilities.

## Source Module Structure

Source: [`src/codomyrmex/agents/generic/`](../../../../src/codomyrmex/agents/generic/)

### Key Files

| File | Purpose |
|:---|:---|
| [agent_orchestrator.py](../../../../src/codomyrmex/agents/generic/agent_orchestrator.py) |  |
| [api_agent_base.py](../../../../src/codomyrmex/agents/generic/api_agent_base.py) |  |
| [cli_agent_base.py](../../../../src/codomyrmex/agents/generic/cli_agent_base.py) |  |
| [message_bus.py](../../../../src/codomyrmex/agents/generic/message_bus.py) |  |
| [task_planner.py](../../../../src/codomyrmex/agents/generic/task_planner.py) |  |

## Quick Start

```python
from codomyrmex.agents.generic import GenericClient

client = GenericClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [generic/README.md](../../../../src/codomyrmex/agents/generic/README.md) |
| SPEC | [generic/SPEC.md](../../../../src/codomyrmex/agents/generic/SPEC.md) |
| AGENTS | [generic/AGENTS.md](../../../../src/codomyrmex/agents/generic/AGENTS.md) |
| PAI | [generic/PAI.md](../../../../src/codomyrmex/agents/generic/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/generic/](../../../../src/codomyrmex/agents/generic/)
- **Project Root**: [README.md](../../../README.md)
