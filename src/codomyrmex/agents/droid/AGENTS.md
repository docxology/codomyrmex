# Codomyrmex Agents — src/codomyrmex/agents/droid

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Droid module providing task management, automation, and todo tracking capabilities. This module enables automated task execution, configuration management, and progress tracking for agent workflows.

## Active Components

- `controller.py` - Main droid controller and configuration
- `todo.py` - Todo item and manager implementation
- `tasks.py` - Task definitions and handlers
- `run_todo_droid.py` - Standalone droid runner
- `handlers/` - Directory containing task handlers
- `__init__.py` - Module exports
- `README.md` - Module documentation
- `SPEC.md` - Specification document
- `todo_list.txt` - Sample todo list

## Key Classes

### Controller
- **`DroidController`** - Main controller for droid operations
  - Manages task queue and execution
  - Tracks metrics and performance
  - Handles configuration and state
  - Coordinates with agent backends

### Configuration
- **`DroidConfig`** - Configuration dataclass for droid settings
- **`load_config_from_file()`** - Load configuration from JSON/YAML file
- **`save_config_to_file()`** - Save configuration to file
- **`create_default_controller()`** - Factory for creating default controller

### Status and Metrics
- **`DroidMode`** - Enum defining operation modes (e.g., AUTO, MANUAL, SUPERVISED)
- **`DroidStatus`** - Enum defining status states (e.g., IDLE, RUNNING, PAUSED, ERROR)
- **`DroidMetrics`** - Dataclass for tracking performance metrics

### Todo Management
- **`TodoManager`** - Manages a collection of todo items
  - Add, remove, update todo items
  - Track completion status
  - Persist todo state
- **`TodoItem`** - Dataclass representing a single todo item
  - Title, description, priority
  - Status and completion tracking
  - Metadata and timestamps

## Operating Contracts

- Controller must be started before task execution.
- Configuration changes require controller restart to take effect.
- Todo items are persisted to maintain state across sessions.
- Metrics are collected during operation for monitoring.
- CLI handlers provide start, stop, status, and config operations.

## Signposting

- **Starting automation?** Use `DroidController.start()` after configuration.
- **Managing todos?** Use `TodoManager` for CRUD operations on tasks.
- **Checking status?** Use `DroidController.status` or CLI status handler.
- **Custom configuration?** Create `DroidConfig` and pass to controller.
- **Standalone execution?** Run `run_todo_droid.py` directly.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **AI Code Editing**: [ai_code_editing](../ai_code_editing/AGENTS.md) - Code generation integration
- **CLI Handlers**: [cli](../cli/AGENTS.md) - CLI command handlers
- **Project Root**: ../../../../README.md - Main project documentation
