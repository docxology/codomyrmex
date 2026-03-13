# Droid Task Management

**Module**: `codomyrmex.agents.droid` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Structured task management system for agents. Provides task decomposition, progress tracking, priority queues, and cross-agent coordination via shared task boards.

## Purpose

The droid package provides a thread-safe task execution framework built around `DroidController`, `DroidConfig`, and `TodoManager`. It processes structured TODO lists through resolved handler functions, with configurable operation permissions, retry settings, and real-time execution metrics.

## Source Module Structure

Source: [`src/codomyrmex/agents/droid/`](../../../../src/codomyrmex/agents/droid/)

### Key Files

| File | Purpose |
|:---|:---|
| [controller.py](../../../../src/codomyrmex/agents/droid/controller.py) |  |
| [run_todo_droid.py](../../../../src/codomyrmex/agents/droid/run_todo_droid.py) |  |
| [tasks.py](../../../../src/codomyrmex/agents/droid/tasks.py) |  |
| [todo.py](../../../../src/codomyrmex/agents/droid/todo.py) |  |

### Subdirectories

- `generators/`
- `handlers/`

## Quick Start

```python
from codomyrmex.agents.droid import DroidClient

client = DroidClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [droid/README.md](../../../../src/codomyrmex/agents/droid/README.md) |
| SPEC | [droid/SPEC.md](../../../../src/codomyrmex/agents/droid/SPEC.md) |
| AGENTS | [droid/AGENTS.md](../../../../src/codomyrmex/agents/droid/AGENTS.md) |
| PAI | [droid/PAI.md](../../../../src/codomyrmex/agents/droid/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/droid/](../../../../src/codomyrmex/agents/droid/)
- **Project Root**: [README.md](../../../README.md)
