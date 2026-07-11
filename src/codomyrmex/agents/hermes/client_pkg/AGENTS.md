# client_pkg/ — AGENTS.md

## Purpose

Hermes client implementation split from the former monolithic `hermes_client.py`.

## Key Files

| Module | Mixin / type | Responsibility |
| --- | --- | --- |
| `errors.py` | `HermesError`, `AutoRetryException` | Exceptions + auto-heal allowlist |
| `core.py` | `HermesClient` | `__init__`, backend properties, MRO root |
| `execution.py` | `HermesExecutionMixin` | CLI/Ollama execute + stream |
| `context_memory.py` | `HermesContextMixin` | Summarize + Obsidian export |
| `chat.py` | `HermesChatMixin` | `chat_session` loop |
| `session_ops.py` | `HermesSessionOpsMixin` | Worktrees, fork/merge, batch |
| `maintenance.py` | `HermesMaintenanceMixin` | Doctor, skills, coverage loop |
| `gateway.py` | `HermesGatewayMixin` | Gateway status, FastMCP scaffold |

## Dependencies

Import via `codomyrmex.agents.hermes.hermes_client` (shim) or `client_pkg` directly.

## Development Guidelines

- Each mixin owns one responsibility; `core.py`'s `HermesClient` composes them via MRO — new behavior gets its own mixin, not a `core.py` addition.
- Keep the `hermes_client` shim's public surface (`AUTO_HEAL_ALLOWLIST`, `AutoRetryException`, `HermesClient`, `HermesError`) stable.
