"""CLI startup benchmark.

Measures the wall-clock time to run ``codomyrmex --help`` and analyses
heaviest imports via ``importlib`` hooks.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import time
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

    # Remove from cache if already loaded to measure cold import
    cached_module = sys.modules.pop(module_name, None)
    # Also remove child modules
    children_to_remove = [
        k for k in sys.modules if k.startswith(f"{module_name}.")
    ]
    cached_children = {k: sys.modules.pop(k) for k in children_to_remove}

    try:
        t0 = time.perf_counter()
        importlib.import_module(module_name)
        t1 = time.perf_counter()
        import_time = t1 - t0
    except ImportError:
        import_time = -1.0
    finally:
        # Restore cached module
        if cached_module is not None:
            sys.modules[module_name] = cached_module
        for k, v in cached_children.items():
            sys.modules[k] = v

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
    sub_modules = sorted(
        k for k in sys.modules
        if k.startswith(f"{root_module}.")
    )

    results: list[dict[str, Any]] = []
    for mod_name in sub_modules:
        result = measure_import_time(mod_name)
        if result["import_time_seconds"] >= 0:
            results.append(result)

    results.sort(key=lambda x: x["import_time_seconds"], reverse=True)
    return results


__all__ = [
    "benchmark_cli_startup",
    "measure_import_time",
    "analyse_import_weights",
]
