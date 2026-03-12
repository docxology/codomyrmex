"""Flaky test quarantine system.

Detects tests that fail intermittently and auto-quarantines them
so they don't block the main CI pipeline.

Example::

    quarantine = FlakyTestQuarantine()
    quarantine.record_run("test_network_timeout", passed=False)
    quarantine.record_run("test_network_timeout", passed=True)
    quarantine.record_run("test_network_timeout", passed=False)
    assert quarantine.is_flaky("test_network_timeout")
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TestRunResult:
    """A single test run outcome.

    Attributes:
        test_id: Fully qualified test name (e.g., ``test_module::test_func``).
        passed: Whether the test passed.
        timestamp: Unix timestamp of the run.
        duration_ms: Test duration in milliseconds.
    """

    test_id: str
    passed: bool
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0


@dataclass
class QuarantineEntry:
    """A quarantined test entry.

    Attributes:
        test_id: Fully qualified test name.
        reason: Why the test was quarantined.
        fail_rate: Failure rate over recent runs (0.0–1.0).
        total_runs: Total runs analyzed.
        quarantined_at: When the quarantine was applied.
    """

    test_id: str
    reason: str
    fail_rate: float
    total_runs: int
    quarantined_at: float = field(default_factory=time.time)


class FlakyTestQuarantine:
    """Detect and quarantine flaky tests.

    A test is considered flaky if it fails more than ``fail_threshold``
    times within the last ``window_size`` runs but also passes at least once.

    Args:
        window_size: Number of recent runs to analyze.
        fail_threshold: Minimum failures within window to flag as flaky.

    Example::

        quarantine = FlakyTestQuarantine()
        for _ in range(5):
            quarantine.record_run("test_x", passed=True)
        quarantine.record_run("test_x", passed=False)
        quarantine.record_run("test_x", passed=False)
        print(quarantine.is_flaky("test_x"))  # True
    """

    def __init__(
        self,
        window_size: int = 10,
        fail_threshold: int = 2,
    ) -> None:
        self._window_size = window_size
        self._fail_threshold = fail_threshold
        self._runs: dict[str, list[TestRunResult]] = defaultdict(list)
        self._quarantined: dict[str, QuarantineEntry] = {}

    def record_run(
        self,
        test_id: str,
        passed: bool,
        duration_ms: float = 0.0,
    ) -> None:
        """Record a test run result.

        Args:
            test_id: Fully qualified test name.
            passed: Whether the test passed.
            duration_ms: Test duration.
        """
        self._runs[test_id].append(TestRunResult(
            test_id=test_id,
            passed=passed,
            duration_ms=duration_ms,
        ))
        # Keep only the last window_size runs
        if len(self._runs[test_id]) > self._window_size:
            self._runs[test_id] = self._runs[test_id][-self._window_size:]

        # Auto-detect flakiness
        self._check_flaky(test_id)

    def _check_flaky(self, test_id: str) -> None:
        """Check if a test has become flaky and quarantine it."""
        runs = self._runs[test_id]
        if len(runs) < self._fail_threshold:
            return

        recent = runs[-self._window_size:]
        failures = sum(1 for r in recent if not r.passed)
        passes = sum(1 for r in recent if r.passed)

        # Flaky = fails sometimes AND passes sometimes
        if failures >= self._fail_threshold and passes > 0:
            fail_rate = failures / len(recent)
            if test_id not in self._quarantined:
                self._quarantined[test_id] = QuarantineEntry(
                    test_id=test_id,
                    reason=f"Failed {failures}/{len(recent)} recent runs (threshold: {self._fail_threshold})",
                    fail_rate=fail_rate,
                    total_runs=len(recent),
                )
                logger.warning("Quarantined flaky test: %s (%.0f%% fail rate)", test_id, fail_rate * 100)

    def is_flaky(self, test_id: str) -> bool:
        """Check if a test is quarantined as flaky."""
        return test_id in self._quarantined

    def get_quarantined(self) -> list[QuarantineEntry]:
        """Get all quarantined tests."""
        return list(self._quarantined.values())

    def release(self, test_id: str) -> bool:
        """Remove a test from quarantine.

        Returns:
            ``True`` if the test was quarantined.
        """
        return self._quarantined.pop(test_id, None) is not None

    def get_summary(self) -> dict[str, Any]:
        """Return a summary of quarantine state.

        Returns:
            Dict with ``total_tracked``, ``quarantined_count``, ``quarantined_tests``.
        """
        return {
            "total_tracked": len(self._runs),
            "quarantined_count": len(self._quarantined),
            "quarantined_tests": [e.test_id for e in self._quarantined.values()],
        }

    def generate_pytest_markers(self) -> str:
        """Generate pytest markers for quarantined tests.

        Returns:
            Python code string with ``@pytest.mark.flaky`` decorators.
        """
        if not self._quarantined:
            return "# No flaky tests quarantined\n"

        lines = ["import pytest\n\n# Auto-generated flaky test markers\n"]
        for entry in sorted(self._quarantined.values(), key=lambda e: e.test_id):
            lines.append(f"# {entry.reason}")
            lines.append(f'# Quarantined at: {time.strftime("%Y-%m-%d %H:%M", time.localtime(entry.quarantined_at))}')
            lines.append(f"pytest.mark.flaky(reruns=3)  # {entry.test_id}\n")
        return "\n".join(lines)


__all__ = [
    "FlakyTestQuarantine",
    "QuarantineEntry",
    "TestRunResult",
]
