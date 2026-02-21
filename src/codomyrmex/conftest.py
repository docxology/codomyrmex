"""Root-level conftest for Codomyrmex test collection.

Handles Python 3.14+ stdlib ``compression`` module namespace collision.
"""

import importlib.util
import os
import sys
import sysconfig


def pytest_configure(config):
    """Pre-load stdlib ``compression`` to prevent namespace shadowing.

    Python 3.14 added a ``compression`` package to the stdlib.  Because
    pytest sets ``pythonpath = src`` (adding ``src/`` to ``sys.path``) and
    ``testpaths = src/codomyrmex``, our ``codomyrmex/compression/``
    directory can shadow the stdlib ``compression`` when other stdlib
    modules (e.g. ``gzip``) do ``from compression._common import …``.

    This hook runs before any test file collection, ensuring the real
    stdlib ``compression`` is cached in ``sys.modules`` first.
    """
    if sys.version_info >= (3, 14) and "compression" not in sys.modules:
        stdlib_dir = sysconfig.get_path("stdlib")
        stdlib_init = os.path.join(stdlib_dir, "compression", "__init__.py")
        if os.path.isfile(stdlib_init):
            spec = importlib.util.spec_from_file_location(
                "compression",
                stdlib_init,
                submodule_search_locations=[
                    os.path.join(stdlib_dir, "compression"),
                ],
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules["compression"] = mod
            spec.loader.exec_module(mod)
