# Droid — Task Management

**Module**: `codomyrmex.agents.droid` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Task management and automation framework (the "TODO Droid"). Provides priority queues, status tracking, and cross-agent task coordination with persistent SQLite storage.

## Key Classes

| Class | Purpose |
|:---|:---|
| `DroidController` | Main controller — task lifecycle, scheduling, execution |
| `DroidConfig` | Configuration dataclass (priorities, limits, paths) |
| `DroidMetrics` | Performance and throughput metrics |
| `DroidMode` | Operating modes (autonomous, supervised, manual) |
| `DroidStatus` | Status enum (pending, running, complete, failed) |
| `TodoItem` | Individual task representation |
| `TodoManager` | CRUD operations on TODO items |

## Key Functions

| Function | Purpose |
|:---|:---|
| `create_default_controller()` | Factory with sensible defaults |
| `load_config_from_file(path)` | Load YAML/JSON config |
| `save_config_to_file(config, path)` | Persist config |

## Usage

```python
from codomyrmex.agents.droid import DroidController, TodoManager, TodoItem

# Create controller
controller = create_default_controller()

# Manage TODOs
manager = TodoManager()
manager.add(TodoItem(title="Fix parser bug", priority=1))
items = manager.list(status="pending")
```

## Source Module

Source: [`src/codomyrmex/agents/droid/`](../../../src/codomyrmex/agents/droid/)

| File | Purpose |
|:---|:---|
| `controller.py` | DroidController, config, metrics, status management |
| `todo.py` | TodoItem and TodoManager CRUD |
| `tasks.py` | Task definitions and scheduling |
| `run_todo_droid.py` | CLI entry point for the TODO droid |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/droid/](../../../src/codomyrmex/agents/droid/)
- **Project Root**: [README.md](../../../README.md)
