# src

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: April 2026

## Overview

`src/` contains the installable Codomyrmex Python package and its source-adjacent documentation. The package root is [codomyrmex/](codomyrmex/), which exposes the module facade, CLI entry point, MCP tools, agent integrations, and the repository's source-level tests.

Current volatile counts are documented in [../docs/reference/inventory.md](../docs/reference/inventory.md) and refreshed with `uv run python scripts/doc_inventory.py` from the repository root. Avoid duplicating those numbers in this file unless they are generated.

## Architecture Boundaries

- `codomyrmex/__init__.py` owns package metadata, lazy submodule loading, and the public module list.
- `codomyrmex/cli/` owns command-line dispatch; command handlers should delegate to module APIs instead of embedding domain logic.
- `codomyrmex/model_context_protocol/` owns MCP decorators, schemas, transport, discovery, and tool registration.
- `codomyrmex/agents/`, `codomyrmex/skills/`, and `codomyrmex/tool_use/` provide agent, skill, and tool registries that expose capabilities to higher-level orchestration.
- `codomyrmex/logging_monitoring/`, `codomyrmex/config_management/`, `codomyrmex/validation/`, and `codomyrmex/exceptions/` are foundation modules used across the tree.
- `codomyrmex/tests/` contains source-level unit, integration, and performance tests; package builds exclude tests per `pyproject.toml`.

## Directory Contents

- `AGENTS.md` – Agent coordination for the source surface
- `INDEX.md` – Source index
- `PAI.md` – PAI-facing source notes
- `README.md` – This overview
- `SPEC.md` – Source-surface specification
- `__init__.py` – Source-root marker
- `codomyrmex/` – Installable package root

## Development Expectations

- Keep public API changes synchronized with module `README.md`, `SPEC.md`, `API_SPECIFICATION.md`, and `MCP_TOOL_SPECIFICATION.md` files where present.
- Preserve module boundaries: foundation modules should not depend on specialized agent or domain modules.
- Use the centralized logging and validation helpers instead of ad-hoc print/error handling in shared code.
- Prefer deterministic tests and real components; avoid mocks unless a local module explicitly documents an exception.
- Before changing generated documentation, check for curated markers and repository guidance in [../AGENTS.md](../AGENTS.md).

## Verification

Useful targeted checks from the repository root:

```bash
uv run python scripts/doc_inventory.py
uv run python -m compileall -q src
uv run --no-sync ruff check src/codomyrmex/documentation scripts/doc_inventory.py scripts/rasp_gap_report.py
PYTHONPATH=src python3 src/codomyrmex/documentation/scripts/check_doc_links.py
```

## Navigation

- **Project Root**: [../README.md](../README.md)
- **Root Agent Guide**: [../AGENTS.md](../AGENTS.md)
- **Package Root**: [codomyrmex/README.md](codomyrmex/README.md)
- **Architecture**: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Inventory**: [../docs/reference/inventory.md](../docs/reference/inventory.md)
- **Related Agents**: [AGENTS.md](AGENTS.md)
