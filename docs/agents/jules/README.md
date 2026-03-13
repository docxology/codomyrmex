# Jules (Google)

**Module**: `codomyrmex.agents.jules` | **Category**: CLI-based | **Last Updated**: March 2026

## Overview

Google Jules integration for cloud-based AI coding tasks. Jules runs asynchronous coding tasks in sandboxed cloud VMs, with support for swarm orchestration (113+ concurrent sessions), remote session management, and patch extraction.

## Key Classes

| Class | Purpose |
|:---|:---|
| `JulesClient` | CLI wrapper for `jules` command — task submission, session tracking |
| `JulesSwarmDispatcher` | Swarm orchestration — concurrent multi-session dispatch |
| `JulesIntegrationAdapter` | Bridges Jules with other Codomyrmex modules |

## Key Features

- **Asynchronous execution**: Submit tasks and check status later
- **Swarm dispatch**: Parallelize work across 100+ concurrent sessions
- **Patch extraction**: Pull completed diffs back to local repo
- **Session management**: List, inspect, and resume remote sessions

## Usage

```python
from codomyrmex.agents.jules import JulesClient, JulesSwarmDispatcher

# Submit a task
client = JulesClient()
session_id = client.submit_task("Fix all type errors in src/utils/")

# Check status
status = client.get_session_status(session_id)

# Swarm dispatch
dispatcher = JulesSwarmDispatcher()
dispatcher.dispatch_batch(prompts=[...], repo="docxology/codomyrmex")
```

## CLI Commands

```bash
jules create "Fix bug in parser"     # Create new task
jules list                           # List sessions
jules remote list --session          # List remote sessions with details
jules remote pull <session-id>       # Pull completed patches
```

## Configuration

**Required**: Google Cloud account with Jules access.

## Source Module

Source: [`src/codomyrmex/agents/jules/`](../../../../src/codomyrmex/agents/jules/)

| File | Purpose |
|:---|:---|
| `jules_client.py` | CLI wrapper, task submission, swarm dispatch |
| `jules_integration.py` | Integration adapter for cross-module use |
| `mcp_tools.py` | MCP tool definitions |

## Source Documentation

| Document | Path |
|:---|:---|
| README | [jules/README.md](../../../../src/codomyrmex/agents/jules/README.md) |
| SPEC | [jules/SPEC.md](../../../../src/codomyrmex/agents/jules/SPEC.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/jules/](../../../../src/codomyrmex/agents/jules/)
- **Project Root**: [README.md](../../../README.md)
