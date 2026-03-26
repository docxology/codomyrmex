# PAI PM Module Integration — Design Document

**Date:** 2026-03-05
**Status:** Complete
**PRD:** `MEMORY/WORK/20260305-000000_pai-pm-module-integration/PRD.md`

## Summary

Integrated the PAI Project Manager TypeScript/Bun server (`scripts/pai/pm/`) as a Python module (`src/codomyrmex/pai_pm/`) following the `aider` module pattern. Fixed two P0 security gaps in `trust_gateway.py`. Created 57 zero-mock tests (all passing).

## Triple Review Order

### Pass 1 — Security (P0 Fixes)

**Fix 1: Trust ledger atomic write + chmod 0600**
`trust_gateway.py:_save()` was using `write_text()` directly — world-readable during write and no permission restriction. Fixed with `.tmp → rename` pattern + `chmod(0o600)` before rename.

**Fix 2: Threading lock for `_pending_confirmations`**
`_pending_confirmations` was accessed across threads without a lock. Added `_confirmations_lock = threading.Lock()` and wrapped the confirmation block in `trusted_call_tool()` with `with _confirmations_lock:`. Renamed cleanup function to `_cleanup_expired_confirmations_locked()` with docstring making clear it must be called with lock held.

**Bonus fix: SyntaxError in `environment_setup/dependency_resolver.py:119`**
A dangling `try:` block (missing `except ImportError:` for the `import tomllib` guard) caused `pkgutil.walk_packages` to raise `SyntaxError` during the full module scan, preventing `TrustRegistry` from being instantiated in tests. Fixed by adding the correct `except ImportError:` + early return.

### Pass 2 — New Module

**Python files created:**
- `exceptions.py` — 5-class hierarchy (`PaiPmError` → 4 subtypes)
- `config.py` — `PaiPmConfig` dataclass with 5 env-var-backed fields
- `server_manager.py` — `PaiPmServerManager` with subprocess lifecycle, PID file (0o600), env allowlist
- `client.py` — `PaiPmClient` stdlib HTTP (no extra deps), 8 endpoint methods
- `mcp_tools.py` — 6 `@mcp_tool` definitions (auto-discovered)
- `__init__.py` — exports + `HAS_BUN` flag

**TypeScript source:**
Copied (rsync, excluding `node_modules/`) from `scripts/pai/pm/` to `src/codomyrmex/pai_pm/server/`.

**pyproject.toml** (`[tool.pytest.ini_options]`): Added `pai_pm:` marker.
**pyproject.toml:** Added `[project.optional-dependencies.pai_pm]` (no Python deps, requires bun).

### Pass 3 — Documentation

RASP docs created: `README.md`, `SPEC.md`, `AGENTS.md`, `PAI.md`.

## Key Design Decisions

1. **`_cleanup_expired_confirmations_locked()` naming** — "locked" suffix convention (used in CPython itself) signals to callers that the lock must already be held, preventing accidental double-acquisition deadlock.

2. **Atomic write with `.tmp` + rename** — OS guarantees rename is atomic. Setting permissions on `.tmp` *before* rename eliminates the brief readable window.

3. **`_build_safe_env()` allowlist vs blocklist** — Allowlist approach (only PAI_*, GOOGLE_*, AGENTMAIL_*, common system vars) is safer than a blocklist. Blocklist grows with each new API key env var.

4. **stdlib HTTP only in `client.py`** — `urllib.request` instead of `requests` or `httpx`. Zero new Python dependencies for a module that wraps a TypeScript server.

5. **`rsync` over `git mv`** — Moving `node_modules/` via git would pollute history with hundreds of files. `rsync --exclude='node_modules/'` copies only source files.

## Test Counts

| Area | Tests |
|------|-------|
| Security (trust_gateway) | 8 |
| pai_pm exceptions | 9 |
| pai_pm config | 12 |
| pai_pm server_manager | 17 |
| pai_pm client | 7 |
| pai_pm MCP tools | 8 |
| **Total** | **57** |

All tests pass. Ruff zero violations.
