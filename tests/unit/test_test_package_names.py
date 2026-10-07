"""Guard against test packages that shadow real modules.

pytest runs with ``--import-mode=importlib``. A test directory with an
``__init__.py`` whose parent has none (every ``tests/unit/<name>/`` package)
is imported as the top-level module ``<name>``. When that name is also a real
module -- stdlib, third-party or ours -- the test package replaces it in
``sys.modules`` for the rest of the worker's session. That is how
``tests/unit/tree_sitter/`` hid the py-tree-sitter library and silently
skipped every parser test, and how ``tests/unit/soul/`` hid the ``soul``
SDK that ``codomyrmex.soul`` wraps.

Test directories that collide must not be packages (drop ``__init__.py``;
importlib mode gives their modules unique names).
"""

from __future__ import annotations

import site
import sys
from importlib.machinery import PathFinder

import pytest
from tests.support.repo_paths import REPO_ROOT

TESTS = REPO_ROOT / "tests"


def _top_level_test_packages() -> dict[str, str]:
    """Map each top-level module name pytest derives to its test directory."""
    roots: dict[str, str] = {}
    for init in TESTS.rglob("__init__.py"):
        package = init.parent
        if (package.parent / "__init__.py").exists():
            continue  # nested inside another package: not a top-level name
        roots[package.name] = str(package.relative_to(REPO_ROOT))
    return roots


def _real_module_exists(name: str) -> bool:
    if name in sys.stdlib_module_names:
        return True
    # PathFinder ignores sys.modules, so an already-imported test package
    # cannot mask the real module. The search path is fixed rather than taken
    # from sys.path, which other tests may have extended: the repository root
    # (scripts and tools put it on sys.path), src/, and installed packages.
    search = [str(REPO_ROOT), str(REPO_ROOT / "src"), *site.getsitepackages()]
    spec = PathFinder.find_spec(name, search)
    # Plain directories (namespace packages) do not count: tests create output
    # directories such as git_analysis/ in the working directory.
    return spec is not None and spec.origin is not None


@pytest.mark.unit
def test_test_packages_do_not_shadow_real_modules() -> None:
    clashes = [
        f"{path} is imported as '{name}', which is a real module"
        for name, path in sorted(_top_level_test_packages().items())
        if name != "tests" and _real_module_exists(name)
    ]
    assert not clashes, "remove __init__.py from:\n" + "\n".join(clashes)
