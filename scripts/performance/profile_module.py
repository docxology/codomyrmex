#!/usr/bin/env python3
"""
Profile a Python module or function for performance analysis.

Usage:
    python profile_module.py <module_path> [--function FUNC] [--output OUTPUT]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import cProfile
import pstats
import io
import time
import importlib.util


def load_module(module_path: str):
    """Dynamically load a Python module."""
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile_function(func, *args, **kwargs) -> tuple:
    """Profile a function and return stats."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    
    profiler.disable()
    
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(20)
    
    return result, elapsed, stream.getvalue(), stats


def format_time(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


def main():
    parser = argparse.ArgumentParser(description="Profile Python module/function")
    parser.add_argument("module_path", nargs="?", help="Path to Python module")
    parser.add_argument("--function", "-f", default="main", help="Function to profile (default: main)")
    parser.add_argument("--output", "-o", default=None, help="Output file for profile data")
    parser.add_argument("--top", "-t", type=int, default=15, help="Show top N functions")
    parser.add_argument("--demo", action="store_true", help="Run a demo profile")
    args = parser.parse_args()
    
    if args.demo:
        print("🔬 Performance Profiler Demo\n")
        
        # Demo function to profile
        def demo_function():
            result = []
            for i in range(10000):
                result.append(str(i) * 10)
            return "".join(result)
        
        result, elapsed, profile_output, stats = profile_function(demo_function)
        
        print(f"⏱️  Execution time: {format_time(elapsed)}")
        print(f"📊 Result size: {len(result)} characters\n")
        print("📈 Top functions by cumulative time:")
        print(profile_output[:2000])
        return 0
    
    if not args.module_path:
        print("🔬 Performance Profiler")
        print("\nUsage:")
        print("  python profile_module.py <module.py> --function <func_name>")
        print("  python profile_module.py --demo")
        print("\nExample:")
        print("  python profile_module.py my_script.py --function process_data")
        return 0
    
    module_path = Path(args.module_path)
    if not module_path.exists():
        print(f"❌ Module not found: {module_path}")
        return 1
    
    print(f"🔬 Profiling: {module_path}")
    print(f"   Function: {args.function}\n")
    
    try:
        module = load_module(str(module_path))
    except Exception as e:
        print(f"❌ Failed to load module: {e}")
        return 1
    
    if not hasattr(module, args.function):
        print(f"❌ Function '{args.function}' not found in module")
        available = [n for n in dir(module) if not n.startswith("_") and callable(getattr(module, n))]
        if available:
            print(f"   Available: {', '.join(available[:10])}")
        return 1
    
    func = getattr(module, args.function)
    
    try:
        result, elapsed, profile_output, stats = profile_function(func)
        print(f"⏱️  Execution time: {format_time(elapsed)}")
        print("\n📈 Top functions by cumulative time:\n")
        print(profile_output[:3000])
        
        if args.output:
            stats.dump_stats(args.output)
            print(f"💾 Profile data saved to: {args.output}")
    
    except Exception as e:
        print(f"❌ Profiling failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
