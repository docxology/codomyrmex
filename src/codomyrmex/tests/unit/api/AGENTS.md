# Codomyrmex Agents — src/codomyrmex/tests/unit/api

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `authentication/` – Directory containing authentication components
- `circuit_breaker/` – Directory containing circuit_breaker components
- `mocking/` – Directory containing mocking components
- `pagination/` – Directory containing pagination components
- `py.typed` – Project file
- `rate_limiting/` – Directory containing rate_limiting components
- `test_api_freeze.py` – Project file
- `test_api_http_primitives.py` – Project file
- `test_api_request_response.py` – Project file
- `test_api_routing.py` – Project file
- `test_api_schema.py` – Project file
- `test_api_versioning.py` – Project file
- `test_api_versioning_direct.py` – Project file
- `test_graphql_api.py` – Project file
- `test_openapi.py` – Project file
- `test_openapi_doc_generator.py` – Project file
- `test_openapi_std_generator.py` – Project file
- `test_rest_api.py` – Project file
- `webhooks/` – Directory containing webhooks components

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
- `test_api_freeze.py`
- `test_api_http_primitives.py`
- `test_api_request_response.py`
- `test_api_routing.py`
- `test_api_schema.py`
- `test_api_versioning.py`
- `test_api_versioning_direct.py`
- `test_graphql_api.py`
- `test_openapi.py`
- `test_openapi_doc_generator.py`
- `test_openapi_std_generator.py`
- `test_rest_api.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
