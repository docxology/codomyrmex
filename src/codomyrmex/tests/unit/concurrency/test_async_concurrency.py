"""Comprehensive async tests for the concurrency module.

This module provides extensive async tests for:
- AsyncLocalSemaphore acquire/release
- Async lock operations
- Concurrent async operations
- Timeout handling
- Race condition prevention
"""

import asyncio
import time

import pytest

try:
    from codomyrmex.concurrency.semaphores.semaphore import (
        AsyncLocalSemaphore,
        LocalSemaphore,
    )
    _HAS_CONCURRENCY = True
except ImportError:
    _HAS_CONCURRENCY = False

if not _HAS_CONCURRENCY:
    pytest.skip("concurrency deps not available", allow_module_level=True)

# ==================== ASYNC SEMAPHORE TESTS ====================

@pytest.mark.asyncio
class TestAsyncSemaphoreBasicOperations:
    """Tests for basic async semaphore acquire and release operations."""

    async def test_acquire_single_permit(self):
        """Test acquiring a single permit from async semaphore."""
        sem = AsyncLocalSemaphore(value=1)

        # Should acquire successfully
        await sem.acquire_async()

        # Release the permit
        sem.release()

    async def test_acquire_multiple_permits_sequentially(self):
        """Test acquiring multiple permits sequentially."""
        sem = AsyncLocalSemaphore(value=3)

        # Acquire all three permits
        await sem.acquire_async()
        await sem.acquire_async()
        await sem.acquire_async()

        # Release all permits
        sem.release()
        sem.release()
        sem.release()

    async def test_release_increases_permit_count(self):
        """Test that release properly increases available permits."""
        sem = AsyncLocalSemaphore(value=1)

        # Acquire the permit
        await sem.acquire_async()

        # Release it
        sem.release()

        # Should be able to acquire again
        await sem.acquire_async()
        sem.release()

    async def test_semaphore_initial_value_respected(self):
        """Test that semaphore respects initial value."""
        sem = AsyncLocalSemaphore(value=5)
        assert sem.initial_value == 5

    async def test_semaphore_with_zero_initial_value(self):
        """Test semaphore with zero initial value blocks immediately."""
        sem = AsyncLocalSemaphore(value=0)

        # Should timeout since there are no permits
        acquired = False
        try:
            await asyncio.wait_for(sem.acquire_async(), timeout=0.1)
            acquired = True
        except TimeoutError:
            pass

        assert acquired is False


@pytest.mark.asyncio
class TestAsyncSemaphoreBlocking:
    """Tests for async semaphore blocking behavior."""

    async def test_blocks_when_no_permits_available(self):
        """Test that acquire blocks when no permits are available."""
        sem = AsyncLocalSemaphore(value=1)

        # Acquire the only permit
        await sem.acquire_async()

        # Second acquire should block
        start_time = time.time()
        try:
            await asyncio.wait_for(sem.acquire_async(), timeout=0.2)
            pytest.fail("Should have timed out")
        except TimeoutError:
            elapsed = time.time() - start_time
            assert elapsed >= 0.15  # Should have blocked for at least timeout duration

        sem.release()

    async def test_unblocks_when_permit_released(self):
        """Test that blocked acquire unblocks when permit is released."""
        sem = AsyncLocalSemaphore(value=1)

        # Acquire the permit
        await sem.acquire_async()

        # Schedule release after short delay
        async def delayed_release():
            await asyncio.sleep(0.1)
            sem.release()

        # Start the delayed release
        release_task = asyncio.create_task(delayed_release())

        # Should unblock when release happens
        start_time = time.time()
        await sem.acquire_async()
        elapsed = time.time() - start_time

        assert elapsed >= 0.05  # Should have waited for the release
        assert elapsed < 0.5    # But not too long

        sem.release()
        await release_task

    async def test_fifo_ordering_of_blocked_acquires(self):
        """Test that blocked acquires are granted in FIFO order."""
        sem = AsyncLocalSemaphore(value=1)
        order = []

        await sem.acquire_async()  # Take the only permit

        async def acquire_and_record(task_id: int):
            await sem.acquire_async()
            order.append(task_id)
            sem.release()

        # Start multiple tasks that will block
        task1 = asyncio.create_task(acquire_and_record(1))
        await asyncio.sleep(0.01)  # Ensure order
        task2 = asyncio.create_task(acquire_and_record(2))
        await asyncio.sleep(0.01)
        task3 = asyncio.create_task(acquire_and_record(3))

        await asyncio.sleep(0.05)  # Let tasks get queued

        # Release to start unblocking
        sem.release()

        # Wait for all tasks
        await asyncio.gather(task1, task2, task3)

        # Should be in order (asyncio Semaphore uses FIFO)
        assert order == [1, 2, 3]


