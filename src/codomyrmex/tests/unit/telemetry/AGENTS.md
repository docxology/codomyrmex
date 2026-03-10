# Codomyrmex Agents — src/codomyrmex/tests/unit/telemetry

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `metrics/` – Directory containing metrics components
- `test_agent_hooks.py` – Project file
- `test_alerts.py` – Project file
- `test_dashboard_models.py` – Project file
- `test_exporters.py` – Project file
- `test_mcp_tools_telemetry.py` – Project file
- `test_metrics.py` – Project file
- `test_observability_pipeline.py` – Project file
- `test_slo.py` – Project file
- `test_spans.py` – Project file
- `test_telemetry_concurrency.py` – Project file
- `test_telemetry_dashboard.py` – Project file
- `test_telemetry_dashboard_core.py` – Project file
- `test_trace_context.py` – Project file
- `test_tracing_framework.py` – Project file
- `test_tracing_models.py` – Project file
- `tracing/` – Directory containing tracing components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `test_agent_hooks.py`
- `test_alerts.py`
- `test_dashboard_models.py`
- `test_exporters.py`
- `test_mcp_tools_telemetry.py`
- `test_metrics.py`
- `test_observability_pipeline.py`
- `test_slo.py`
- `test_spans.py`
- `test_telemetry_concurrency.py`
- `test_telemetry_dashboard.py`
- `test_telemetry_dashboard_core.py`
- `test_trace_context.py`
- `test_tracing_framework.py`
- `test_tracing_models.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
