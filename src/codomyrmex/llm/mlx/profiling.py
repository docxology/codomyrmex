"""Portable configuration profiling, explicitly separate from MLX inference."""

from __future__ import annotations

import cProfile
import hashlib
import importlib.metadata
import os
import platform
import pstats
import statistics
import sys
import time
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .config import MLXConfig

logger = get_logger(__name__)
PROFILE_SCHEMA = "codomyrmex.mlx.configuration-profile.v1"
SCENARIOS = (
    ("unbounded", {}),
    ("bounded_4096", {"max_kv_size": 4096}),
    ("quantized_4bit", {"kv_bits": 4}),
    ("quantized_8bit", {"kv_bits": 8}),
)


def _configuration(options: dict[str, Any]) -> MLXConfig:
    """Use explicit non-sensitive settings independent of user model selection."""
    return MLXConfig(
        model="profile/no-model-loaded",
        temperature=0.7,
        max_tokens=128,
        top_p=0.9,
        repetition_penalty=1.1,
        cache_dir="profile/no-cache-written",
        seed=0,
        kv_group_size=64,
        quantized_kv_start=0,
        **options,
    )


def _exercise(options: dict[str, Any], iterations: int) -> None:
    """Exercise actual construction, serialization, validation, and forwarding."""
    for _ in range(iterations):
        config = _configuration(options)
        config.to_dict()
        config.get_generation_kwargs()


def _hotspots(profiler: cProfile.Profile) -> list[dict[str, Any]]:
    """Return cumulative CPU hotspots without retaining absolute local paths."""
    stats = pstats.Stats(profiler)
    return [
        {
            "file": Path(filename).name,
            "line": line,
            "function": function,
            "primitive_calls": values[0],
            "total_calls": values[1],
            "self_seconds": values[2],
            "cumulative_seconds": values[3],
        }
        for (filename, line, function), values in sorted(
            stats.stats.items(),
            key=lambda entry: entry[1][3],
            reverse=True,
        )[:30]
    ]


def profile_cache_configuration(
    iterations: int = 2000,
    repeats: int = 7,
    source_revision: str | None = None,
    source_dirty: bool | None = None,
) -> dict[str, Any]:
    """Measure Python configuration overhead, not inference or Metal memory.

    Uninstrumented timing samples are collected separately from cProfile and
    tracemalloc passes. Exceptions propagate: failed workloads are not timings.
    Caller-owned tracing and ambient automatic-cache overrides are rejected.
    """
    if type(iterations) is not int or not 1 <= iterations <= 1_000_000:
        raise ValueError("iterations must be an integer in [1, 1000000]")
    if type(repeats) is not int or not 3 <= repeats <= 100:
        raise ValueError("repeats must be an integer in [3, 100]")
    ambient = [
        key
        for key in ("MLX_MAX_KV_SIZE", "MLX_KV_BITS", "MLX_PREFILL_STEP_SIZE")
        if key in os.environ
    ]
    if ambient:
        raise ValueError(
            "unset automatic-cache environment overrides before profiling: "
            + ", ".join(ambient)
        )
    if tracemalloc.is_tracing():
        raise RuntimeError(
            "profiling requires ownership of tracemalloc; tracing is already active"
        )
    monitoring = getattr(sys, "monitoring", None)
    if sys.getprofile() is not None or (
        monitoring is not None
        and monitoring.get_tool(monitoring.PROFILER_ID) is not None
    ):
        raise RuntimeError("profiling requires ownership of the CPU profiler")
    if sys.gettrace() is not None or (
        monitoring is not None
        and any(monitoring.get_tool(tool_id) is not None for tool_id in range(6))
    ):
        raise RuntimeError("uninstrumented timing requires no active tracing tools")
    samples: dict[str, list[float]] = {name: [] for name, _ in SCENARIOS}
    for _, options in SCENARIOS:
        _exercise(options, min(iterations, 100))
    for repetition in range(repeats):
        start = repetition % len(SCENARIOS)
        for name, options in SCENARIOS[start:] + SCENARIOS[:start]:
            started = time.perf_counter_ns()
            _exercise(options, iterations)
            samples[name].append((time.perf_counter_ns() - started) / iterations)
    results = []
    for name, options in SCENARIOS:
        with cProfile.Profile() as profiler:
            _exercise(options, iterations)
        tracemalloc.start()
        try:
            _exercise(options, iterations)
            retained, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        median = statistics.median(samples[name])
        results.append(
            {
                "name": name,
                "configuration": _configuration(options).to_dict(),
                "cache_kwargs": _configuration(options).get_cache_kwargs(),
                "timing_ns_per_operation": samples[name],
                "median_ns_per_operation": median,
                "mad_ns_per_operation": statistics.median(
                    abs(value - median) for value in samples[name]
                ),
                "python_retained_bytes": retained,
                "python_peak_bytes": peak,
                "hotspots": _hotspots(profiler),
            }
        )
        logger.info(
            "Profiled MLX configuration %s: median %.3f us/op", name, median / 1000
        )
    dependencies = {}
    for package in (
        "aiohttp",
        "jsonschema",
        "pydantic",
        "python-dotenv",
        "pyyaml",
        "requests",
        "rich",
    ):
        try:
            dependencies[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            dependencies[package] = None
    return {
        "schema": PROFILE_SCHEMA,
        "created_at": datetime.now(UTC).isoformat(),
        "scope": "Python MLXConfig construction, serialization, validation, and kwargs only",
        "native_inference": "not_run",
        "metal_memory": "not_measured",
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "python_build": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "dependencies": dependencies,
            "clock_resolution_seconds": time.get_clock_info("perf_counter").resolution,
        },
        "provenance": {
            "source_revision": source_revision,
            "source_dirty": source_dirty,
            "source_sha256": {
                filename: hashlib.sha256(
                    Path(__file__).with_name(filename).read_bytes()
                ).hexdigest()
                for filename in ("config.py", "profiling.py", "profile_report.py")
            },
        },
        "method": {
            "iterations": iterations,
            "repeats": repeats,
            "warmup_operations": min(iterations, 100),
            "timing_order": "cyclic rotation per repeat",
            "instrumentation": "separate timing, cProfile, and tracemalloc passes",
            "uncertainty": "median absolute deviation; not a confidence interval",
        },
        "scenarios": results,
    }