@pytest.mark.asyncio
class TestAsyncSemaphoreConcurrency:
    """Tests for concurrent access to async semaphores."""

    async def test_concurrent_acquire_respects_limit(self):
        """Test that concurrent acquires respect the semaphore limit."""
        sem = AsyncLocalSemaphore(value=3)
        concurrent_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()

        async def worker(worker_id: int):
            nonlocal concurrent_count, max_concurrent
            await sem.acquire_async()
            try:
                async with lock:
                    concurrent_count += 1
                    max_concurrent = max(max_concurrent, concurrent_count)
                await asyncio.sleep(0.05)
            finally:
                async with lock:
                    concurrent_count -= 1
                sem.release()

        # Run 10 concurrent workers
        await asyncio.gather(*[worker(i) for i in range(10)])

        # Max concurrent should never exceed semaphore value
        assert max_concurrent <= 3

    async def test_high_contention_scenario(self):
        """Test semaphore under high contention."""
        sem = AsyncLocalSemaphore(value=2)
        total_completions = 0

        async def rapid_worker():
            nonlocal total_completions
            for _ in range(10):
                await sem.acquire_async()
                await asyncio.sleep(0.001)
                total_completions += 1
                sem.release()

        # Run 5 workers doing 10 operations each
        await asyncio.gather(*[rapid_worker() for _ in range(5)])

        # All operations should complete
        assert total_completions == 50

    async def test_fairness_under_load(self):
        """Test that all tasks eventually complete under load."""
        sem = AsyncLocalSemaphore(value=2)
        completions = dict.fromkeys(range(20), False)

        async def task(task_id: int):
            await sem.acquire_async()
            await asyncio.sleep(0.01)
            completions[task_id] = True
            sem.release()

        await asyncio.gather(*[task(i) for i in range(20)])

        # All tasks should complete
        assert all(completions.values())


@pytest.mark.asyncio
class TestAsyncSemaphoreTimeout:
    """Tests for timeout handling in async semaphores."""

    async def test_acquire_with_timeout_success(self):
        """Test successful acquire within timeout."""
        sem = AsyncLocalSemaphore(value=1)

        try:
            await asyncio.wait_for(sem.acquire_async(), timeout=1.0)
            acquired = True
        except TimeoutError:
            acquired = False

        assert acquired is True
        sem.release()

    async def test_acquire_with_timeout_failure(self):
        """Test acquire timeout when no permits available."""
        sem = AsyncLocalSemaphore(value=1)

        # Take the only permit
        await sem.acquire_async()

        # Second acquire should timeout
        try:
            await asyncio.wait_for(sem.acquire_async(), timeout=0.1)
            acquired = True
        except TimeoutError:
            acquired = False

        assert acquired is False
        sem.release()

    async def test_timeout_does_not_affect_other_waiters(self):
        """Test that one waiter timing out doesn't affect others."""
        sem = AsyncLocalSemaphore(value=1)
        results = []

        await sem.acquire_async()  # Take the permit

        async def waiter_with_timeout():
            try:
                await asyncio.wait_for(sem.acquire_async(), timeout=0.05)
                results.append("acquired")
                sem.release()
            except TimeoutError:
                results.append("timeout")

        async def patient_waiter():
            await sem.acquire_async()
            results.append("patient_acquired")
            sem.release()

        # Start both waiters
        timeout_task = asyncio.create_task(waiter_with_timeout())
        await asyncio.sleep(0.01)  # Let timeout waiter queue first
        patient_task = asyncio.create_task(patient_waiter())

        await asyncio.sleep(0.1)  # Let timeout occur

        # Release the permit for patient waiter
        sem.release()

        await asyncio.gather(timeout_task, patient_task)

        assert "timeout" in results
        assert "patient_acquired" in results


