#!/usr/bin/env python3
"""Build and validation workflow.

Complete build pipeline with validation:
1. Clean previous build artifacts
2. Run linting and type checking
3. Run tests
4. Build package
5. Validate build

Usage:
    python build_and_validate.py [--skip-tests] [--skip-lint]
"""

import argparse
import asyncio
import shutil
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator import Workflow, RetryPolicy
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


async def clean_build(_task_results: dict = None) -> dict:
    """Clean previous build artifacts."""
    dirs_to_clean = [
        project_root / "dist",
        project_root / "build",
        project_root / ".pytest_cache",
    ]

    # Also clean __pycache__ directories
    pycache_dirs = list(project_root.glob("**/__pycache__"))

    cleaned = 0
    for d in dirs_to_clean + pycache_dirs[:50]:  # Limit pycache cleanup
        if d.exists():
            try:
                shutil.rmtree(d)
                cleaned += 1
            except Exception:
                pass  # best-effort cleanup

    return {"success": True, "directories_cleaned": cleaned}


async def run_linting(_task_results: dict = None) -> dict:
    """Run ruff linting."""
    result = subprocess.run(
        ["uv", "run", "ruff", "check", "src/", "--output-format=concise"],
        capture_output=True,
        text=True,
        cwd=project_root
    )

    issues = result.stdout.count("\n") if result.stdout else 0

    return {
        "success": result.returncode == 0,
        "issues": issues,
        "output": result.stdout[:1000] if result.stdout else ""
    }


async def run_type_checking(_task_results: dict = None) -> dict:
    """Run mypy type checking."""
    result = subprocess.run(
        ["uv", "run", "mypy", "src/codomyrmex", "--ignore-missing-imports", "--no-error-summary"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=project_root
    )

    errors = result.stdout.count("error:") if result.stdout else 0

    return {
        "success": result.returncode == 0,
        "errors": errors,
        "output": result.stdout[:1000] if result.stdout else ""
    }


async def run_tests(_task_results: dict = None) -> dict:
    """Run test suite."""
    result = subprocess.run(
        ["uv", "run", "pytest", "src/codomyrmex/tests/unit", "-q", "--tb=no", "-x"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=project_root
    )

    # Extract pass/fail counts
    passed = failed = 0
    for line in result.stdout.split("\n"):
        if "passed" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "passed" and i > 0:
                    try:
                        passed = int(parts[i-1])
                    except ValueError:
                        pass
                if p == "failed" and i > 0:
                    try:
                        failed = int(parts[i-1])
                    except ValueError:
                        pass

    return {
        "success": result.returncode == 0,
        "passed": passed,
        "failed": failed,
        "output": result.stdout[-500:] if result.stdout else ""
    }


async def build_package(_task_results: dict = None) -> dict:
    """Build the package."""
    result = subprocess.run(
        ["uv", "build"],
        capture_output=True,
        text=True,
        cwd=project_root
    )

    # Find built files
    dist_dir = project_root / "dist"
    built_files = list(dist_dir.glob("*")) if dist_dir.exists() else []

    return {
        "success": result.returncode == 0,
        "files": [f.name for f in built_files],
        "output": result.stdout
    }


async def validate_build(_task_results: dict = None) -> dict:
    """Validate the built package."""
    from codomyrmex.orchestrator import TaskResult

    dist_dir = project_root / "dist"

    if not dist_dir.exists():
        return {"success": False, "error": "dist directory not found"}

    wheels = list(dist_dir.glob("*.whl"))
    tarballs = list(dist_dir.glob("*.tar.gz"))

    validation_passed = True
    issues = []

    if not wheels:
        issues.append("No wheel file found")
        validation_passed = False

    if not tarballs:
        issues.append("No source tarball found")
        validation_passed = False

    # Check wheel can be inspected
    if wheels:
        result = subprocess.run(
            ["python", "-m", "zipfile", "-l", str(wheels[0])],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            issues.append("Wheel file inspection failed")
            validation_passed = False

    return {
        "success": validation_passed,
        "wheels": [w.name for w in wheels],
        "tarballs": [t.name for t in tarballs],
        "issues": issues
    }


async def main() -> int:
    """Run the build workflow."""
    setup_logging()
    parser = argparse.ArgumentParser(description="Build and validate package")
    parser.add_argument("--skip-tests", action="store_true", help="Skip tests")
    parser.add_argument("--skip-lint", action="store_true", help="Skip linting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    def on_progress(task: str, status: str, details: dict):
        if args.verbose:
            print(f"  [{status.upper():10}] {task}")

    workflow = Workflow(
        name="build_and_validate",
        timeout=600,
        fail_fast=True,
        progress_callback=on_progress
    )

    # Clean
    workflow.add_task(name="clean", action=clean_build, timeout=30)

    # Parallel linting and type checking
    if not args.skip_lint:
        workflow.add_task(
            name="lint",
            action=run_linting,
            dependencies=["clean"],
            timeout=60
        )
        workflow.add_task(
            name="typecheck",
            action=run_type_checking,
            dependencies=["clean"],
            timeout=120
        )

    # Tests after lint/typecheck
    if not args.skip_tests:
        deps = ["clean"]
        if not args.skip_lint:
            deps.extend(["lint", "typecheck"])
        workflow.add_task(
            name="tests",
            action=run_tests,
            dependencies=deps,
            timeout=300,
            retry_policy=RetryPolicy(max_attempts=2)
        )

    # Build after all checks pass
    build_deps = ["clean"]
    if not args.skip_lint:
        build_deps.extend(["lint", "typecheck"])
    if not args.skip_tests:
        build_deps.append("tests")

    workflow.add_task(
        name="build",
        action=build_package,
        dependencies=build_deps,
        timeout=60
    )

    # Validate after build
    workflow.add_task(
        name="validate",
        action=validate_build,
        dependencies=["build"],
        timeout=30
    )

    print_info("Running build workflow...")
    print()

    try:
        await workflow.run()
        summary = workflow.get_summary()

        print()
        print("=" * 50)
        print(f"Build {'succeeded' if summary['success'] else 'failed'}")
        print(f"  Tasks: {summary['completed']}/{summary['total_tasks']}")
        print(f"  Time:  {summary['elapsed_time']:.1f}s")

        # Show task details
        for name, task in workflow.tasks.items():
            icon = "✅" if task.status.value == "completed" else "❌"
            print(f"  {icon} {name}: {task.status.value}")
            if task.error:
                print(f"      Error: {task.error}")

        return 0 if summary["success"] else 1

    except Exception as e:
        print_error(f"Build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
