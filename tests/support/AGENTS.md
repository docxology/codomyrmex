# AGENTS.md — `codomyrmex/tests/support`

## Purpose

Shared test-support helpers for the top-level `tests/` suite.

## Layout

- `repo_paths.py` — canonical path constants (`REPO_ROOT`, `SRC_ROOT`, `PACKAGE_ROOT`) for locating the repo and `src/codomyrmex/` from tests.
- `permissions.py` — `RUNNING_AS_ROOT` and the `requires_permission_enforcement` skip marker for tests that rely on chmod denying access.
- `isolated_git.py` — `isolated_git_repo(tmp_path, monkeypatch)` creates a one-commit repository, chdirs into it and points `HOME`/`USERPROFILE` at `tmp_path`; use it for anything that runs `git worktree`/`git branch` so tests never touch the developer's clone.

## Gotchas

- Import path helpers belong here, not duplicated in individual test modules.