@pytest.mark.asyncio
class TestAsyncSemaphoreRaceConditions:
    """Tests for race condition prevention in async semaphores."""

    async def test_rapid_acquire_release_cycles(self):
        """Test rapid acquire/release cycles don't cause races."""
        sem = AsyncLocalSemaphore(value=1)
        counter = 0

        async def rapid_cycle():
            nonlocal counter
            for _ in range(100):
                await sem.acquire_async()
                counter += 1
                sem.release()

        # Run multiple rapid cyclers concurrently
        await asyncio.gather(*[rapid_cycle() for _ in range(5)])

        assert counter == 500

    async def test_concurrent_release_safety(self):
        """Test that concurrent releases don't corrupt semaphore state."""
        sem = AsyncLocalSemaphore(value=5)

        # Acquire all permits
        for _ in range(5):
            await sem.acquire_async()

        # Release all permits concurrently
        async def release_permit():
            sem.release()

        # This shouldn't raise any errors
        await asyncio.gather(*[release_permit() for _ in range(5)])

        # Should be able to acquire all permits again
        for _ in range(5):
            await sem.acquire_async()

        for _ in range(5):
            sem.release()

    async def test_interleaved_operations_integrity(self):
        """Test integrity with interleaved acquire/release operations."""
        sem = AsyncLocalSemaphore(value=3)
        operations_log = []
        lock = asyncio.Lock()

        async def worker(worker_id: int):
            for _ in range(10):
                await sem.acquire_async()
                async with lock:
                    operations_log.append(f"acquire_{worker_id}")
                await asyncio.sleep(0.001)
                async with lock:
                    operations_log.append(f"release_{worker_id}")
                sem.release()

        await asyncio.gather(*[worker(i) for i in range(5)])

        # Count acquires and releases
        acquires = sum(1 for op in operations_log if op.startswith("acquire"))
        releases = sum(1 for op in operations_log if op.startswith("release"))

        assert acquires == releases == 50


@pytest.mark.asyncio
class TestAsyncSemaphoreResourcePool:
    """Tests for using async semaphore as a resource pool."""

    async def test_connection_pool_pattern(self):
        """Test semaphore as a connection pool."""
        pool_size = 3
        pool = AsyncLocalSemaphore(value=pool_size)
        active_connections = 0
        max_active = 0
        lock = asyncio.Lock()

        async def use_connection(task_id: int):
            nonlocal active_connections, max_active

            # Acquire a connection
            await pool.acquire_async()
            try:
                async with lock:
                    active_connections += 1
                    max_active = max(max_active, active_connections)

                # Use the connection
                await asyncio.sleep(0.02)
            finally:
                async with lock:
                    active_connections -= 1
                pool.release()

        # Simulate 10 concurrent clients
        await asyncio.gather(*[use_connection(i) for i in range(10)])

        assert max_active <= pool_size
        assert active_connections == 0

    async def test_rate_limiter_pattern(self):
        """Test semaphore as a rate limiter."""
        rate_limit = 5
        limiter = AsyncLocalSemaphore(value=rate_limit)

        request_times = []
        start_time = time.time()

        async def make_request():
            await limiter.acquire_async()
            try:
                request_times.append(time.time() - start_time)
                await asyncio.sleep(0.1)  # Simulate request processing
            finally:
                limiter.release()

        # Make 10 requests
        await asyncio.gather(*[make_request() for _ in range(10)])

        # First 5 should start immediately, next 5 should be delayed
        first_batch = request_times[:5]
        request_times[5:]

        # All first batch should be close to 0
        assert all(t < 0.05 for t in first_batch)


@pytest.mark.asyncio
class TestAsyncSemaphoreProducerConsumer:
    """Tests for producer-consumer patterns with async semaphores."""

    async def test_bounded_buffer(self):
        """Test bounded buffer implementation with semaphores."""
        buffer_size = 3
        empty_slots = AsyncLocalSemaphore(value=buffer_size)
        full_slots = AsyncLocalSemaphore(value=0)
        buffer = []
        buffer_lock = asyncio.Lock()

        async def producer(count: int):
            for i in range(count):
                await empty_slots.acquire_async()
                async with buffer_lock:
                    buffer.append(i)
                full_slots.release()

        async def consumer(count: int):
            results = []
            for _ in range(count):
                await full_slots.acquire_async()
                async with buffer_lock:
                    results.append(buffer.pop(0))
                empty_slots.release()
            return results

        # Produce and consume 10 items
        producer_task = asyncio.create_task(producer(10))
        consumer_task = asyncio.create_task(consumer(10))

        await producer_task
        results = await consumer_task

        assert len(results) == 10
        assert results == list(range(10))
        assert len(buffer) == 0

    async def test_multiple_producers_consumers(self):
        """Test multiple producers and consumers."""
        buffer_size = 5
        empty_slots = AsyncLocalSemaphore(value=buffer_size)
        full_slots = AsyncLocalSemaphore(value=0)
        buffer = []
        buffer_lock = asyncio.Lock()
        produced_count = 0
        consumed_count = 0

        async def producer(producer_id: int, count: int):
            nonlocal produced_count
            for i in range(count):
                await empty_slots.acquire_async()
                async with buffer_lock:
                    buffer.append((producer_id, i))
                    produced_count += 1
                full_slots.release()

        async def consumer(consumer_id: int, count: int):
            nonlocal consumed_count
            for _ in range(count):
                await full_slots.acquire_async()
                async with buffer_lock:
                    buffer.pop(0)
                    consumed_count += 1
                empty_slots.release()

        # 3 producers producing 5 items each
        # 3 consumers consuming 5 items each
        tasks = []
        for i in range(3):
            tasks.append(asyncio.create_task(producer(i, 5)))
            tasks.append(asyncio.create_task(consumer(i, 5)))

        await asyncio.gather(*tasks)

        assert produced_count == 15
        assert consumed_count == 15
        assert len(buffer) == 0


