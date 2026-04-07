# Mission Control

**Module**: `codomyrmex.agents.mission_control` | **Category**: Specialized | **Last Updated**: March 2026

## Overview

Integration with the builderz-labs/mission-control open-source dashboard for AI agent orchestration. Communicates via REST API for agent management, task tracking, cost monitoring, and real-time workflow orchestration.

**Upstream**: [mission-control](https://github.com/builderz-labs/mission-control)

## Key Classes

| Class | Purpose |
|:---|:---|
| `MissionControlClient` | REST API client for the Mission Control dashboard |
| `MissionControlConfig` | Configuration dataclass (API URL, auth, timeouts) |
| `MissionControlError` | Error handling for API failures |

## Configuration

**Required**: Mission Control dashboard URL (default: `http://localhost:3000`)

## Usage

```python
from codomyrmex.agents.mission_control import MissionControlClient

client = MissionControlClient()
```

## Source Module

Source: [`src/codomyrmex/agents/mission_control/`](../../../src/codomyrmex/agents/mission_control/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/mission_control/](../../../src/codomyrmex/agents/mission_control/)
- **Project Root**: [README.md](../../../README.md)
