#!/usr/bin/env python3
"""Dependency check workflow.

Check and update project dependencies:
1. List outdated packages
2. Check for security vulnerabilities
3. Verify dependency compatibility
4. Generate update report

Usage:
    python dependency_check.py [--update] [--security-only]
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator import Workflow, parallel
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error


async def list_outdated_packages(_task_results: dict = None) -> Dict[str, Any]:
    """List outdated packages using pip."""
    result = subprocess.run(
        ["uv", "pip", "list", "--outdated", "--format=json"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=120
    )

    outdated = []
    if result.returncode == 0 and result.stdout.strip():
        try:
            outdated = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass

    return {
        "success": result.returncode == 0,
        "outdated_count": len(outdated),
        "packages": outdated[:20]  # Limit to top 20
    }


async def check_security_vulnerabilities(_task_results: dict = None) -> Dict[str, Any]:
    """Check for known security vulnerabilities."""
    # Try pip-audit or safety
    result = subprocess.run(
        ["uv", "run", "pip-audit", "--format=json", "--progress-spinner=off"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=180
    )

    vulnerabilities = []
    if result.returncode == 0 and result.stdout.strip():
        try:
            audit_result = json.loads(result.stdout)
            if isinstance(audit_result, dict):
                vulnerabilities = audit_result.get("vulnerabilities", [])
            elif isinstance(audit_result, list):
                vulnerabilities = audit_result
        except json.JSONDecodeError:
            pass

    return {
        "success": True,
        "vulnerabilities_found": len(vulnerabilities),
        "vulnerabilities": vulnerabilities[:10],  # Limit output
        "audit_available": result.returncode == 0
    }


async def check_dependency_tree(_task_results: dict = None) -> Dict[str, Any]:
    """Analyze dependency tree for issues."""
    result = subprocess.run(
        ["uv", "pip", "check"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=60
    )

    issues = []
    if result.stdout:
        issues = [line.strip() for line in result.stdout.split("\n") if line.strip()]

    return {
        "success": result.returncode == 0,
        "issues_found": len(issues),
        "issues": issues[:20],
        "tree_healthy": result.returncode == 0
    }


async def verify_requirements_files(_task_results: dict = None) -> Dict[str, Any]:
    """Verify requirements files exist and are valid."""
    req_files = list(project_root.glob("requirements*.txt"))
    pyproject = project_root / "pyproject.toml"

    results = {
        "requirements_files": [str(f.relative_to(project_root)) for f in req_files],
        "has_pyproject": pyproject.exists(),
        "issues": []
    }

    # Check pyproject.toml for dependencies section
    if pyproject.exists():
        content = pyproject.read_text()
        if "[project.dependencies]" in content or "dependencies" in content:
            results["pyproject_has_deps"] = True
        else:
            results["pyproject_has_deps"] = False
            results["issues"].append("pyproject.toml missing dependencies section")

    # Check each requirements file is parseable
    for req_file in req_files:
        try:
            content = req_file.read_text()
            lines = [l.strip() for l in content.split("\n") if l.strip() and not l.startswith("#")]
            results[f"{req_file.name}_entries"] = len(lines)
        except Exception as e:
            results["issues"].append(f"Error reading {req_file.name}: {e}")

    results["success"] = len(results["issues"]) == 0
    return results


def _extract_result(obj) -> dict:
    """Extract value from TaskResult or return dict directly."""
    if obj is None:
        return {}
    # If it's a TaskResult object, get its value attribute
    value = getattr(obj, "value", obj)
    # If value is still not a dict, try to get from the object itself
    if value is None:
        return {}
    return value if isinstance(value, dict) else {}


async def generate_dependency_report(task_results: dict = None, _task_results: dict = None) -> Dict[str, Any]:
    """Generate comprehensive dependency report."""
    # Handle both parameter naming conventions
    raw_results = task_results or _task_results or {}
    
    report = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "summary": {},
        "recommendations": []
    }

    # Aggregate results - extract from TaskResult objects
    outdated = _extract_result(raw_results.get("list_outdated"))
    security = _extract_result(raw_results.get("check_security"))
    tree = _extract_result(raw_results.get("check_tree"))
    reqs = _extract_result(raw_results.get("verify_requirements"))

    # Build summary
    report["summary"]["outdated_packages"] = outdated.get("outdated_count", 0)
    report["summary"]["security_issues"] = security.get("vulnerabilities_found", 0)
    report["summary"]["dependency_conflicts"] = tree.get("issues_found", 0)

    # Generate recommendations
    if outdated.get("outdated_count", 0) > 10:
        report["recommendations"].append("Consider updating outdated packages")

    if security.get("vulnerabilities_found", 0) > 0:
        report["recommendations"].append("URGENT: Security vulnerabilities detected - review and update affected packages")

    if not tree.get("tree_healthy", True):
        report["recommendations"].append("Resolve dependency conflicts before deployment")

    if not reqs.get("pyproject_has_deps", True):
        report["recommendations"].append("Migrate dependencies to pyproject.toml")

    # Calculate overall health
    issues = (
        outdated.get("outdated_count", 0) +
        security.get("vulnerabilities_found", 0) * 5 +  # Weight security higher
        tree.get("issues_found", 0) * 2
    )

    if issues == 0:
        report["overall_health"] = "excellent"
    elif issues < 10:
        report["overall_health"] = "good"
    elif issues < 25:
        report["overall_health"] = "fair"
    else:
        report["overall_health"] = "needs_attention"

    return {
        "success": True,
        "report": report
    }


async def main() -> int:
    """Run dependency check workflow."""
    setup_logging()
    parser = argparse.ArgumentParser(description="Check project dependencies")
    parser.add_argument("--update", action="store_true", help="Update outdated packages")
    parser.add_argument("--security-only", action="store_true", help="Only run security checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print_info("Checking project dependencies...")
    print()

    workflow = Workflow(
        name="dependency_check",
        timeout=600,
        fail_fast=False
    )

    if args.security_only:
        # Only security checks
        workflow.add_task(name="check_security", action=check_security_vulnerabilities, timeout=180)
    else:
        # Full dependency check
        workflow.add_task(name="list_outdated", action=list_outdated_packages, timeout=120)
        workflow.add_task(name="check_security", action=check_security_vulnerabilities, timeout=180)
        workflow.add_task(name="check_tree", action=check_dependency_tree, timeout=60)
        workflow.add_task(name="verify_requirements", action=verify_requirements_files, timeout=30)
        workflow.add_task(
            name="generate_report",
            action=generate_dependency_report,
            dependencies=["list_outdated", "check_security", "check_tree", "verify_requirements"],
            timeout=30
        )

    try:
        await workflow.run()
        summary = workflow.get_summary()

        print()
        print("=" * 50)
        print(f"Dependency Check {'Completed' if summary['success'] else 'Had Issues'}")
        print()

        # Print results
        for name, task in workflow.tasks.items():
            icon = "" if task.status.value == "completed" else ""
            print(f"  {icon} {name}")

            if task.result and args.verbose:
                result_data = task.result
                if isinstance(result_data, dict):
                    for key, value in result_data.items():
                        if key not in ("success", "error") and not isinstance(value, (list, dict)):
                            print(f"      {key}: {value}")

        # Print report summary if available
        report_task = workflow.tasks.get("generate_report")
        if report_task and report_task.result:
            report = report_task.result.get("report", {})
            if report:
                print()
                print("Summary:")
                for key, value in report.get("summary", {}).items():
                    print(f"  {key}: {value}")

                if report.get("recommendations"):
                    print()
                    print("Recommendations:")
                    for rec in report["recommendations"]:
                        print(f"  - {rec}")

                print()
                print(f"Overall Health: {report.get('overall_health', 'unknown')}")

        return 0 if summary["success"] else 1

    except Exception as e:
        print_error(f"Dependency check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