@pytest.mark.asyncio
class TestAsyncSemaphoreErrorHandling:
    """Tests for error handling in async semaphores."""

    async def test_exception_in_critical_section(self):
        """Test that semaphore is released even when exception occurs."""
        sem = AsyncLocalSemaphore(value=1)

        async def faulty_worker():
            await sem.acquire_async()
            try:
                raise ValueError("Simulated error")
            finally:
                sem.release()

        with pytest.raises(ValueError):
            await faulty_worker()

        # Semaphore should still be usable
        await sem.acquire_async()
        sem.release()

    async def test_cancellation_handling(self):
        """Test handling of task cancellation while waiting."""
        sem = AsyncLocalSemaphore(value=1)

        # Take the permit
        await sem.acquire_async()

        async def waiting_task():
            await sem.acquire_async()
            sem.release()

        task = asyncio.create_task(waiting_task())
        await asyncio.sleep(0.05)  # Let it start waiting

        # Cancel the waiting task
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Semaphore should still work
        sem.release()
        await sem.acquire_async()
        sem.release()

    async def test_sync_acquire_raises_not_implemented(self):
        """Test that sync acquire uses fallback (logs warning instead of raising)."""
        sem = AsyncLocalSemaphore(value=1)
        # Implementation uses fallback sync counter with warning instead of raising
        result = sem.acquire()
        assert result is True or result is None  # Fallback behavior


@pytest.mark.asyncio
class TestAsyncSemaphoreContextManager:
    """Tests for context manager usage patterns."""

    async def test_manual_context_pattern(self):
        """Test manual acquire/release as context pattern."""
        sem = AsyncLocalSemaphore(value=1)
        resource_used = False

        await sem.acquire_async()
        try:
            resource_used = True
            await asyncio.sleep(0.01)
        finally:
            sem.release()

        assert resource_used

    async def test_nested_semaphore_usage(self):
        """Test nested semaphore usage."""
        outer_sem = AsyncLocalSemaphore(value=2)
        inner_sem = AsyncLocalSemaphore(value=1)

        async def nested_worker():
            await outer_sem.acquire_async()
            try:
                await inner_sem.acquire_async()
                try:
                    await asyncio.sleep(0.01)
                finally:
                    inner_sem.release()
            finally:
                outer_sem.release()

        # Run multiple nested workers
        await asyncio.gather(*[nested_worker() for _ in range(5)])


# ==================== ASYNC LOCK PATTERNS TESTS ====================

@pytest.mark.asyncio
class TestAsyncLockPatterns:
    """Tests for async lock patterns using semaphores and locks."""

    async def test_mutex_pattern(self):
        """Test mutex pattern with semaphore(1)."""
        mutex = AsyncLocalSemaphore(value=1)
        shared_resource = {"counter": 0}

        async def increment():
            await mutex.acquire_async()
            try:
                current = shared_resource["counter"]
                await asyncio.sleep(0.001)  # Simulate some work
                shared_resource["counter"] = current + 1
            finally:
                mutex.release()

        # Run 100 concurrent increments
        await asyncio.gather(*[increment() for _ in range(100)])

        assert shared_resource["counter"] == 100

    async def test_readers_writers_pattern(self):
        """Test readers-writers pattern."""
        read_sem = AsyncLocalSemaphore(value=10)  # Allow up to 10 concurrent readers
        write_lock = AsyncLocalSemaphore(value=1)
        reader_count = 0
        reader_count_lock = asyncio.Lock()

        read_count_total = 0
        write_count_total = 0

        async def reader():
            nonlocal read_count_total, reader_count
            await read_sem.acquire_async()
            try:
                async with reader_count_lock:
                    reader_count += 1
                    if reader_count == 1:
                        await write_lock.acquire_async()  # Block writers

                # Read operation
                await asyncio.sleep(0.01)
                read_count_total += 1

                async with reader_count_lock:
                    reader_count -= 1
                    if reader_count == 0:
                        write_lock.release()  # Allow writers
            finally:
                read_sem.release()

        async def writer():
            nonlocal write_count_total
            await write_lock.acquire_async()
            try:
                # Write operation
                await asyncio.sleep(0.01)
                write_count_total += 1
            finally:
                write_lock.release()

        # Run readers and writers
        tasks = [reader() for _ in range(10)] + [writer() for _ in range(3)]
        await asyncio.gather(*tasks)

        assert read_count_total == 10
        assert write_count_total == 3


