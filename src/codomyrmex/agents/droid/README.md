# droid

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - [handlers](handlers/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Autonomous Agent abstraction for persisted or ephemeral agentic sessions that maintain state, execute multi-step reasoning, and use tools. Follows the `Think -> Act -> Observe` loop with support for personas (e.g., "RefactoringDroid", "DocsDroid"), tool execution, and conversation history.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `controller.py` – File
- `handlers/` – Subdirectory
- `run_todo_droid.py` – File
- `tasks.py` – File
- `todo.py` – File
- `todo_list.txt` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.droid import (
    DroidController,
    DroidConfig,
    create_default_controller,
)

# Create a Droid controller
config = DroidConfig(
    mode="autonomous",
    persona="RefactoringDroid",
    max_iterations=10
)
controller = create_default_controller(config)

# Execute a task
result = controller.execute_task(
    task="Refactor the authentication module to use async/await",
    context={"module_path": "src/auth.py"}
)

# Check status
status = controller.get_status()
print(f"Droid status: {status}")
```

