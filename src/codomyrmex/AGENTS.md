<!-- agents: curated -->

# Codomyrmex Agents — src/codomyrmex

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `src/codomyrmex`
- **Human overview**: [README.md](README.md)
- **Functional spec**: [SPEC.md](SPEC.md)
- **Repository agents**: [../../AGENTS.md](../../AGENTS.md)
- **Parent (`src/`)**: [../AGENTS.md](../AGENTS.md)
- **Live counts**: [docs/reference/inventory.md](../../docs/reference/inventory.md)

## Purpose

Installable package root: **128** top-level subpackages (each with `__init__.py`), plus `tests/`, `examples/`, and per-package RASP docs. Programmatic names: `codomyrmex.list_modules()` in [__init__.py](__init__.py). Full directory listing: [README.md](README.md) (Directory Contents).

## Active Components (summary)

Top-level packages are listed in [README.md § Directory Contents](README.md#directory-contents). Do not duplicate that list here; edit the README when the tree changes.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` — agent coordination (this file)
- `README.md` — directory overview and module table
- `INDEX.md`, `PAI.md`, `SPEC.md` — project signposts
- `__init__.py` — package exports and `list_modules()`
- `conftest.py`, `py.typed` — test / typing markers

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [src](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../README.md - Main project documentation
