# Codomyrmex Agents — src/codomyrmex/tests/unit/cloud

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `_stubs.py` – Project file
- `conftest.py` – Project file
- `google_workspace/` – Directory containing google_workspace components
- `test_cloud_edge.py` – Project file
- `test_cloud_security_middleware.py` – Project file
- `test_coda_cloud_client.py` – Project file
- `test_coda_io_client.py` – Project file
- `test_coda_io_exceptions.py` – Project file
- `test_coda_io_models.py` – Project file
- `test_coda_models.py` – Project file
- `test_infomaniak_auth.py` – Project file
- `test_infomaniak_base.py` – Project file
- `test_infomaniak_block_storage.py` – Project file
- `test_infomaniak_compute.py` – Project file
- `test_infomaniak_dns.py` – Project file
- `test_infomaniak_exceptions.py` – Project file
- `test_infomaniak_identity.py` – Project file
- `test_infomaniak_metering.py` – Project file
- `test_infomaniak_module_exports.py` – Project file
- `test_infomaniak_network.py` – Project file
- `test_infomaniak_newsletter.py` – Project file
- `test_infomaniak_object_storage.py` – Project file
- `test_infomaniak_orchestration.py` – Project file
- `test_unified_storage.py` – Project file

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
- `_stubs.py`
- `conftest.py`
- `test_cloud_edge.py`
- `test_cloud_security_middleware.py`
- `test_coda_cloud_client.py`
- `test_coda_io_client.py`
- `test_coda_io_exceptions.py`
- `test_coda_io_models.py`
- `test_coda_models.py`
- `test_infomaniak_auth.py`
- `test_infomaniak_base.py`
- `test_infomaniak_block_storage.py`
- `test_infomaniak_compute.py`
- `test_infomaniak_dns.py`
- `test_infomaniak_exceptions.py`
- `test_infomaniak_identity.py`
- `test_infomaniak_metering.py`
- `test_infomaniak_module_exports.py`
- `test_infomaniak_network.py`
- `test_infomaniak_newsletter.py`
- `test_infomaniak_object_storage.py`
- `test_infomaniak_orchestration.py`
- `test_unified_storage.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
