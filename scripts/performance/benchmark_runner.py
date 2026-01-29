#!/usr/bin/env python3
"""
Run benchmarks and compare against baseline.

Usage:
    python benchmark_runner.py [--suite SUITE] [--iterations N] [--save-baseline]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import time
import json
import statistics


# Built-in benchmark suite
def benchmark_string_operations(n=10000):
    """Benchmark string concatenation and formatting."""
    result = ""
    for i in range(n):
        result += str(i)
    return len(result)


def benchmark_list_operations(n=10000):
    """Benchmark list append and iteration."""
    data = []
    for i in range(n):
        data.append(i * 2)
    return sum(data)


def benchmark_dict_operations(n=10000):
    """Benchmark dictionary operations."""
    data = {}
    for i in range(n):
        data[f"key_{i}"] = i * 3
    return sum(data.values())


def benchmark_file_io(n=100):
    """Benchmark file write/read operations."""
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        path = f.name
        for i in range(n):
            f.write(f"Line {i}\n" * 100)
    
    with open(path, 'r') as f:
        lines = f.readlines()
    
    os.unlink(path)
    return len(lines)


BENCHMARKS = {
    "string": benchmark_string_operations,
    "list": benchmark_list_operations,
    "dict": benchmark_dict_operations,
    "file_io": benchmark_file_io,
}


def run_benchmark(name: str, func, iterations: int = 5) -> dict:
    """Run a benchmark multiple times and collect stats."""
    times = []
    result = None
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return {
        "name": name,
        "iterations": iterations,
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "result": result,
    }


def format_time(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


def load_baseline(path: Path) -> dict:
    """Load baseline results from file."""
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_baseline(results: list, path: Path):
    """Save results as baseline."""
    data = {r["name"]: r for r in results}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Run performance benchmarks")
    parser.add_argument("--suite", "-s", default="all", help="Benchmark suite (all, string, list, dict, file_io)")
    parser.add_argument("--iterations", "-i", type=int, default=5, help="Iterations per benchmark")
    parser.add_argument("--save-baseline", action="store_true", help="Save results as baseline")
    parser.add_argument("--compare", "-c", action="store_true", help="Compare to baseline")
    args = parser.parse_args()
    
    print("⚡ Performance Benchmark Runner\n")
    
    # Select benchmarks
    if args.suite == "all":
        benchmarks = BENCHMARKS
    elif args.suite in BENCHMARKS:
        benchmarks = {args.suite: BENCHMARKS[args.suite]}
    else:
        print(f"❌ Unknown suite: {args.suite}")
        print(f"   Available: all, {', '.join(BENCHMARKS.keys())}")
        return 1
    
    baseline_path = Path(__file__).parent / "benchmark_baseline.json"
    baseline = load_baseline(baseline_path) if args.compare else {}
    
    results = []
    
    print(f"Running {len(benchmarks)} benchmark(s) with {args.iterations} iterations each\n")
    
    for name, func in benchmarks.items():
        print(f"🔄 {name}...", end=" ", flush=True)
        result = run_benchmark(name, func, args.iterations)
        results.append(result)
        
        baseline_result = baseline.get(name)
        if baseline_result:
            diff = (result["mean"] - baseline_result["mean"]) / baseline_result["mean"] * 100
            if diff > 5:
                indicator = f"🔴 +{diff:.1f}%"
            elif diff < -5:
                indicator = f"🟢 {diff:.1f}%"
            else:
                indicator = f"🟡 {diff:+.1f}%"
            print(f"{format_time(result['mean'])} (±{format_time(result['stdev'])}) {indicator}")
        else:
            print(f"{format_time(result['mean'])} (±{format_time(result['stdev'])})")
    
    print("\n📊 Summary:")
    print("-" * 60)
    print(f"{'Benchmark':<15} {'Min':<12} {'Mean':<12} {'Max':<12} {'StdDev':<12}")
    print("-" * 60)
    
    for r in results:
        print(f"{r['name']:<15} {format_time(r['min']):<12} {format_time(r['mean']):<12} {format_time(r['max']):<12} {format_time(r['stdev']):<12}")
    
    if args.save_baseline:
        save_baseline(results, baseline_path)
        print(f"\n💾 Baseline saved to: {baseline_path}")
    elif not baseline and baseline_path.exists():
        print(f"\n💡 Use --compare to compare with baseline")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
