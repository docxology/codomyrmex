"""Parallel Script Runner.

Provides concurrent execution of scripts with streaming output and resource management.

This module enables:
- Parallel execution of multiple scripts with configurable concurrency
- Streaming output for real-time progress monitoring
- Resource-aware execution based on CPU/memory
- Batch execution with dependency awareness
"""

import asyncio
import concurrent.futures
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .runner import run_script

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of a parallel execution batch."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    timeout: int = 0
    skipped: int = 0
    execution_time: float = 0.0
    results: list[dict[str, Any]] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if all scripts passed."""
        return self.failed == 0 and self.timeout == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "timeout": self.timeout,
            "skipped": self.skipped,
            "execution_time": self.execution_time,
            "success": self.success,
        }


ProgressCallback = Callable[[str, str, dict[str, Any]], None]


class ParallelRunner:
    """Run multiple scripts in parallel with resource management."""

    def __init__(
        self,
        max_workers: int | None = None,
        progress_callback: ProgressCallback | None = None,
        default_timeout: int = 60,
        fail_fast: bool = False
    ):
        """Initialize parallel runner.

        Args:
            max_workers: Maximum concurrent workers (defaults to CPU count)
            progress_callback: Callback for progress updates
            default_timeout: Default timeout per script in seconds
            fail_fast: Stop on first failure if True
        """
        self.max_workers = max_workers or min(os.cpu_count() or 1, 8)
        self.progress_callback = progress_callback
        self.default_timeout = default_timeout
        self.fail_fast = fail_fast
        self._cancelled = False
        self._executor: concurrent.futures.ProcessPoolExecutor | None = None

    def _emit_progress(self, script: str, status: str, details: dict[str, Any] = None):
        """Emit progress update."""
        if self.progress_callback:
            try:
                self.progress_callback(script, status, details or {})
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                logger.warning(f"Progress callback error: {e}")

    def run_scripts(
        self,
        scripts: list[Path],
        timeout: int | None = None,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        configs: dict[str, dict[str, Any]] | None = None
    ) -> ExecutionResult:
        """Run scripts in parallel.

        Args:
            scripts: List of script paths
            timeout: Timeout per script (overrides default)
            cwd: Working directory
            env: Environment variables
            configs: Per-script configurations keyed by script name

        Returns:
            ExecutionResult with aggregated results
        """
        if not scripts:
            return ExecutionResult()

        timeout = timeout or self.default_timeout
        configs = configs or {}
        self._cancelled = False

        result = ExecutionResult(total=len(scripts))
        start_time = time.time()

        self._emit_progress("batch", "started", {"total": len(scripts), "workers": self.max_workers})

        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            self._executor = executor
            futures = {}

            for script in scripts:
                if self._cancelled:
                    result.skipped += 1
                    continue

                config = configs.get(script.name, {})
                future = executor.submit(
                    run_script,
                    script,
                    timeout=timeout,
                    env=env,
                    cwd=cwd,
                    config=config
                )
                futures[future] = script
                self._emit_progress(script.name, "submitted", {})

            for future in concurrent.futures.as_completed(futures):
                if self._cancelled:
                    break

                script = futures[future]
                try:
                    script_result = future.result()
                    result.results.append(script_result)

                    status = script_result.get("status", "unknown")
                    if status == "passed":
                        result.passed += 1
                    elif status == "failed":
                        result.failed += 1
                        if self.fail_fast:
                            self._cancelled = True
                    elif status == "timeout":
                        result.timeout += 1
                    else:
                        result.failed += 1

                    self._emit_progress(script.name, status, {
                        "execution_time": script_result.get("execution_time", 0)
                    })

                except concurrent.futures.CancelledError:
                    result.skipped += 1
                    self._emit_progress(script.name, "cancelled", {})
                except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                    result.failed += 1
                    result.results.append({
                        "script": str(script),
                        "name": script.name,
                        "status": "error",
                        "error": str(e)
                    })
                    self._emit_progress(script.name, "error", {"error": str(e)})

            self._executor = None

        result.execution_time = time.time() - start_time
        self._emit_progress("batch", "completed", result.to_dict())

        return result

    async def run_scripts_async(
        self,
        scripts: list[Path],
        timeout: int | None = None,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        configs: dict[str, dict[str, Any]] | None = None
    ) -> ExecutionResult:
        """Run scripts in parallel asynchronously.

        Args:
            scripts: List of script paths
            timeout: Timeout per script
            cwd: Working directory
            env: Environment variables
            configs: Per-script configurations

        Returns:
            ExecutionResult with aggregated results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.run_scripts(scripts, timeout, cwd, env, configs)
        )

    def cancel(self):
        """Cancel running execution."""
        self._cancelled = True
        if self._executor:
            self._executor.shutdown(wait=False, cancel_futures=True)


class BatchRunner:
    """Run scripts in batches with dependencies."""

    def __init__(
        self,
        max_workers: int | None = None,
        progress_callback: ProgressCallback | None = None
    ):
        """Initialize batch runner.

        Args:
            max_workers: Maximum concurrent workers per batch
            progress_callback: Callback for progress updates
        """
        self.parallel_runner = ParallelRunner(
            max_workers=max_workers,
            progress_callback=progress_callback
        )

    def run_batches(
        self,
        batches: list[list[Path]],
        timeout: int = 60,
        cwd: Path | None = None,
        stop_on_batch_failure: bool = True
    ) -> list[ExecutionResult]:
        """Run batches sequentially, scripts within batches in parallel.

        Args:
            batches: List of script batches
            timeout: Timeout per script
            cwd: Working directory
            stop_on_batch_failure: Stop if any batch has failures

        Returns:
            List of ExecutionResult per batch
        """
        results = []

        for i, batch in enumerate(batches):
            logger.info(f"Running batch {i + 1}/{len(batches)} ({len(batch)} scripts)")

            result = self.parallel_runner.run_scripts(
                scripts=batch,
                timeout=timeout,
                cwd=cwd
            )
            results.append(result)

            if stop_on_batch_failure and not result.success:
                logger.warning(f"Batch {i + 1} failed, stopping")
                break

        return results


def run_parallel(
    scripts: list[Path],
    max_workers: int | None = None,
    timeout: int = 60,
    progress_callback: ProgressCallback | None = None
) -> ExecutionResult:
    """Convenience function to run scripts in parallel.

    Args:
        scripts: List of script paths
        max_workers: Maximum concurrent workers
        timeout: Timeout per script
        progress_callback: Progress callback

    Returns:
        ExecutionResult
    """
    runner = ParallelRunner(
        max_workers=max_workers,
        progress_callback=progress_callback,
        default_timeout=timeout
    )
    return runner.run_scripts(scripts)


async def run_parallel_async(
    scripts: list[Path],
    max_workers: int | None = None,
    timeout: int = 60,
    progress_callback: ProgressCallback | None = None
) -> ExecutionResult:
    """Async convenience function to run scripts in parallel.

    Args:
        scripts: List of script paths
        max_workers: Maximum concurrent workers
        timeout: Timeout per script
        progress_callback: Progress callback

    Returns:
        ExecutionResult
    """
    runner = ParallelRunner(
        max_workers=max_workers,
        progress_callback=progress_callback,
        default_timeout=timeout
    )
    return await runner.run_scripts_async(scripts)
