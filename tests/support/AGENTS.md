# AGENTS.md — `codomyrmex/tests/support`

## Purpose
Shared test-support helpers for the top-level `tests/` suite.

## Layout
- `repo_paths.py` — canonical path constants (`REPO_ROOT`, `SRC_ROOT`, `PACKAGE_ROOT`) for locating the repo and `src/codomyrmex/` from tests.

## Gotchas
- Import path helpers belong here, not duplicated in individual test modules.
