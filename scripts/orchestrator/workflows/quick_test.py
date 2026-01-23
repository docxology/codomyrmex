#!/usr/bin/env python3
"""Quick test workflow for rapid validation.

Fast parallel execution of tests across multiple modules.

Usage:
    python quick_test.py [--modules MODULE...] [--workers N]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator import run_parallel, discover_scripts
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def main():
    """Run quick test workflow."""
    parser = argparse.ArgumentParser(description="Quick parallel test runner")
    parser.add_argument("--modules", "-m", nargs="+", help="Specific modules to test")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Parallel workers")
    parser.add_argument("--timeout", "-t", type=int, default=60, help="Timeout per test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    test_dir = project_root / "src" / "codomyrmex" / "tests" / "unit"

    # Find test files
    if args.modules:
        test_files = []
        for module in args.modules:
            module_test_dir = test_dir / module
            if module_test_dir.exists():
                test_files.extend(module_test_dir.glob("test_*.py"))
            else:
                # Try direct file
                test_file = test_dir / f"test_{module}.py"
                if test_file.exists():
                    test_files.append(test_file)
    else:
        test_files = list(test_dir.glob("**/test_*.py"))

    if not test_files:
        print("No test files found")
        return 1

    print(f"🧪 Running {len(test_files)} test files with {args.workers} workers")
    print()

    def on_progress(name: str, status: str, details: dict):
        if args.verbose:
            exec_time = details.get("execution_time", 0)
            print(f"  [{status.upper():8}] {name} ({exec_time:.1f}s)")
        elif status == "failed":
            print(f"  ❌ {name}")

    result = run_parallel(
        scripts=test_files,
        max_workers=args.workers,
        timeout=args.timeout,
        progress_callback=on_progress if args.verbose else None
    )

    print()
    print("=" * 50)
    print(f"Results: {result.passed}/{result.total} passed")
    print(f"  Passed:  {result.passed}")
    print(f"  Failed:  {result.failed}")
    print(f"  Timeout: {result.timeout}")
    print(f"  Time:    {result.execution_time:.1f}s")

    if result.failed > 0:
        print("\nFailed tests:")
        for r in result.results:
            if r.get("status") != "passed":
                print(f"  ❌ {r.get('name')}")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
