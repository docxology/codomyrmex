# Codomyrmex Agents — src/codomyrmex/cloud/infomaniak

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `auth.py` – Project file
- `base.py` – Project file
- `block_storage/` – Directory containing block_storage components
- `compute/` – Directory containing compute components
- `dns/` – Directory containing dns components
- `exceptions.py` – Project file
- `identity/` – Directory containing identity components
- `metering/` – Directory containing metering components
- `network/` – Directory containing network components
- `newsletter/` – Directory containing newsletter components
- `object_storage/` – Directory containing object_storage components
- `orchestration/` – Directory containing orchestration components
- `py.typed` – Project file
- `security.py` – Project file

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
- `auth.py`
- `base.py`
- `exceptions.py`
- `py.typed`
- `security.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [cloud](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
