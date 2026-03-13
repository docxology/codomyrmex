# Mission Control

**Module**: `codomyrmex.agents.mission_control` | **Category**: Specialized | **Last Updated**: March 2026

## Overview

High-level mission orchestration and monitoring dashboard. Coordinates multiple agents on complex multi-step missions with progress visualization, rollback, and convergence detection.

## Purpose

To integrate the builderz-labs/mission-control open-source agent orchestration dashboard within the Codomyrmex agent ecosystem. This module provides a Python client that communicates with the dashboard's REST API for agent fleet management, task orchestration, and cost monitoring.

## Source Module Structure

Source: [`src/codomyrmex/agents/mission_control/`](../../../../src/codomyrmex/agents/mission_control/)

### Key Files

| File | Purpose |
|:---|:---|
| [mcp_tools.py](../../../../src/codomyrmex/agents/mission_control/mcp_tools.py) |  |
| [mission_control_client.py](../../../../src/codomyrmex/agents/mission_control/mission_control_client.py) |  |

### Subdirectories

- `app/`

## Quick Start

```python
from codomyrmex.agents.mission_control import MissionControlClient

client = MissionControlClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [mission_control/README.md](../../../../src/codomyrmex/agents/mission_control/README.md) |
| SPEC | [mission_control/SPEC.md](../../../../src/codomyrmex/agents/mission_control/SPEC.md) |
| AGENTS | [mission_control/AGENTS.md](../../../../src/codomyrmex/agents/mission_control/AGENTS.md) |
| PAI | [mission_control/PAI.md](../../../../src/codomyrmex/agents/mission_control/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/mission_control/](../../../../src/codomyrmex/agents/mission_control/)
- **Project Root**: [README.md](../../../README.md)
