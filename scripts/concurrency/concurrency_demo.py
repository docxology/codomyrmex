#!/usr/bin/env python3
"""
Comprehensive demo of the Codomyrmex Concurrency Module.
Demonstrates LocalLock, RedisLock (via fakeredis), ReadWriteLock,
LocalSemaphore, and AsyncWorkerPool.
"""

import sys
import time
import random
import threading
import asyncio
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.concurrency import (
    LocalLock,
    LockManager,
    ReadWriteLock,
    LocalSemaphore,
    AsyncWorkerPool,
    RedisLock
)

# Use fakeredis for zero-mock demonstration
try:
    import fakeredis
except ImportError:
    fakeredis = None

def section(name: str):
    print(f"\n--- {name} ---")

def demo_local_lock():
    section("LocalLock (Process & Thread Safe)")
    lock = LocalLock("demo_resource")

    # Re-entry demonstration
    print("Attempting re-entry...")
    with lock:
        print("  Locked once")
        with lock:
            print("    Locked twice (re-entry)")
    print("  Released all")

def demo_read_write_lock():
    section("ReadWriteLock (Multiple Readers, Exclusive Writer)")
    rw_lock = ReadWriteLock()
    results = []

    def reader(id: int):
        with rw_lock.read_lock():
            print(f"  Reader {id} entered")
            time.sleep(0.1)
            results.append(f"R{id}")
            print(f"  Reader {id} exited")

    def writer(id: int):
        with rw_lock.write_lock():
            print(f"  Writer {id} entered")
            time.sleep(0.2)
            results.append(f"W{id}")
            print(f"  Writer {id} exited")

    threads = [
        threading.Thread(target=reader, args=(1,)),
        threading.Thread(target=reader, args=(2,)),
        threading.Thread(target=writer, args=(1,)),
        threading.Thread(target=reader, args=(3,)),
    ]

    for t in threads: t.start()
    for t in threads: t.join()
    print(f"Sequence: {results}")

def demo_lock_manager():
    section("LockManager (Multi-resource Acquisition)")
    manager = LockManager()
    manager.register_lock("resource_A", LocalLock("A"))
    manager.register_lock("resource_B", LocalLock("B"))

    print("Acquiring multiple resources safely...")
    if manager.acquire_all(["resource_A", "resource_B"], timeout=5.0):
        try:
            print("  Acquired resource_A and resource_B")
        finally:
            manager.release_all(["resource_A", "resource_B"])
            print("  Released all resources")

    stats = manager.stats
    print(f"Manager Stats: Total acquisitions={stats.total_acquisitions}")

def demo_redis_lock():
    section("RedisLock (Distributed Coordination)")
    if not fakeredis:
        print("  Skipping: fakeredis not installed")
        return

    client = fakeredis.FakeRedis()
    lock = RedisLock("global_task", client, ttl=10)

    print("Acquiring distributed lock...")
    with lock:
        print("  Acquired distributed lock")
        print(f"  Is locked externally? {lock.is_locked_externally()}")
        print("  Extending lock TTL...")
        if lock.extend(20):
            print("  Lock extended")
    print("  Released distributed lock")

def demo_semaphore():
    section("LocalSemaphore (Resource Throttling)")
    sem = LocalSemaphore(value=2)

    def throttled_worker(id: int):
        with sem:
            print(f"  Worker {id} processing...")
            time.sleep(0.2)
            print(f"  Worker {id} done")

    threads = [threading.Thread(target=throttled_worker, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()

async def demo_async_worker_pool():
    section("AsyncWorkerPool (Bounded Async Execution)")

    async def task(item: str, delay: float):
        await asyncio.sleep(delay)
        return f"Processed {item}"

    print("Running 10 tasks with max_workers=3...")
    async with AsyncWorkerPool(max_workers=3, name="demo_pool") as pool:
        items = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        # Mix of delays
        results = await pool.map(lambda x: task(x, random.uniform(0.1, 0.3)), items)

        success_count = sum(1 for r in results if r.success)
        print(f"  Completed {success_count}/{len(items)} tasks")

        stats = pool.stats
        print(f"  Pool Stats: Completed={stats.completed}, Failed={stats.failed}")

def main():
    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "concurrency" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    print("🚀 Codomyrmex Concurrency Module Demo")

    demo_local_lock()
    demo_read_write_lock()
    demo_lock_manager()
    demo_redis_lock()
    demo_semaphore()

    asyncio.run(demo_async_worker_pool())

    print("\n✅ Concurrency Demo Completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
