# Codomyrmex Agents — src/codomyrmex/orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Task orchestration with fractal execution, parallel runners, workflow management, and scheduling. Coordinates multi-step agent workflows with resilience patterns.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `agent_supervisor.py` – Internal implementation module
- `config.py` – Configuration management and settings
- `core.py` – Core implementation
- `discovery.py` – Discovery implementation
- `engines/` – Processing engines and execution logic
- `exceptions.py` – Custom exceptions and error types
- `execution/` – execution module implementation
- `fractals/` – fractals module implementation
- `heartbeat.py` – Heartbeat implementation
- `integration.py` – Integration layer for external services
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `module_connector.py` – Internal implementation module
- `monitors/` – monitors module implementation
- `observability/` – observability module implementation
- `pipelines/` – pipelines module implementation
- `process_orchestrator.py` – Internal implementation module
- `py.typed` – PEP 561 marker for typed package
- `resilience/` – resilience module implementation
- `scheduler/` – scheduler module implementation
- `schedulers/` – schedulers module implementation
- `state/` – state module implementation
- `templates/` – Template files and schemas
- `thin.py` – Thin implementation
- `triage_engine.py` – Internal implementation module
- `triggers/` – triggers module implementation
- `workflows/` – workflows module implementation


## Key Interfaces

- `engines/parallel.py — Parallel execution engine`
- `execution/runner.py — Sequential task runner`
- `fractals/executor.py — Fractal task decomposition`
- `scheduler/ — Cron and interval-based scheduling`
- `workflows/workflow.py — Workflow definition and execution`

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `agent_supervisor.py`
- `config.py`
- `core.py`
- `discovery.py`
- `exceptions.py`
- `heartbeat.py`
- `integration.py`
- `mcp_tools.py`
- `module_connector.py`
- `process_orchestrator.py`
- `py.typed`
- `thin.py`
- `triage_engine.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
