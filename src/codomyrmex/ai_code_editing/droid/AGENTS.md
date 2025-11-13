# Codomyrmex Agents — src/codomyrmex/ai_code_editing/droid

## Purpose
Runtime coordinators, TODO runners, and task handlers powering the droid automation workflows.

## Active Components
- `controller.py` – Droid controller with configuration and task execution
- `run_todo_droid.py` – Main TODO processor with interactive and command-line modes
- `todo.py` – TODO list management and parsing utilities
- `tasks.py` – Built-in task handlers for various operations
- `todo_list.txt` – Structured TODO list with Markdown-based tracking
- `README.md` – Documentation for the droid system
- `handlers/` – Directory for custom task handler implementations

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All handlers and utilities MUST be real, executable implementations. No stubs.
- The `run_todo_droid.py` entrypoint MUST execute tasks via the droid controller, not by direct calls.

## Related Modules
- **AI Code Editing Module** (`../`) - Parent module directory
- **Droid Handlers** (`handlers/`) - Task handler implementations
- **Droid Tests** (`../tests/unit/droid/`) - Droid-specific test suite

## Navigation Links
- **📚 Module Overview**: [../README.md](../README.md) - AI code editing module documentation
- **🤖 Droid Handlers**: [handlers/AGENTS.md](handlers/AGENTS.md) - Droid handler coordination
- **🧪 Droid Tests**: [../tests/unit/droid/AGENTS.md](../tests/unit/droid/AGENTS.md) - Droid test coordination
- **🏠 Package Root**: [../../../README.md](../../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../../docs/README.md](../../../../docs/README.md) - Complete documentation
