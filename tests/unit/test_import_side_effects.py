"""Importing a codomyrmex package must not write to stdout or the CWD.

Tools that emit machine-readable output import codomyrmex packages: the
documentation reference checker prints JSON
(``scripts/documentation/validate_code_references.py --format json``) and the
MCP stdio server reserves stdout for JSON-RPC frames. A package that logs or
prints while it is imported corrupts that output. Library code must not
configure logging on import (no ``logging.basicConfig``, no ``setup_logging``,
no handlers on the root logger) and must not ``print`` at module level; entry
points configure logging themselves, and diagnostics belong on stderr.

Whether a misconfigured handler actually prints during the import depends on
the environment (matplotlib, for example, logs at INFO only while it builds
its font cache), so the probe also fails when the import leaves handlers on,
or changes the level of, the root logger.

Each import runs in a fresh interpreter, so modules already imported by the
test session cannot hide a side effect. The interpreter starts in an empty
directory, which must still be empty afterwards: importing a package must not
create output directories in the current working directory.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from tests.support.repo_paths import PACKAGE_ROOT, SRC_ROOT

# Exit statuses the probe uses for "an optional third-party dependency is
# missing" and "the import configured the root logger".
_MISSING_OPTIONAL_DEPENDENCY = 75
_ROOT_LOGGER_CONFIGURED = 76

# Runs in the child interpreter. A missing module outside codomyrmex is an
# optional dependency that is not installed; an unresolved codomyrmex module
# is a real defect and fails the test like any other import error.
_PROBE = """
import importlib
import logging
import sys

name = sys.argv[1]
missing_dependency_status, root_configured_status = map(int, sys.argv[2:4])
try:
    importlib.import_module(name)
except ImportError as exc:
    missing = exc.name or ""
    if missing == "codomyrmex" or missing.startswith("codomyrmex."):
        raise
    sys.stderr.write(f"{type(exc).__name__}: {exc}")
    sys.exit(missing_dependency_status)
root = logging.getLogger()
if root.handlers or root.level != logging.WARNING:
    level = logging.getLevelName(root.level)
    sys.stderr.write(f"root logger: level={level} handlers={root.handlers!r}")
    sys.exit(root_configured_status)
"""

# Modules that configured logging or printed on import before they were
# fixed. They run in the fast unit lane; the full sweep below runs every
# top-level package.
_PREVIOUSLY_NOISY = [
    "codomyrmex.agents.ai_code_editing.droid_manager",
    "codomyrmex.agents.droid.run_todo_droid",
    "codomyrmex.documentation",
    "codomyrmex.documentation.scripts.apply_curated_markers",
    "codomyrmex.documentation.scripts.bootstrap_agents_readmes",
    "codomyrmex.documentation.scripts.smart_template_engine",
    "codomyrmex.maintenance",
    "codomyrmex.meme.verify_all",
    "codomyrmex.system_discovery",
]


def _top_level_packages() -> list[str]:
    return sorted(
        f"codomyrmex.{path.name}"
        for path in PACKAGE_ROOT.iterdir()
        if (path / "__init__.py").is_file()
    )


def _assert_import_is_silent(module: str, cwd: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(SRC_ROOT), env.get("PYTHONPATH")])
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            _PROBE,
            module,
            str(_MISSING_OPTIONAL_DEPENDENCY),
            str(_ROOT_LOGGER_CONFIGURED),
        ],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    if result.returncode == _MISSING_OPTIONAL_DEPENDENCY:
        pytest.skip(f"{module}: optional dependency not installed ({result.stderr})")
    assert result.returncode != _ROOT_LOGGER_CONFIGURED, (
        f"importing {module} configured the root logger; library code must "
        f"not call setup_logging() or logging.basicConfig() on import:\n"
        f"{result.stderr}"
    )
    assert result.returncode == 0, f"importing {module} failed:\n{result.stderr}"
    assert result.stdout == "", (
        f"importing {module} wrote to stdout; library code must not configure "
        f"logging or print on import:\n{result.stdout}"
    )
    created = sorted(path.name for path in cwd.iterdir())
    assert not created, f"importing {module} created {created} in the CWD"


@pytest.mark.unit
def test_top_level_package_list_is_not_empty() -> None:
    packages = _top_level_packages()
    assert "codomyrmex.logging_monitoring" in packages
    assert len(packages) > 100


@pytest.mark.unit
@pytest.mark.parametrize("module", _PREVIOUSLY_NOISY)
def test_previously_noisy_import_is_silent(module: str, tmp_path: Path) -> None:
    _assert_import_is_silent(module, tmp_path)


@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.parametrize("module", _top_level_packages())
def test_top_level_import_is_silent(module: str, tmp_path: Path) -> None:
    _assert_import_is_silent(module, tmp_path)
