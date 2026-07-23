"""CLI startup benchmark.

Measures the wall-clock time to run ``codomyrmex --help`` and analyses
heaviest imports via ``importlib`` hooks.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import time
import warnings
from types import ModuleType
from typing import Any


def benchmark_cli_startup(
    command: list[str] | None = None,
    iterations: int = 5,
) -> dict[str, Any]:
    """Measure wall-clock time for CLI startup.

    Parameters
    ----------
    command:
        Command to run. Defaults to ``["python", "-m", "codomyrmex", "--help"]``.
    iterations:
        Number of runs to average over.

    Returns
    -------
    dict with ``avg_seconds``, ``min_seconds``, ``max_seconds``, ``times``.
    """
    if command is None:
        command = [sys.executable, "-c", "import codomyrmex"]

    times: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        subprocess.run(
            command,
            capture_output=True,
            timeout=30,
            check=False,
        )
        t1 = time.perf_counter()
        times.append(t1 - t0)

    return {
        "command": command,
        "iterations": iterations,
        "avg_seconds": sum(times) / len(times),
        "min_seconds": min(times),
        "max_seconds": max(times),
        "times": times,
    }


def measure_import_time(module_name: str) -> dict[str, Any]:
    """Measure the time to import a single module.

    Parameters
    ----------
    module_name:
        Fully qualified module name.

    Returns
    -------
    dict with ``module``, ``import_time_seconds``, ``already_loaded``.
    """
    already_loaded = module_name in sys.modules

    # Importing into the current interpreter and restoring only sys.modules is
    # unsafe for packages: parent-package attributes retain references to the
    # freshly imported child graph.  Subsequent code can then observe two
    # distinct class/singleton identities for the same qualified module.
    # Snapshot the module table and package dictionaries so the probe is cold
    # without leaving a duplicate graph behind.  The top-level package timing
    # test uses a subprocess because it intentionally measures interpreter
    # startup as a whole.
    cached_modules = dict(sys.modules)
    package_state = {
        module: dict(module.__dict__)
        for module in set(cached_modules.values())
        if isinstance(module, ModuleType) and hasattr(module, "__path__")
    }
    sys.modules.pop(module_name, None)
    for name in list(sys.modules):
        if name.startswith(f"{module_name}."):
            sys.modules.pop(name, None)
    parent_name, _, child_name = module_name.rpartition(".")
    parent_module = sys.modules.get(parent_name)
    if parent_module is not None:
        parent_module.__dict__.pop(child_name, None)

    try:
        started = time.perf_counter()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            importlib.import_module(module_name)
        import_time = time.perf_counter() - started
    except ImportError:
        import_time = -1.0
    finally:
        # Restore the complete table first, then restore package attributes
        # that importlib may have populated with temporary child modules.
        sys.modules.clear()
        sys.modules.update(cached_modules)
        for module, state in package_state.items():
            module.__dict__.clear()
            module.__dict__.update(state)

    return {
        "module": module_name,
        "import_time_seconds": import_time,
        "already_loaded": already_loaded,
    }


def analyse_import_weights(
    root_module: str = "codomyrmex",
) -> list[dict[str, Any]]:
    """Rank sub-modules by import time.

    Parameters
    ----------
    root_module:
        Root module to scan.

    Returns
    -------
    list of dicts sorted by ``import_time_seconds`` descending.
    """
    # Discover all sub-modules currently loaded
    sub_modules = sorted(k for k in sys.modules if k.startswith(f"{root_module}."))

    results: list[dict[str, Any]] = []
    for mod_name in sub_modules:
        result = measure_import_time(mod_name)
        if result["import_time_seconds"] >= 0:
            results.append(result)

    results.sort(key=lambda x: x["import_time_seconds"], reverse=True)
    return results


__all__ = [
    "analyse_import_weights",
    "benchmark_cli_startup",
    "measure_import_time",
]
