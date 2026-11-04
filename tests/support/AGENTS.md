# AGENTS.md — `codomyrmex/tests/support`

## Purpose

Shared test-support helpers for the top-level `tests/` suite.

## Layout

- `repo_paths.py` — canonical path constants (`REPO_ROOT`, `SRC_ROOT`, `PACKAGE_ROOT`) for locating the repo and `src/codomyrmex/` from tests.
- `permissions.py` — `RUNNING_AS_ROOT` and the `requires_permission_enforcement` skip marker for tests that rely on chmod denying access.
- `isolated_git.py` — `isolated_git_repo(tmp_path, monkeypatch)` creates a one-commit repository, chdirs into it and points `HOME`/`USERPROFILE` at `tmp_path`; use it for anything that runs `git worktree`/`git branch` so tests never touch the developer's clone.
- `git_temp_repository.py` — `initialize_repository(path, root=tmp_path)` initialises a throwaway repository and writes the test identity into **its own** `.git/config`; `assert_contained(path, root)` refuses a target outside the test's own tree. Use it instead of a session-wide commit identity, which reaches every Git process the suite starts.

## Gotchas

- Import path helpers belong here, not duplicated in individual test modules.
