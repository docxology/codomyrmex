#!/usr/bin/env python3
"""Concurrency Module - Comprehensive Usage Script.

Demonstrates and tests concurrency primitives with full configurability,
unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --dry-run                # Preview without executing
    python basic_usage.py --verbose                # Verbose output
    python basic_usage.py --output-dir ./results   # Custom output directory
    python basic_usage.py --workers 4              # Custom worker count
    python basic_usage.py --config config.yaml     # Use config file

Environment Variables:
    CONCURRENCY_WORKERS      Number of concurrent workers
    CONCURRENCY_LOCK_TIMEOUT Lock acquisition timeout
"""

import sys
import time
import threading
from pathlib import Path
from typing import Any, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
script_base_path = project_root / "src" / "codomyrmex" / "utils" / "script_base.py"
spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class ConcurrencyScript(ScriptBase):
    """Comprehensive concurrency module demonstration and testing."""

    def __init__(self):
        super().__init__(
            name="concurrency_usage",
            description="Demonstrate and test concurrency primitives",
            version="1.0.0",
        )

    def add_arguments(self, parser):
        """Add concurrency-specific arguments."""
        group = parser.add_argument_group("Concurrency Options")
        group.add_argument(
            "--workers", "-w", type=int, default=4,
            help="Number of concurrent workers (default: 4)"
        )
        group.add_argument(
            "--lock-timeout", type=float, default=5.0,
            help="Lock acquisition timeout in seconds (default: 5.0)"
        )
        group.add_argument(
            "--semaphore-limit", type=int, default=3,
            help="Semaphore concurrent limit (default: 3)"
        )
        group.add_argument(
            "--test-iterations", type=int, default=10,
            help="Number of test iterations per primitive (default: 10)"
        )
        group.add_argument(
            "--skip-redis", action="store_true",
            help="Skip Redis lock tests (if Redis unavailable)"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
        """Execute concurrency demonstrations and tests."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "primitives_tested": [],
            "timing_results": {},
            "errors": [],
        }

        workers = args.workers
        lock_timeout = args.lock_timeout
        semaphore_limit = args.semaphore_limit
        iterations = args.test_iterations

        self.log_info(f"Configuration: workers={workers}, timeout={lock_timeout}s, iterations={iterations}")

        if config.dry_run:
            self.log_info("Would test: LocalLock, LocalSemaphore, LockManager, ReadWriteLock")
            results["dry_run"] = True
            return results

        # Import concurrency module (after dry_run check)

        # Test 1: LocalLock
        self.log_info("\n1. Testing LocalLock - File-based mutex")
        try:
            lock_results = self._test_local_lock(iterations, lock_timeout)
            results["primitives_tested"].append("LocalLock")
            results["timing_results"]["local_lock"] = lock_results
            results["tests_passed"] += 1
            self.log_success(f"LocalLock: {lock_results['acquisitions']} acquisitions, avg {lock_results['avg_time_ms']:.2f}ms")
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"LocalLock: {e}")
            self.log_error(f"LocalLock test failed: {e}")
        results["tests_run"] += 1

        # Test 2: LocalSemaphore
        self.log_info(f"\n2. Testing LocalSemaphore - Counting semaphore (limit={semaphore_limit})")
        try:
            sem_results = self._test_semaphore(semaphore_limit, workers, iterations)
            results["primitives_tested"].append("LocalSemaphore")
            results["timing_results"]["semaphore"] = sem_results
            results["tests_passed"] += 1
            self.log_success(f"LocalSemaphore: max_concurrent={sem_results['max_concurrent']}, operations={sem_results['total_operations']}")
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"LocalSemaphore: {e}")
            self.log_error(f"LocalSemaphore test failed: {e}")
        results["tests_run"] += 1

        # Test 3: LockManager
        self.log_info("\n3. Testing LockManager - Multi-resource coordination")
        try:
            manager_results = self._test_lock_manager(iterations, lock_timeout)
            results["primitives_tested"].append("LockManager")
            results["timing_results"]["lock_manager"] = manager_results
            results["tests_passed"] += 1
            self.log_success(f"LockManager: {manager_results['multi_lock_acquisitions']} multi-lock acquisitions")
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"LockManager: {e}")
            self.log_error(f"LockManager test failed: {e}")
        results["tests_run"] += 1

        # Test 4: ReadWriteLock
        self.log_info("\n4. Testing ReadWriteLock - Reader/writer pattern")
        try:
            rw_results = self._test_read_write_lock(workers, iterations)
            results["primitives_tested"].append("ReadWriteLock")
            results["timing_results"]["read_write_lock"] = rw_results
            results["tests_passed"] += 1
            self.log_success(f"ReadWriteLock: {rw_results['reads']} reads, {rw_results['writes']} writes")
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"ReadWriteLock: {e}")
            self.log_error(f"ReadWriteLock test failed: {e}")
        results["tests_run"] += 1

        # Test 5: Concurrent stress test
        self.log_info(f"\n5. Concurrent stress test ({workers} workers)")
        try:
            stress_results = self._stress_test(workers, iterations)
            results["timing_results"]["stress_test"] = stress_results
            results["tests_passed"] += 1
            self.log_success(f"Stress test: {stress_results['total_operations']} ops in {stress_results['duration_ms']:.2f}ms")
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"Stress test: {e}")
            self.log_error(f"Stress test failed: {e}")
        results["tests_run"] += 1

        # Add metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])
        self.add_metric("success_rate", results["tests_passed"] / results["tests_run"] * 100)

        return results

    def _test_local_lock(self, iterations: int, timeout: float) -> Dict[str, Any]:
        """Test LocalLock acquire/release cycles."""
        from codomyrmex.concurrency import LocalLock

        times = []
        lock = LocalLock("test_basic_lock")

        for i in range(iterations):
            start = time.perf_counter()
            acquired = lock.acquire(timeout=timeout)
            if acquired:
                time.sleep(0.001)  # Simulate work
                lock.release()
                times.append((time.perf_counter() - start) * 1000)
            else:
                raise RuntimeError(f"Failed to acquire lock on iteration {i}")

        return {
            "acquisitions": iterations,
            "avg_time_ms": sum(times) / len(times),
            "max_time_ms": max(times),
            "min_time_ms": min(times),
        }

    def _test_semaphore(self, limit: int, workers: int, iterations: int) -> Dict[str, Any]:
        """Test semaphore with concurrent access."""
        from codomyrmex.concurrency import LocalSemaphore

        semaphore = LocalSemaphore(value=limit)
        concurrent_count = [0]
        max_concurrent = [0]
        lock = threading.Lock()
        total_ops = [0]

        def worker_task():
            for _ in range(iterations):
                if semaphore.acquire(timeout=5.0):
                    with lock:
                        concurrent_count[0] += 1
                        if concurrent_count[0] > max_concurrent[0]:
                            max_concurrent[0] = concurrent_count[0]
                        total_ops[0] += 1

                    time.sleep(0.01)  # Simulate work

                    with lock:
                        concurrent_count[0] -= 1

                    semaphore.release()

        threads = [threading.Thread(target=worker_task) for _ in range(workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return {
            "limit": limit,
            "workers": workers,
            "max_concurrent": max_concurrent[0],
            "total_operations": total_ops[0],
            "within_limit": max_concurrent[0] <= limit,
        }

    def _test_lock_manager(self, iterations: int, timeout: float) -> Dict[str, Any]:
        """Test LockManager multi-resource acquisition."""
        from codomyrmex.concurrency import LockManager, LocalLock

        manager = LockManager()
        resources = ["resource_a", "resource_b", "resource_c"]

        for name in resources:
            manager.register_lock(name, LocalLock(name))

        multi_acquisitions = 0
        for _ in range(iterations):
            if manager.acquire_all(resources, timeout=timeout):
                multi_acquisitions += 1
                time.sleep(0.001)
                manager.release_all(resources)

        stats = manager.stats

        return {
            "resources": len(resources),
            "multi_lock_acquisitions": multi_acquisitions,
            "total_acquisitions": stats.total_acquisitions,
            "total_releases": stats.total_releases,
        }

    def _test_read_write_lock(self, workers: int, iterations: int) -> Dict[str, Any]:
        """Test ReadWriteLock with concurrent readers and writers."""
        from codomyrmex.concurrency import ReadWriteLock

        rw_lock = ReadWriteLock()
        shared_data = {"value": 0}
        reads = [0]
        writes = [0]
        lock = threading.Lock()

        def reader():
            for _ in range(iterations):
                rw_lock.acquire_read()
                _ = shared_data["value"]  # Read
                with lock:
                    reads[0] += 1
                time.sleep(0.001)
                rw_lock.release_read()

        def writer():
            for _ in range(iterations // 2):
                rw_lock.acquire_write()
                shared_data["value"] += 1  # Write
                with lock:
                    writes[0] += 1
                time.sleep(0.002)
                rw_lock.release_write()

        threads = []
        for i in range(workers):
            if i % 3 == 0:
                threads.append(threading.Thread(target=writer))
            else:
                threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return {
            "workers": workers,
            "reads": reads[0],
            "writes": writes[0],
            "final_value": shared_data["value"],
        }

    def _stress_test(self, workers: int, iterations: int) -> Dict[str, Any]:
        """Stress test with mixed concurrent operations."""
        from codomyrmex.concurrency import LocalLock, LocalSemaphore

        lock = LocalLock("stress_lock")
        semaphore = LocalSemaphore(value=workers // 2)
        counter = [0]
        counter_lock = threading.Lock()

        start_time = time.perf_counter()

        def stress_worker(worker_id: int):
            ops = 0
            for i in range(iterations):
                # Alternate between lock and semaphore
                if i % 2 == 0:
                    if lock.acquire(timeout=1.0):
                        with counter_lock:
                            counter[0] += 1
                        lock.release()
                        ops += 1
                else:
                    if semaphore.acquire(timeout=1.0):
                        with counter_lock:
                            counter[0] += 1
                        semaphore.release()
                        ops += 1
            return ops

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(stress_worker, i) for i in range(workers)]
            results = [f.result() for f in as_completed(futures)]

        duration = (time.perf_counter() - start_time) * 1000

        return {
            "workers": workers,
            "iterations_per_worker": iterations,
            "total_operations": counter[0],
            "expected_operations": workers * iterations,
            "duration_ms": duration,
            "ops_per_second": counter[0] / (duration / 1000),
        }


if __name__ == "__main__":
    script = ConcurrencyScript()
    sys.exit(script.execute())
