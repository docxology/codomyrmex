# Codomyrmex Agents — src/codomyrmex/agents/droid

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [handlers](handlers/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Autonomous Agent abstraction for persisted or ephemeral agentic sessions that maintain state, execute multi-step reasoning, and use tools. Follows the `Think -> Act -> Observe` loop with support for personas (e.g., "RefactoringDroid", "DocsDroid"), tool execution, and conversation history.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `controller.py` – Thread-safe controller coordinating droid operations
- `handlers/` – Directory containing task handlers
- `run_todo_droid.py` – TODO droid execution script
- `tasks.py` – Task definitions and generators
- `todo.py` – TODO management
- `todo_list.txt` – TODO list file

## Key Classes and Functions

### DroidController (`controller.py`)
- `DroidController(config: DroidConfig)` – Thread-safe controller coordinating droid operations
- `start() -> None` – Start droid
- `stop() -> None` – Stop droid
- `run_task(task: str) -> str` – Execute a complex task
- `chat(user_input: str) -> str` – Chat interface
- `update_config(**overrides: Any) -> DroidConfig` – Update configuration
- `reset_metrics() -> None` – Reset metrics
- `status: DroidStatus` – Current droid status
- `metrics: dict[str, Any]` – Droid metrics

### DroidConfig (`controller.py`)
- `DroidConfig` (dataclass) – Droid configuration settings
- `validate() -> None` – Validate configuration
- `with_overrides(**overrides: Any) -> DroidConfig` – Create config with overrides
- `to_dict() -> dict` – Convert to dictionary

### DroidStatus (`controller.py`)
- `DroidStatus` (Enum) – Droid status: STOPPED, IDLE, RUNNING, ERROR

### DroidMode (`controller.py`)
- `DroidMode` (Enum) – Droid execution modes

### DroidMetrics (`controller.py`)
- `DroidMetrics` (dataclass) – Droid performance metrics
- `snapshot() -> dict[str, Any]` – Get metrics snapshot
- `reset() -> None` – Reset metrics

### TodoManager (`todo.py`)
- `TodoManager()` – TODO management
- `TodoItem` (dataclass) – TODO item representation

### Module Functions (`__init__.py`)
- `create_default_controller() -> DroidController` – Create default controller
- `load_config_from_file(config_path: str) -> DroidConfig` – Load configuration from file
- `save_config_to_file(config: DroidConfig, config_path: str) -> None` – Save configuration to file

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation