#!/usr/bin/env python3
"""Distributed locking example for the concurrency module.

This script demonstrates distributed lock patterns for multi-process
and multi-machine coordination.

Usage:
    python distributed_locking.py [--redis-url URL]
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from codomyrmex.utils.cli_helpers import print_success, print_error, print_info
except ImportError:
    def print_success(msg): print(f"SUCCESS: {msg}")
    def print_error(msg): print(f"ERROR: {msg}")
    def print_info(msg): print(f"INFO: {msg}")


async def simulate_distributed_work(worker_id: int, lock, duration: float = 0.1):
    """Simulate work that requires exclusive access."""
    async with lock:
        print_info(f"  Worker {worker_id}: Acquired lock, working...")
        await asyncio.sleep(duration)
        print_success(f"  Worker {worker_id}: Released lock")


def main():
    """Demonstrate distributed locking patterns."""
    parser = argparse.ArgumentParser(description="Distributed locking demo")
    parser.add_argument("--redis-url", help="Redis URL for distributed locks")
    parser.add_argument("--workers", type=int, default=3, help="Number of workers")
    args = parser.parse_args()

    print_info("Concurrency Module - Distributed Locking Example")
    print_info("=" * 50)

    try:
        from codomyrmex.concurrency import LocalLock, LockManager

        # Demonstrate local lock (in-process)
        print_info("\n1. Local lock pattern (in-process)")
        local_lock = LocalLock("shared_resource")

        print_info(f"   Simulating {args.workers} workers with shared resource...")
        # Note: For true async demonstration, would use asyncio
        for i in range(args.workers):
            with local_lock:
                print_info(f"   Worker {i}: Has exclusive access")

        print_success("   All workers completed successfully")

        # Show distributed lock pattern
        print_info("\n2. Distributed lock pattern (cross-process)")
        if args.redis_url:
            from codomyrmex.concurrency import RedisLock
            print_info(f"   Using Redis at: {args.redis_url}")
            # Would create RedisLock here
        else:
            print_info("   Redis not configured - showing pattern only")
            print_info("   Use --redis-url to enable distributed locking")

        # Demonstrate LockManager
        print_info("\n3. LockManager for centralized lock handling")
        manager = LockManager()
        print_success(f"   Created manager: {type(manager).__name__}")

        # Show lock patterns
        print_info("\n4. Common distributed lock patterns:")
        print_info("   - Leader election: One process coordinates")
        print_info("   - Resource pooling: Limit concurrent access")
        print_info("   - Task coordination: Prevent duplicate work")
        print_info("   - Rate limiting: Control request rates")

        print_success("\nDistributed locking demonstration complete!")
        return 0

    except ImportError as e:
        print_error(f"Failed to import concurrency module: {e}")
        return 1
    except Exception as e:
        print_error(f"Error during demonstration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
