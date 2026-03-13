# Git Agent

**Module**: `codomyrmex.agents.git_agent` | **Category**: Specialized | **Last Updated**: March 2026

## Overview

Git-aware agent that understands repository structure, branch management, merge conflict resolution, and commit message generation. Integrates with git_operations module.

## Purpose

The `git_agent` module provides a `GitAgent` class that wraps Git and GitHub operations behind the standard `BaseAgent` interface. It parses structured command prompts and dispatches them to the `git_operations` module, enabling automated repository management within agentic workflows.

## Source Module Structure

Source: [`src/codomyrmex/agents/git_agent/`](../../../../src/codomyrmex/agents/git_agent/)

### Key Files

| File | Purpose |
|:---|:---|
| [agent.py](../../../../src/codomyrmex/agents/git_agent/agent.py) |  |

## Quick Start

```python
from codomyrmex.agents.git_agent import GitAgentClient

client = GitAgentClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [git_agent/README.md](../../../../src/codomyrmex/agents/git_agent/README.md) |
| SPEC | [git_agent/SPEC.md](../../../../src/codomyrmex/agents/git_agent/SPEC.md) |
| AGENTS | [git_agent/AGENTS.md](../../../../src/codomyrmex/agents/git_agent/AGENTS.md) |
| PAI | [git_agent/PAI.md](../../../../src/codomyrmex/agents/git_agent/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/git_agent/](../../../../src/codomyrmex/agents/git_agent/)
- **Project Root**: [README.md](../../../README.md)
