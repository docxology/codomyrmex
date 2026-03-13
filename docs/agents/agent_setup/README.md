# Agent Setup & Discovery

**Module**: `codomyrmex.agents.agent_setup` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Validates the local environment, discovers which agent CLIs are installed, and reports agent readiness. Provides the `--status-only` command to see which agents are operative.

## Purpose

Provide a single entry point for discovering, validating, and configuring all
agent integrations in the Codomyrmex ecosystem.

## Source Module Structure

Source: [`src/codomyrmex/agents/agent_setup/`](../../../../src/codomyrmex/agents/agent_setup/)

### Key Files

| File | Purpose |
|:---|:---|
| [__main__.py](../../../../src/codomyrmex/agents/agent_setup/__main__.py) |  |
| [config_file.py](../../../../src/codomyrmex/agents/agent_setup/config_file.py) |  |
| [registry.py](../../../../src/codomyrmex/agents/agent_setup/registry.py) |  |
| [setup_wizard.py](../../../../src/codomyrmex/agents/agent_setup/setup_wizard.py) |  |

## Quick Start

```python
from codomyrmex.agents.agent_setup import AgentSetupClient

client = AgentSetupClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [agent_setup/README.md](../../../../src/codomyrmex/agents/agent_setup/README.md) |
| SPEC | [agent_setup/SPEC.md](../../../../src/codomyrmex/agents/agent_setup/SPEC.md) |
| AGENTS | [agent_setup/AGENTS.md](../../../../src/codomyrmex/agents/agent_setup/AGENTS.md) |
| PAI | [agent_setup/PAI.md](../../../../src/codomyrmex/agents/agent_setup/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/agent_setup/](../../../../src/codomyrmex/agents/agent_setup/)
- **Project Root**: [README.md](../../../README.md)
