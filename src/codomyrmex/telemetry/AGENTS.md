# Codomyrmex Agents — src/codomyrmex/telemetry

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Metrics collection, tracing, dashboards, and observability. OpenTelemetry integration with StatsD client and token tracking.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `agent_hooks.py` – Internal implementation module
- `alerting/` – alerting module implementation
- `context/` – context module implementation
- `dashboard/` – dashboard module implementation
- `exporters/` – exporters module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `metric_aggregator.py` – Internal implementation module
- `metrics/` – metrics module implementation
- `otel.py` – Otel implementation
- `pipeline.py` – Pipeline implementation
- `py.typed` – PEP 561 marker for typed package
- `sampling/` – sampling module implementation
- `spans/` – spans module implementation
- `tracing/` – tracing module implementation


## Key Interfaces

- `metrics/statsd_client.py — StatsD metrics collection`
- `metrics/token_tracker.py — LLM token usage tracking`
- `tracing/call_graph.py — Function call tracing and visualization`
- `otel.py — OpenTelemetry integration`

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
- `agent_hooks.py`
- `mcp_tools.py`
- `metric_aggregator.py`
- `otel.py`
- `pipeline.py`
- `py.typed`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
