# Codomyrmex Agents — src/codomyrmex/tests/unit/mcp

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Validation coverage, fixtures, and regression checks for Mcp.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `py.typed` – Project file
- `test_api_versioning.py` – Project file
- `test_circuit_breaker.py` – Project file
- `test_event_bridge.py` – Project file
- `test_mcp_bridge_errors.py` – Project file
- `test_mcp_client.py` – Project file
- `test_mcp_concurrent_tools.py` – Project file
- `test_mcp_discovery.py` – Project file
- `test_mcp_discovery_cache.py` – Project file
- `test_mcp_discovery_engine.py` – Project file
- `test_mcp_discovery_metrics.py` – Project file
- `test_mcp_error_envelope.py` – Project file
- `test_mcp_http_and_errors.py` – Project file
- `test_mcp_observability.py` – Project file
- `test_mcp_resource_read.py` – Project file
- `test_mcp_smoke.py` – Project file
- `test_mcp_stress.py` – Project file
- `test_mcp_taxonomy.py` – Project file
- `test_mcp_tool_isolation.py` – Project file
- `test_mcp_transport_stress.py` – Project file
- `test_mcp_validation.py` – Project file
- `test_mutation_kill.py` – Project file
- `test_rate_limiter.py` – Project file
- `test_transport_robustness.py` – Project file
- `test_ws_handler.py` – Project file

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
- `__init__.py`
- `py.typed`
- `test_api_versioning.py`
- `test_circuit_breaker.py`
- `test_event_bridge.py`
- `test_mcp_bridge_errors.py`
- `test_mcp_client.py`
- `test_mcp_concurrent_tools.py`
- `test_mcp_discovery.py`
- `test_mcp_discovery_cache.py`
- `test_mcp_discovery_engine.py`
- `test_mcp_discovery_metrics.py`
- `test_mcp_error_envelope.py`
- `test_mcp_http_and_errors.py`
- `test_mcp_observability.py`
- `test_mcp_resource_read.py`
- `test_mcp_smoke.py`
- `test_mcp_stress.py`
- `test_mcp_taxonomy.py`
- `test_mcp_tool_isolation.py`
- `test_mcp_transport_stress.py`
- `test_mcp_validation.py`
- `test_mutation_kill.py`
- `test_rate_limiter.py`
- `test_transport_robustness.py`
- `test_ws_handler.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
