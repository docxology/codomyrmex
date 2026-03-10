# Codomyrmex Agents — scripts/maintenance

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Automation and utility scripts.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `audit_stubs.py` – Project file
- `check_dependencies.py` – Project file
- `fix_docstrings_v2.py` – Project file
- `fix_llm_rasp.py` – Project file
- `fix_nested_rasp.py` – Project file
- `generate_config_docs.py` – Project file
- `generate_configs.py` – Project file
- `list_all_models.py` – Project file
- `list_models.py` – Project file
- `patch_basic_usage.py` – Project file
- `patch_docs.py` – Project file
- `sync_docs.py` – Project file
- `update_overview.py` – Project file
- `verify_index.py` – Project file

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
- `audit_stubs.py`
- `check_dependencies.py`
- `fix_docstrings_v2.py`
- `fix_llm_rasp.py`
- `fix_nested_rasp.py`
- `generate_config_docs.py`
- `generate_configs.py`
- `list_all_models.py`
- `list_models.py`
- `patch_basic_usage.py`
- `patch_docs.py`
- `sync_docs.py`
- `update_overview.py`
- `verify_index.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [scripts](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../README.md - Main project documentation
