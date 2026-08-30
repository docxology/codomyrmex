"""Persistence and Concurrency Study Harness for Colony Kernel (R5).

Executes concurrent multi-worker load simulations, evaluates crash recovery
under injected failures, and audits transactional WAL durability.
"""

from __future__ import annotations

import concurrent.futures
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codomyrmex.colony_kernel.models import (
    ColonySignal,
    DecayRate,
    SignalSource,
    SignalType,
)
from codomyrmex.colony_kernel.research.persistent_store import PersistentPheromoneStore


@dataclass(frozen=True)
class ConcurrencyAuditReport:
    """Diagnostic report from a concurrent multi-worker test run."""

    num_workers: int
    operations_per_worker: int
    total_operations: int
    successful_operations: int
    failed_operations: int
    elapsed_seconds: float
    throughput_ops_per_sec: float
    final_marker_count: int
    data_consistent: bool
    error_summary: dict[str, int]


@dataclass(frozen=True)
class CrashRecoveryReport:
    """Diagnostic report from crash injection & recovery testing."""

    injection_point: str
    crash_induced: bool
    recovered_cleanly: bool
    surviving_marker_count: int
    integrity_check_passed: bool


class PersistenceConcurrencyStudy:
    """Harness for stress-testing SQLite WAL persistence and concurrent writers."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def run_concurrent_load_test(
        self,
        *,
        num_workers: int = 4,
        operations_per_worker: int = 25,
    ) -> ConcurrencyAuditReport:
        """Run concurrent multi-threaded writes against PersistentPheromoneStore."""
        if num_workers < 1:
            raise ValueError("num_workers must be at least 1")
        if operations_per_worker < 1:
            raise ValueError("operations_per_worker must be at least 1")

        errors: dict[str, int] = {}
        successes = 0
        failures = 0
        lock = threading.Lock()

        # Establish the schema before workers race to open independent connections.
        initial_store = PersistentPheromoneStore(self.db_path)
        initial_store.close()

        def worker_task(worker_id: int) -> None:
            nonlocal successes, failures
            store: PersistentPheromoneStore | None = None
            completed = 0
            try:
                # Each worker uses its own connection against the same file.
                store = PersistentPheromoneStore(self.db_path)
                for i in range(operations_per_worker):
                    sig = ColonySignal(
                        signal_type=SignalType.NEED,
                        source=SignalSource.AGENT,
                        location=f"module_w{worker_id}_loc{i % 5}",
                        strength=1.0,
                        decay_rate=DecayRate.NORMAL,
                        evidence={"worker": worker_id, "op": i},
                    )
                    store.deposit_signal(sig)
                    with lock:
                        successes += 1
                    completed += 1
            except Exception as exc:
                err_name = type(exc).__name__
                with lock:
                    abandoned = operations_per_worker - completed
                    failures += abandoned
                    errors[err_name] = errors.get(err_name, 0) + abandoned
            finally:
                if store is not None:
                    store.close()

        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(worker_task, w_id) for w_id in range(num_workers)
            ]
            for future in concurrent.futures.as_completed(futures):
                future.result()

        elapsed = time.perf_counter() - start_time
        total_ops = num_workers * operations_per_worker

        # Verify DB integrity and marker consistency
        verif_store = PersistentPheromoneStore(self.db_path)
        signals = verif_store.top_pressure(k=1000)
        marker_cnt = len(signals)
        verif_store.close()

        # Check raw SQLite integrity
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("PRAGMA integrity_check")
        row = cursor.fetchone()
        consistent = row is not None and row[0] == "ok" and failures == 0
        conn.close()

        return ConcurrencyAuditReport(
            num_workers=num_workers,
            operations_per_worker=operations_per_worker,
            total_operations=total_ops,
            successful_operations=successes,
            failed_operations=failures,
            elapsed_seconds=elapsed,
            throughput_ops_per_sec=successes / elapsed if elapsed > 0 else 0.0,
            final_marker_count=marker_cnt,
            data_consistent=consistent,
            error_summary=errors,
        )

    def test_crash_injection(
        self,
        injection_point: str = "before_commit",
    ) -> CrashRecoveryReport:
        """Inject failure at specified transaction boundary and verify recovery."""
        crashed = False

        def injector(phase: str) -> None:
            nonlocal crashed
            if phase == injection_point:
                crashed = True
                raise RuntimeError(f"Simulated crash at {phase}")

        store = PersistentPheromoneStore(self.db_path, failure_injector=injector)
        try:
            sig = ColonySignal(
                signal_type=SignalType.RISK,
                source=SignalSource.SECURITY,
                location="critical/module",
                strength=2.0,
                decay_rate=DecayRate.FAST,
            )
            store.deposit_signal(sig)
        except RuntimeError:
            pass  # Expected crash
        finally:
            store.close()

        # Reopen fresh and check recovery
        recovered_store = PersistentPheromoneStore(self.db_path)
        signals = recovered_store.top_pressure(k=100)
        marker_cnt = len(signals)
        recovered_store.close()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("PRAGMA integrity_check")
        row = cursor.fetchone()
        integrity_ok = row is not None and row[0] == "ok"
        conn.close()

        return CrashRecoveryReport(
            injection_point=injection_point,
            crash_induced=crashed,
            recovered_cleanly=integrity_ok,
            surviving_marker_count=marker_cnt,
            integrity_check_passed=integrity_ok,
        )
