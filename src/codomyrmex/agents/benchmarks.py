"""Agent performance benchmarking harness.

Provides tools for systematically benchmarking agent execution
across tasks, measuring latency, accuracy, and resource usage.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class BenchmarkResult:
    """Result from a single benchmark run."""
    task_name: str
    agent_name: str
    duration_seconds: float
    success: bool
    output: Any = None
    error: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "task_name": self.task_name,
            "agent_name": self.agent_name,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error": self.error,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
        }


@dataclass
class BenchmarkSuite:
    """A collection of benchmark tasks."""
    name: str
    tasks: list[BenchmarkTask] = field(default_factory=list)

    def add_task(self, name: str, func: Callable, expected: Any = None,
                 timeout: float = 60.0) -> None:
        """Execute Add Task operations natively."""
        self.tasks.append(BenchmarkTask(name=name, func=func,
                                         expected=expected, timeout=timeout))


@dataclass
class BenchmarkTask:
    """A single benchmark task definition."""
    name: str
    func: Callable
    expected: Any = None
    timeout: float = 60.0


class AgentBenchmarker:
    """Harness for benchmarking agent performance.

    Runs agents through benchmark suites and collects performance
    metrics for comparison and regression detection.
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        """Execute   Init   operations natively."""
        self._output_dir = output_dir
        self._results: list[BenchmarkResult] = []

    def run_task(self, task: BenchmarkTask, agent_name: str,
                 agent_func: Callable) -> BenchmarkResult:
        """Run a single benchmark task against an agent."""
        start = time.monotonic()
        try:
            output = agent_func(task.func)
            duration = time.monotonic() - start
            success = True
            if task.expected is not None:
                success = output == task.expected
            result = BenchmarkResult(
                task_name=task.name,
                agent_name=agent_name,
                duration_seconds=duration,
                success=success,
                output=output,
                metrics={"latency_ms": duration * 1000},
            )
        except Exception as e:
            duration = time.monotonic() - start
            result = BenchmarkResult(
                task_name=task.name,
                agent_name=agent_name,
                duration_seconds=duration,
                success=False,
                error=str(e),
                metrics={"latency_ms": duration * 1000},
            )
        self._results.append(result)
        return result

    def run_suite(self, suite: BenchmarkSuite, agent_name: str,
                  agent_func: Callable) -> list[BenchmarkResult]:
        """Run all tasks in a suite against an agent."""
        return [self.run_task(task, agent_name, agent_func) for task in suite.tasks]

    def compare_agents(self, agent_results: dict[str, list[BenchmarkResult]]) -> dict[str, Any]:
        """Compare benchmark results across agents."""
        comparison: dict[str, Any] = {}
        for agent_name, results in agent_results.items():
            durations = [r.duration_seconds for r in results]
            successes = sum(1 for r in results if r.success)
            comparison[agent_name] = {
                "total_tasks": len(results),
                "successes": successes,
                "success_rate": successes / len(results) if results else 0,
                "avg_duration": sum(durations) / len(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
            }
        return comparison

    def save_results(self, path: Path | None = None) -> Path:
        """Save all benchmark results to JSON."""
        output = path or (self._output_dir or Path(".")) / "benchmark_results.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            json.dump([r.to_dict() for r in self._results], f, indent=2)
        return output

    @property
    def results(self) -> list[BenchmarkResult]:
        """Execute Results operations natively."""
        return list(self._results)
