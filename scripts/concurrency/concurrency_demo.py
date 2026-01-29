#!/usr/bin/env python3
"""
Concurrency utilities for parallel task management.

Usage:
    python concurrency_demo.py [--workers N] [--demo TYPE]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import concurrent.futures
import threading
import time
import random


def worker_task(task_id: int, duration: float) -> dict:
    """Simulate a worker task."""
    start = time.time()
    time.sleep(duration)
    return {
        "task_id": task_id,
        "thread": threading.current_thread().name,
        "duration": round(time.time() - start, 3),
    }


def demo_thread_pool(num_tasks: int = 10, workers: int = 4) -> list:
    """Demonstrate thread pool execution."""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for i in range(num_tasks):
            duration = random.uniform(0.1, 0.5)
            futures.append(executor.submit(worker_task, i, duration))
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    return results


def demo_process_pool(num_tasks: int = 5, workers: int = 2) -> list:
    """Demonstrate process pool execution."""
    results = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(worker_task, i, 0.2): i for i in range(num_tasks)}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append({"error": str(e)})
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Concurrency utilities demo")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Number of workers")
    parser.add_argument("--tasks", "-t", type=int, default=10, help="Number of tasks")
    parser.add_argument("--demo", "-d", choices=["thread", "process", "all"], default="thread")
    args = parser.parse_args()
    
    print("⚡ Concurrency Demo\n")
    
    if args.demo in ["thread", "all"]:
        print(f"🔄 Thread Pool ({args.workers} workers, {args.tasks} tasks):")
        start = time.time()
        results = demo_thread_pool(args.tasks, args.workers)
        elapsed = time.time() - start
        
        print(f"   Completed: {len(results)} tasks in {elapsed:.2f}s")
        print(f"   Threads used: {len(set(r['thread'] for r in results))}")
        total_work = sum(r['duration'] for r in results)
        print(f"   Speedup: {total_work / elapsed:.1f}x")
        print()
    
    if args.demo in ["process", "all"]:
        print(f"🔄 Process Pool ({args.workers} workers, {min(args.tasks, 5)} tasks):")
        start = time.time()
        results = demo_process_pool(min(args.tasks, 5), args.workers)
        elapsed = time.time() - start
        
        successful = [r for r in results if "error" not in r]
        print(f"   Completed: {len(successful)}/{len(results)} tasks in {elapsed:.2f}s")
    
    print("\n💡 Tips:")
    print("   - Use ThreadPoolExecutor for I/O-bound tasks")
    print("   - Use ProcessPoolExecutor for CPU-bound tasks")
    print("   - Consider asyncio for many concurrent I/O operations")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
