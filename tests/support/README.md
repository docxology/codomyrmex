# support

Shared helpers for the top-level test suite.

- [`repo_paths.py`](repo_paths.py) — `REPO_ROOT`, `SRC_ROOT`, `PACKAGE_ROOT` path constants.
- [`permissions.py`](permissions.py) — `requires_permission_enforcement` skip marker for chmod-based tests (moot as root or on Windows).
- [`isolated_git.py`](isolated_git.py) — `isolated_git_repo()` runs worktree-creating code in a throwaway repository with an isolated home directory.
- [`stray_paths.py`](stray_paths.py) — `StrayPathGuard` and the `StrayPathPlugin` that `tests/conftest.py` registers: fails the run when tests leave paths in the repository root or a watched directory cannot be inspected (`CODOMYRMEX_STRAY_PATH_GUARD=fail|warn|off`, default `fail`). Observation failures remain recorded after a directory is restored.
- [`event_loop.py`](event_loop.py) — `ensure_current_event_loop()`, which `tests/conftest.py` calls in `pytest_configure` to give the session one owned event loop. It probes without the Python 3.12–3.13 implicit-loop `DeprecationWarning` that pytest 9.2's configure-time `filterwarnings = error` turns into exit 3.
- [`figures.py`](figures.py) — `close_loaded_figures()`, which the root autouse `isolate_matplotlib_figures` fixture runs around every test so leaked pyplot figures cannot reach matplotlib's 20-open-figures warning on an xdist worker.

Parent: [../README.md](../README.md)
