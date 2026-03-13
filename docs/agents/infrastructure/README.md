# Agent Infrastructure

**Module**: `codomyrmex.agents.infrastructure` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Cross-cutting infrastructure concerns for agent deployments. Health checks, resource management, scaling policies, and deployment configuration.

## Purpose

Cloud infrastructure agent module that bridges the `BaseAgent` interface with Infomaniak cloud service clients. Provides JSON command dispatch, automatic tool registry generation via method introspection, and optional security pipeline integration for pre/post execution checks.

## Source Module Structure

Source: [`src/codomyrmex/agents/infrastructure/`](../../../../src/codomyrmex/agents/infrastructure/)

### Key Files

| File | Purpose |
|:---|:---|
| [agent.py](../../../../src/codomyrmex/agents/infrastructure/agent.py) |  |
| [tool_factory.py](../../../../src/codomyrmex/agents/infrastructure/tool_factory.py) |  |

## Quick Start

```python
from codomyrmex.agents.infrastructure import InfrastructureClient

client = InfrastructureClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [infrastructure/README.md](../../../../src/codomyrmex/agents/infrastructure/README.md) |
| SPEC | [infrastructure/SPEC.md](../../../../src/codomyrmex/agents/infrastructure/SPEC.md) |
| AGENTS | [infrastructure/AGENTS.md](../../../../src/codomyrmex/agents/infrastructure/AGENTS.md) |
| PAI | [infrastructure/PAI.md](../../../../src/codomyrmex/agents/infrastructure/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/infrastructure/](../../../../src/codomyrmex/agents/infrastructure/)
- **Project Root**: [README.md](../../../README.md)
