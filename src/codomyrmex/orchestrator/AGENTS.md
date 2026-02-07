# Codomyrmex Agents — src/codomyrmex/orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Centralized script orchestration capabilities for discovering, configuring, executing, and reporting on Python scripts within the Codomyrmex project. Core automation engine.

## Active Components

- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `config.py` – Project file
- `core.py` – Project file
- `discovery.py` – Project file
- `engines/` – Directory containing engines components
- `exceptions.py` – Project file
- `integration.py` – Project file
- `monitors/` – Directory containing monitors components
- `parallel_runner.py` – Project file
- `reporting.py` – Project file
- `runner.py` – Project file
- `schedulers/` – Directory containing schedulers components
- `thin.py` – Project file
- `workflow.py` – Project file
- `workflows/` – Directory containing workflows components

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Common Patterns

```python
from codomyrmex.orchestrator import StepError, OrchestratorTimeoutError, StateError

# Agent uses StepError
instance = StepError()
```

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
