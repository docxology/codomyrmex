# Codomyrmex Agents — src/codomyrmex/examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Example implementations and demonstrations.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `agent_orchestration_demo.py` – Internal implementation module
- `api_endpoint_example.py` – Internal implementation module
- `config_validation_report.json` – Config Validation Report implementation
- `fastapi_endpoint.py` – Internal implementation module
- `fastapi_endpoint_example.py` – Internal implementation module
- `generated_api_endpoint.py` – Internal implementation module
- `invalid_prompt_demo.py` – Internal implementation module
- `invalid_prompt_failure.py` – Internal implementation module
- `link_check_report.json` – Link Check Report implementation
- `new_item_endpoint.py` – Internal implementation module
- `py.typed` – PEP 561 marker for typed package
- `simple_endpoint.py` – Internal implementation module
- `test_fastapi_endpoint.py` – Internal implementation module

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
- `agent_orchestration_demo.py`
- `api_endpoint_example.py`
- `config_validation_report.json`
- `fastapi_endpoint.py`
- `fastapi_endpoint_example.py`
- `generated_api_endpoint.py`
- `invalid_prompt_demo.py`
- `invalid_prompt_failure.py`
- `link_check_report.json`
- `new_item_endpoint.py`
- `py.typed`
- `simple_endpoint.py`
- `test_fastapi_endpoint.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
