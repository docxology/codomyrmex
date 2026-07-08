# AGENTS.md — `mcp_tools_pkg/`

## Purpose

Hermes MCP tool implementations, split by category for maintainability.

## Key Files

| Module | Tools | Role |
| --- | ---: | --- |
| `_client.py` | — | Shared `HermesClient` factory (`_factory_override` for tests) |
| `memory.py` | 6 | Recall, session search, KI graph/extract/search/dedupe |
| `skills.py` | 8 | Skills registry, templates, install, FastMCP scaffold |
| `execution.py` | 7 | Execute, stream, chat session, batch, sampling, spawn |
| `sessions.py` | 11 | Session CRUD, fork/merge/export, worktrees, archive |
| `tasks.py` | 6 | Canvas, vault search, task CRUD, delegate, log chunk |
| `status.py` | 17 | Health, doctor, gateway, pairing, model info |

## Dependencies

Public imports remain `from codomyrmex.agents.hermes import mcp_tools` or
`from codomyrmex.agents.hermes.mcp_tools import hermes_status`.

## Development Guidelines

- New MCP tools join the module matching their category; keep each category module under ~600 LOC (per the original P0 split rationale).
- Route client access through `_client.py`'s factory so tests can use `_factory_override`.
