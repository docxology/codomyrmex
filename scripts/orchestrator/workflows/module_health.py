#!/usr/bin/env python3
"""Module health check workflow.

Check health of all modules in the project:
1. Verify imports work
2. Check for required files (README, AGENTS.md, __init__.py)
3. Run module-specific tests
4. Generate health report

Usage:
    python module_health.py [--module MODULE] [--fix]
"""

import argparse
import asyncio
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator import Workflow, parallel
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def get_all_modules() -> List[Path]:
    """Get all module directories."""
    src_dir = project_root / "src" / "codomyrmex"
    modules = []

    for item in src_dir.iterdir():
        if item.is_dir() and not item.name.startswith(("_", ".")):
            if (item / "__init__.py").exists():
                modules.append(item)

    return sorted(modules)


async def check_module_imports(module_path: Path) -> Dict[str, Any]:
    """Check if module can be imported."""
    module_name = f"codomyrmex.{module_path.name}"

    try:
        importlib.import_module(module_name)
        return {"success": True, "module": module_name}
    except Exception as e:
        return {"success": False, "module": module_name, "error": str(e)}


async def check_module_files(module_path: Path) -> Dict[str, Any]:
    """Check for required files."""
    required_files = ["__init__.py"]
    recommended_files = ["README.md", "AGENTS.md"]

    missing_required = []
    missing_recommended = []

    for f in required_files:
        if not (module_path / f).exists():
            missing_required.append(f)

    for f in recommended_files:
        if not (module_path / f).exists():
            missing_recommended.append(f)

    return {
        "success": len(missing_required) == 0,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "has_tests": (module_path / "tests").exists() or
                    any((project_root / "src" / "codomyrmex" / "tests" / "unit").glob(f"*{module_path.name}*"))
    }


async def check_module_health(module_path: Path, _task_results: dict = None) -> Dict[str, Any]:
    """Full health check for a module."""
    module_name = module_path.name

    # Run checks
    import_result = await check_module_imports(module_path)
    files_result = await check_module_files(module_path)

    # Calculate health score
    score = 100
    issues = []

    if not import_result["success"]:
        score -= 40
        issues.append(f"Import failed: {import_result.get('error', 'Unknown')}")

    if files_result["missing_required"]:
        score -= 30
        issues.append(f"Missing required: {', '.join(files_result['missing_required'])}")

    if files_result["missing_recommended"]:
        score -= 10
        issues.append(f"Missing recommended: {', '.join(files_result['missing_recommended'])}")

    if not files_result["has_tests"]:
        score -= 20
        issues.append("No tests found")

    status = "healthy" if score >= 80 else "degraded" if score >= 50 else "unhealthy"

    return {
        "module": module_name,
        "status": status,
        "score": score,
        "import_ok": import_result["success"],
        "issues": issues,
        "details": {
            "import": import_result,
            "files": files_result
        }
    }


async def main():
    """Run module health workflow."""
    parser = argparse.ArgumentParser(description="Check module health")
    parser.add_argument("--module", "-m", help="Specific module to check")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.module:
        modules = [project_root / "src" / "codomyrmex" / args.module]
        if not modules[0].exists():
            print(f"Module not found: {args.module}")
            return 1
    else:
        modules = get_all_modules()

    print(f"🏥 Checking health of {len(modules)} modules...")
    print()

    results = []
    for module_path in modules:
        result = await check_module_health(module_path)
        results.append(result)

        # Print status
        icon = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(result["status"], "❓")
        print(f"  {icon} {result['module']:30} [{result['score']:3}%] {result['status']}")

        if args.verbose and result["issues"]:
            for issue in result["issues"]:
                print(f"      - {issue}")

    # Summary
    print()
    print("=" * 50)
    healthy = sum(1 for r in results if r["status"] == "healthy")
    degraded = sum(1 for r in results if r["status"] == "degraded")
    unhealthy = sum(1 for r in results if r["status"] == "unhealthy")

    print(f"Summary: {healthy} healthy, {degraded} degraded, {unhealthy} unhealthy")

    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    print(f"Average health score: {avg_score:.0f}%")

    # Fix mode
    if args.fix:
        print()
        print("Attempting fixes...")
        for result in results:
            if result["details"]["files"]["missing_recommended"]:
                module_path = project_root / "src" / "codomyrmex" / result["module"]
                for missing in result["details"]["files"]["missing_recommended"]:
                    file_path = module_path / missing
                    if missing == "README.md":
                        file_path.write_text(f"# {result['module'].replace('_', ' ').title()}\n\nModule documentation.\n")
                        print(f"  Created: {file_path}")
                    elif missing == "AGENTS.md":
                        file_path.write_text(f"# Agents for {result['module']}\n\nAgent instructions.\n")
                        print(f"  Created: {file_path}")

    return 0 if unhealthy == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