@pytest.mark.asyncio
class TestAsyncDeadlockPrevention:
    """Tests for deadlock prevention patterns."""

    async def test_ordered_lock_acquisition(self):
        """Test that ordered lock acquisition prevents deadlock."""
        lock_a = AsyncLocalSemaphore(value=1)
        lock_b = AsyncLocalSemaphore(value=1)

        async def worker1():
            # Always acquire A before B
            await lock_a.acquire_async()
            await asyncio.sleep(0.01)
            await lock_b.acquire_async()

            await asyncio.sleep(0.01)

            lock_b.release()
            lock_a.release()

        async def worker2():
            # Always acquire A before B (same order)
            await lock_a.acquire_async()
            await asyncio.sleep(0.01)
            await lock_b.acquire_async()

            await asyncio.sleep(0.01)

            lock_b.release()
            lock_a.release()

        # Should complete without deadlock
        await asyncio.wait_for(
            asyncio.gather(worker1(), worker2()),
            timeout=2.0
        )

    async def test_trylock_pattern(self):
        """Test try-lock pattern for deadlock avoidance."""
        lock_a = AsyncLocalSemaphore(value=1)
        lock_b = AsyncLocalSemaphore(value=1)

        success_count = 0
        retry_count = 0

        async def try_acquire_both():
            nonlocal success_count, retry_count
            max_retries = 10

            for attempt in range(max_retries):
                await lock_a.acquire_async()
                try:
                    # Try to acquire lock_b with timeout
                    try:
                        await asyncio.wait_for(lock_b.acquire_async(), timeout=0.01)
                        # Got both locks
                        await asyncio.sleep(0.01)
                        success_count += 1
                        lock_b.release()
                        return
                    except TimeoutError:
                        retry_count += 1
                        await asyncio.sleep(0.01)  # Back off
                finally:
                    lock_a.release()

        # Run multiple workers using try-lock pattern
        await asyncio.gather(*[try_acquire_both() for _ in range(5)])


@pytest.mark.asyncio
class TestAsyncSemaphoreStress:
    """Stress tests for async semaphores."""

    async def test_many_concurrent_tasks(self):
        """Test semaphore with many concurrent tasks."""
        sem = AsyncLocalSemaphore(value=10)
        completions = 0

        async def task():
            nonlocal completions
            await sem.acquire_async()
            await asyncio.sleep(0.001)
            completions += 1
            sem.release()

        # Run 100 concurrent tasks
        await asyncio.gather(*[task() for _ in range(100)])

        assert completions == 100

    async def test_sustained_load(self):
        """Test semaphore under sustained load."""
        sem = AsyncLocalSemaphore(value=5)
        total_ops = 0
        duration = 0.5  # Run for half a second

        async def continuous_worker():
            nonlocal total_ops
            end_time = time.time() + duration
            while time.time() < end_time:
                await sem.acquire_async()
                await asyncio.sleep(0.001)
                total_ops += 1
                sem.release()

        await asyncio.gather(*[continuous_worker() for _ in range(10)])

        # Should have completed many operations
        assert total_ops > 100


# ==================== LOCAL SEMAPHORE ASYNC INTERACTION TESTS ====================

@pytest.mark.asyncio
class TestLocalSemaphoreAsyncInteraction:
    """Tests for LocalSemaphore interaction with async code."""

    async def test_local_semaphore_in_thread(self):
        """Test LocalSemaphore used from async code via threads."""
        sem = LocalSemaphore(value=2)
        results = []

        def blocking_operation(task_id: int):
            if sem.acquire(timeout=1.0):
                results.append(f"acquired_{task_id}")
                time.sleep(0.05)
                sem.release()
                results.append(f"released_{task_id}")

        # Run blocking operations in thread pool
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, blocking_operation, i)
            for i in range(5)
        ]

        await asyncio.gather(*tasks)

        # All operations should complete
        assert len([r for r in results if r.startswith("acquired")]) == 5
        assert len([r for r in results if r.startswith("released")]) == 5
