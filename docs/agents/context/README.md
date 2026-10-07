# Context Management

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.context` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Repository indexing, project scanning, and tool selection for agents. Provides Python symbol and import indexing, project file inventories, and file-type/task-based tool recommendations.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `RepoIndexer` | Symbol and import indexing for Python files (`indexer.py`) |
| `ProjectScanner` | Directory scan producing a `ProjectContext` file inventory (`project.py`) |
| `ToolSelector` | Recommends tools for a file extension and task type (`project.py`) |

## Usage

```python
from codomyrmex.agents.context.indexer import RepoIndexer
from codomyrmex.agents.context.project import ProjectScanner, ToolSelector

ctx = ProjectScanner().scan(".")
print(f"Found {ctx.file_count} files in {ctx.module_count} modules")

index = RepoIndexer().index_directory("src")
print(f"Indexed {index.symbol_count} symbols")

print(ToolSelector().select(file_ext="py", task_type="review"))
```

## Source Module

Source: [`src/codomyrmex/agents/context/`](../../../src/codomyrmex/agents/context/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/context/](../../../src/codomyrmex/agents/context/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
