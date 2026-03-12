"""Performance profiler CLI integration.

Provides profiling utilities that can be invoked from the CLI
to benchmark module operations, measure startup times, and
generate performance baselines.

Example::

    profiler = CLIProfiler()
    result = profiler.profile_import("codomyrmex.agents")
    print(f"Import time: {result['duration_ms']:.1f}ms")
"""

from __future__ import annotations

import importlib
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


@dataclass
class ProfileResult:
    """Result of a profiling operation.

    Attributes:
        name: Name of profiled operation.
        duration_ms: Duration in milliseconds.
        success: Whether the operation succeeded.
        details: Additional profiling data.
    """

    name: str
    duration_ms: float = 0.0
    success: bool = True
    details: dict[str, Any] = field(default_factory=dict)


class CLIProfiler:
    """Performance profiler for CLI and module operations.

    Example::

        profiler = CLIProfiler()
        results = profiler.profile_all_imports()
        for r in results[:5]:
            print(f"  {r.name}: {r.duration_ms:.1f}ms")
    """

    def profile_import(self, module_name: str) -> ProfileResult:
        """Profile the import time of a module.

        Args:
            module_name: Fully qualified module name.

        Returns:
            :class:`ProfileResult` with import timing.
        """
        # Remove from cache if present
        was_cached = module_name in sys.modules
        if was_cached:
            cached_mod = sys.modules.pop(module_name, None)

        start = time.monotonic()
        try:
            importlib.import_module(module_name)
            elapsed = (time.monotonic() - start) * 1000
            return ProfileResult(
                name=module_name,
                duration_ms=round(elapsed, 2),
                details={"was_cached": was_cached},
            )
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return ProfileResult(
                name=module_name,
                duration_ms=round(elapsed, 2),
                success=False,
                details={"error": str(e)},
            )
        finally:
            # Restore cached module
            if was_cached and cached_mod is not None:
                sys.modules[module_name] = cached_mod

    def profile_function(
        self,
        func: Callable[..., Any],
        *args: Any,
        iterations: int = 1,
        **kwargs: Any,
    ) -> ProfileResult:
        """Profile a function's execution time.

        Args:
            func: Function to profile.
            *args: Positional arguments.
            iterations: Number of iterations to average.
            **kwargs: Keyword arguments.

        Returns:
            :class:`ProfileResult` with timing stats.
        """
        durations: list[float] = []

        for _ in range(iterations):
            start = time.monotonic()
            try:
                func(*args, **kwargs)
            except Exception:
                pass
            durations.append((time.monotonic() - start) * 1000)

        avg = sum(durations) / len(durations) if durations else 0.0
        return ProfileResult(
            name=func.__name__,
            duration_ms=round(avg, 2),
            details={
                "iterations": iterations,
                "min_ms": round(min(durations), 2) if durations else 0,
                "max_ms": round(max(durations), 2) if durations else 0,
                "total_ms": round(sum(durations), 2),
            },
        )

    def profile_all_imports(self, package: str = "codomyrmex") -> list[ProfileResult]:
        """Profile import times for all submodules of a package.

        Args:
            package: Package name to scan.

        Returns:
            List of :class:`ProfileResult` sorted by duration (slowest first).
        """
        src_root = Path(__file__).resolve().parents[1]
        results: list[ProfileResult] = []

        for mod_dir in sorted(src_root.iterdir()):
            if not mod_dir.is_dir() or mod_dir.name.startswith(("_", ".")) or mod_dir.name == "tests":
                continue

            module_name = f"{package}.{mod_dir.name}"
            result = self.profile_import(module_name)
            results.append(result)

        return sorted(results, key=lambda r: r.duration_ms, reverse=True)

    def benchmark_startup(self) -> ProfileResult:
        """Benchmark the full CLI startup time.

        Returns:
            :class:`ProfileResult` with CLI import chain timing.
        """
        modules_to_load = [
            "codomyrmex",
            "codomyrmex.cli",
            "codomyrmex.cli.core",
            "codomyrmex.logging_monitoring",
        ]

        total_ms = 0.0
        details: dict[str, float] = {}

        for mod in modules_to_load:
            result = self.profile_import(mod)
            total_ms += result.duration_ms
            details[mod] = result.duration_ms

        return ProfileResult(
            name="cli_startup",
            duration_ms=round(total_ms, 2),
            details=details,
        )


__all__ = [
    "CLIProfiler",
    "ProfileResult",
]
