---
task: PAI PM module integration triple review security quality docs
slug: 20260305-000000_pai-pm-module-integration
effort: Comprehensive
phase: complete
progress: 52/52
mode: ALGORITHM
started: 2026-03-05T00:00:00Z
updated: 2026-03-05T00:00:00Z
---

## Context

The `scripts/pai/pm/` directory contains a production TypeScript/Bun PAI Project Manager server
(HTTP REST API on port 8889, 9 route modules). It needs to be integrated as
`src/codomyrmex/pai_pm/` — a Python wrapper module following the `aider` pattern.

Two P0 security gaps exist in `trust_gateway.py` that must be fixed first:
1. Trust ledger file has no permission restrictions (world-readable)
2. `_pending_confirmations` dict accessed without a lock (race condition)

Triple review order: Security → Quality (new module) → Documentation (RASP).

### Risks
- threading.Lock on confirmations must be careful not to double-acquire (cleanup must be called with lock held)
- Atomic write with `.tmp` rename must handle cross-filesystem edge cases
- `_build_safe_env()` must not leak API keys to TypeScript subprocess
- Module auto-discovery requires valid `mcp_tools.py` — any syntax error breaks 121 modules

## Criteria

### Pass 1: Security Fixes

- [ ] ISC-1: `_save()` writes to `.tmp` file before renaming to final path
- [ ] ISC-2: `.tmp` file has `chmod(0o600)` set before rename
- [ ] ISC-3: Final `trust_ledger.json` has mode `0o600` after save
- [ ] ISC-4: `_load()` migrates existing file to `0o600` if wrong mode
- [ ] ISC-5: `_confirmations_lock = threading.Lock()` declared at module level
- [ ] ISC-6: `_cleanup_expired_confirmations_locked()` does NOT acquire lock internally
- [ ] ISC-7: Confirmation block in `trusted_call_tool()` wrapped in `with _confirmations_lock:`
- [ ] ISC-8: Test `TestTrustLedgerPermissions` verifies `_save()` creates file mode `0o600`
- [ ] ISC-9: Test `TestTrustLedgerAtomicWrite` verifies `.tmp` file absent after save
- [ ] ISC-10: Test `TestConfirmationsThreadSafety` runs 50 concurrent threads without RuntimeError

### Pass 2: New Module — pai_pm

- [ ] ISC-11: `exceptions.py` defines `PaiPmError`, `PaiPmNotInstalledError`, `PaiPmServerError`, `PaiPmTimeoutError`, `PaiPmConnectionError`
- [ ] ISC-12: All exceptions in `exceptions.py` form correct inheritance hierarchy
- [ ] ISC-13: `config.py` has `PaiPmConfig` dataclass with all 5 env-var-backed fields
- [ ] ISC-14: `PAI_PM_PORT` defaults to `8889` in `config.py`
- [ ] ISC-15: `PAI_PM_HOST` defaults to `127.0.0.1` in `config.py`
- [ ] ISC-16: `server_script` field defaults to `pai_pm/server/server.ts` relative path
- [ ] ISC-17: `server_manager.py` has `_find_bun()` raising `PaiPmNotInstalledError` when absent
- [ ] ISC-18: `server_manager.py` has `is_running()` using urllib (stdlib only), never raises
- [ ] ISC-19: `server_manager.py` has `start()` raising `PaiPmServerError` on timeout
- [ ] ISC-20: `server_manager.py` has `stop()` sending SIGTERM then SIGKILL after 5s
- [ ] ISC-21: `_build_safe_env()` includes `NO_COLOR=1` in output
- [ ] ISC-22: `_build_safe_env()` excludes `ANTHROPIC_API_KEY` from output
- [ ] ISC-23: `_build_safe_env()` excludes `OPENAI_API_KEY` from output
- [ ] ISC-24: PID file written with chmod `0o600` in `_write_pid()`
- [ ] ISC-25: `client.py` has `PaiPmClient` with `health()`, `get_state()`, `get_awareness()`, `dispatch_execute()`, `dispatch_status()`, `list_missions()`, `list_projects()`, `list_tasks()`
- [ ] ISC-26: `client.py` raises `PaiPmConnectionError` when server unreachable
- [ ] ISC-27: `mcp_tools.py` has `pai_pm_start` tool decorated with `@mcp_tool`
- [ ] ISC-28: `mcp_tools.py` has `pai_pm_stop` tool
- [ ] ISC-29: `mcp_tools.py` has `pai_pm_health` tool
- [ ] ISC-30: `mcp_tools.py` has `pai_pm_get_state` tool
- [ ] ISC-31: `mcp_tools.py` has `pai_pm_get_awareness` tool
- [ ] ISC-32: `mcp_tools.py` has `pai_pm_dispatch` tool
- [ ] ISC-33: All 6 MCP tools return `{"status": "error", "message": ...}` on exception
- [ ] ISC-34: `__init__.py` exports `PaiPmConfig`, all exceptions, `PaiPmServerManager`, `HAS_BUN`, `get_bun_version`, `get_config`
- [ ] ISC-35: `pyproject.toml` has `[project.optional-dependencies.pai_pm]` entry
- [ ] ISC-36: `pytest.ini` has `pai_pm:` marker after `aider:` line
- [ ] ISC-37: TypeScript files moved from `scripts/pai/pm/` to `src/codomyrmex/pai_pm/server/`

### Pass 2: Tests

- [ ] ISC-38: `tests/unit/pai_pm/__init__.py` exists
- [ ] ISC-39: `tests/unit/pai_pm/conftest.py` defines `bun_installed`, `requires_bun`, `requires_running_server`
- [ ] ISC-40: `test_exceptions.py` verifies hierarchy and isinstance relationships
- [ ] ISC-41: `test_config.py` verifies defaults and env var overrides
- [ ] ISC-42: `test_server_manager.py` verifies `HAS_BUN` is bool without bun
- [ ] ISC-43: `test_server_manager.py` verifies `_write_pid()` creates file mode `0o600`
- [ ] ISC-44: `test_server_manager.py` verifies `_build_safe_env()` excludes API keys
- [ ] ISC-45: `test_client.py` verifies `PaiPmConnectionError` raised on unreachable port
- [ ] ISC-46: `test_mcp_tools.py` verifies `pai_pm_health()` returns dict when server down

### Pass 3: Documentation

- [ ] ISC-47: `README.md` created with MCP tools table, env vars table
- [ ] ISC-48: `SPEC.md` created with 6 tool schemas and error taxonomy
- [ ] ISC-49: `AGENTS.md` created with decision tree
- [ ] ISC-50: `PAI.md` created with 7-phase mapping table
- [ ] ISC-51: `docs/plans/2026-03-05-pai-pm-module-integration.md` design doc saved
- [ ] ISC-52: Ruff check passes with zero violations on new `pai_pm/` module

## Decisions

## Verification
