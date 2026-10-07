# support

Shared helpers for the top-level test suite.

- [`repo_paths.py`](repo_paths.py) — `REPO_ROOT`, `SRC_ROOT`, `PACKAGE_ROOT` path constants.
- [`permissions.py`](permissions.py) — `requires_permission_enforcement` skip marker for chmod-based tests (moot as root or on Windows).
- [`isolated_git.py`](isolated_git.py) — `isolated_git_repo()` runs worktree-creating code in a throwaway repository with an isolated home directory.

Parent: [../README.md](../README.md)
