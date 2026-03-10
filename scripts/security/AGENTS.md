# Codomyrmex Agents — scripts/security

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Automation and utility scripts.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `audit/` – Directory containing audit components
- `audit_secrets.py` – Project file
- `compliance/` – Directory containing compliance components
- `examples/` – Directory containing examples components
- `orchestrate.py` – Project file
- `scan_dependencies.py` – Project file
- `scanning/` – Directory containing scanning components
- `secrets/` – Directory containing secrets components

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
- `audit_secrets.py`
- `orchestrate.py`
- `scan_dependencies.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [scripts](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../README.md - Main project documentation
