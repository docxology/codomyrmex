#!/usr/bin/env python3
"""Code quality workflow.

Comprehensive code quality checks:
1. Run linting (ruff)
2. Run type checking (mypy)
3. Check code complexity
4. Run security analysis
5. Generate quality report

Usage:
    python code_quality.py [--fix] [--strict]
"""

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator import Workflow, RetryPolicy
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


async def run_ruff_lint(task_results: dict = None, fix: bool = False) -> Dict[str, Any]:
    """Run ruff linting."""
    cmd = ["uv", "run", "ruff", "check", "src/"]
    if fix:
        cmd.append("--fix")
    cmd.extend(["--output-format=concise", "--statistics"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=120
    )

    issues = result.stdout.count("\n") if result.stdout else 0
    fixed = 0
    if fix and "Fixed" in result.stdout:
        # Extract fixed count
        for line in result.stdout.split("\n"):
            if "Fixed" in line:
                try:
                    fixed = int(line.split()[1])
                except (IndexError, ValueError):
                    pass

    return {
        "success": result.returncode == 0,
        "issues_found": issues,
        "fixed": fixed,
        "tool": "ruff",
        "output": result.stdout[:2000] if result.stdout else ""
    }


async def run_mypy_check(task_results: dict = None, strict: bool = False) -> Dict[str, Any]:
    """Run mypy type checking."""
    cmd = ["uv", "run", "mypy", "src/codomyrmex", "--ignore-missing-imports"]
    if strict:
        cmd.append("--strict")
    cmd.append("--no-error-summary")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=180
    )

    errors = result.stdout.count("error:") if result.stdout else 0
    warnings = result.stdout.count("warning:") if result.stdout else 0

    return {
        "success": result.returncode == 0,
        "errors": errors,
        "warnings": warnings,
        "tool": "mypy",
        "output": result.stdout[:2000] if result.stdout else ""
    }


async def check_code_complexity(_task_results: dict = None) -> Dict[str, Any]:
    """Check code complexity using radon."""
    # Try radon for complexity analysis
    result = subprocess.run(
        ["uv", "run", "radon", "cc", "src/codomyrmex", "-a", "-s"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=120
    )

    # Parse complexity grades
    complexity = {
        "A": 0,  # Low complexity (1-5)
        "B": 0,  # Medium-low (6-10)
        "C": 0,  # Medium (11-20)
        "D": 0,  # Medium-high (21-30)
        "E": 0,  # High (31-40)
        "F": 0   # Very high (41+)
    }

    if result.stdout:
        for grade in complexity:
            complexity[grade] = result.stdout.count(f" {grade} ")

    # Calculate average if present
    avg_complexity = None
    for line in (result.stdout or "").split("\n"):
        if "Average complexity:" in line:
            try:
                avg_complexity = float(line.split(":")[-1].strip().split()[0])
            except (ValueError, IndexError):
                pass

    return {
        "success": True,
        "complexity_distribution": complexity,
        "average_complexity": avg_complexity,
        "high_complexity_count": complexity.get("D", 0) + complexity.get("E", 0) + complexity.get("F", 0),
        "tool": "radon",
        "available": result.returncode == 0
    }


async def run_security_scan(_task_results: dict = None) -> Dict[str, Any]:
    """Run security analysis using bandit."""
    result = subprocess.run(
        ["uv", "run", "bandit", "-r", "src/codomyrmex", "-f", "json", "-q"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=180
    )

    issues = {"high": 0, "medium": 0, "low": 0}
    results_list = []

    if result.stdout:
        try:
            import json
            data = json.loads(result.stdout)
            for issue in data.get("results", []):
                severity = issue.get("issue_severity", "LOW").lower()
                issues[severity] = issues.get(severity, 0) + 1
                results_list.append({
                    "file": issue.get("filename", ""),
                    "line": issue.get("line_number", 0),
                    "severity": severity,
                    "issue": issue.get("issue_text", "")[:100]
                })
        except Exception:
            pass

    return {
        "success": result.returncode in (0, 1),  # bandit returns 1 if issues found
        "high_severity": issues["high"],
        "medium_severity": issues["medium"],
        "low_severity": issues["low"],
        "total_issues": sum(issues.values()),
        "top_issues": results_list[:5],
        "tool": "bandit",
        "available": "error" not in result.stderr.lower() if result.stderr else True
    }


async def run_docstring_coverage(_task_results: dict = None) -> Dict[str, Any]:
    """Check docstring coverage using interrogate."""
    result = subprocess.run(
        ["uv", "run", "interrogate", "src/codomyrmex", "-v", "--fail-under=0"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=120
    )

    coverage = None
    if result.stdout:
        for line in result.stdout.split("\n"):
            if "%" in line and "TOTAL" in line:
                try:
                    # Extract percentage
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            coverage = float(part.replace("%", ""))
                            break
                except (ValueError, IndexError):
                    pass

    return {
        "success": True,
        "coverage_percent": coverage,
        "tool": "interrogate",
        "available": result.returncode in (0, 1, 2)
    }


async def generate_quality_report(task_results: dict) -> Dict[str, Any]:
    """Generate comprehensive quality report."""
    import datetime

    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "project": "codomyrmex",
        "checks": {},
        "overall_score": 100,
        "recommendations": []
    }

    # Process each check result
    lint_result = task_results.get("lint", {})
    type_result = task_results.get("typecheck", {})
    complexity_result = task_results.get("complexity", {})
    security_result = task_results.get("security", {})
    docstring_result = task_results.get("docstrings", {})

    # Lint check
    report["checks"]["lint"] = {
        "tool": "ruff",
        "issues": lint_result.get("issues_found", 0),
        "passed": lint_result.get("success", False)
    }

    # Type check
    report["checks"]["types"] = {
        "tool": "mypy",
        "errors": type_result.get("errors", 0),
        "warnings": type_result.get("warnings", 0),
        "passed": type_result.get("success", False)
    }

    # Complexity
    report["checks"]["complexity"] = {
        "tool": "radon",
        "average": complexity_result.get("average_complexity"),
        "high_complexity_functions": complexity_result.get("high_complexity_count", 0)
    }

    # Security
    report["checks"]["security"] = {
        "tool": "bandit",
        "high_severity": security_result.get("high_severity", 0),
        "medium_severity": security_result.get("medium_severity", 0),
        "low_severity": security_result.get("low_severity", 0)
    }

    # Docstrings
    report["checks"]["docstrings"] = {
        "tool": "interrogate",
        "coverage": docstring_result.get("coverage_percent")
    }

    # Calculate overall score (out of 100)
    score = 100

    # Deduct for lint issues
    lint_issues = lint_result.get("issues_found", 0)
    score -= min(lint_issues * 0.5, 15)

    # Deduct for type errors
    type_errors = type_result.get("errors", 0)
    score -= min(type_errors * 1, 20)

    # Deduct for security issues
    high_security = security_result.get("high_severity", 0)
    medium_security = security_result.get("medium_severity", 0)
    score -= (high_security * 10) + (medium_security * 3)

    # Deduct for complexity
    high_complexity = complexity_result.get("high_complexity_count", 0)
    score -= min(high_complexity * 2, 10)

    # Deduct for low docstring coverage
    doc_coverage = docstring_result.get("coverage_percent")
    if doc_coverage is not None and doc_coverage < 50:
        score -= (50 - doc_coverage) * 0.2

    report["overall_score"] = max(0, min(100, score))

    # Generate recommendations
    if lint_issues > 20:
        report["recommendations"].append("Run 'ruff check --fix' to auto-fix linting issues")

    if type_errors > 10:
        report["recommendations"].append("Address type annotation issues for better code safety")

    if high_security > 0:
        report["recommendations"].append("URGENT: Review and fix high-severity security issues")

    if high_complexity > 5:
        report["recommendations"].append("Refactor complex functions to improve maintainability")

    if doc_coverage is not None and doc_coverage < 60:
        report["recommendations"].append("Improve docstring coverage for better documentation")

    # Determine grade
    if report["overall_score"] >= 90:
        report["grade"] = "A"
    elif report["overall_score"] >= 80:
        report["grade"] = "B"
    elif report["overall_score"] >= 70:
        report["grade"] = "C"
    elif report["overall_score"] >= 60:
        report["grade"] = "D"
    else:
        report["grade"] = "F"

    return {
        "success": True,
        "report": report
    }


async def main():
    """Run code quality workflow."""
    parser = argparse.ArgumentParser(description="Run code quality checks")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    parser.add_argument("--strict", action="store_true", help="Use strict mode for type checking")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("Running code quality checks...")
    print()

    workflow = Workflow(
        name="code_quality",
        timeout=900,  # 15 minutes total
        fail_fast=False
    )

    # Add all quality checks (can run in parallel)
    workflow.add_task(
        name="lint",
        action=lambda _tr=None: asyncio.get_event_loop().run_in_executor(
            None, lambda: asyncio.run(run_ruff_lint(fix=args.fix))
        ),
        timeout=120
    )
    workflow.add_task(
        name="typecheck",
        action=lambda _tr=None: asyncio.get_event_loop().run_in_executor(
            None, lambda: asyncio.run(run_mypy_check(strict=args.strict))
        ),
        timeout=180
    )
    workflow.add_task(
        name="complexity",
        action=check_code_complexity,
        timeout=120
    )
    workflow.add_task(
        name="security",
        action=run_security_scan,
        timeout=180
    )
    workflow.add_task(
        name="docstrings",
        action=run_docstring_coverage,
        timeout=120
    )

    # Generate report after all checks
    workflow.add_task(
        name="report",
        action=generate_quality_report,
        dependencies=["lint", "typecheck", "complexity", "security", "docstrings"],
        timeout=30
    )

    try:
        await workflow.run()
        summary = workflow.get_summary()

        print()
        print("=" * 60)
        print("Code Quality Report")
        print("=" * 60)

        # Print individual check results
        for name, task in workflow.tasks.items():
            if name == "report":
                continue

            icon = "" if task.status.value == "completed" else ""
            result = task.result or {}

            if name == "lint":
                issues = result.get("issues_found", "?")
                fixed = result.get("fixed", 0)
                print(f"  {icon} Linting:     {issues} issues" + (f" ({fixed} fixed)" if fixed else ""))
            elif name == "typecheck":
                errors = result.get("errors", "?")
                warnings = result.get("warnings", 0)
                print(f"  {icon} Type Check:  {errors} errors, {warnings} warnings")
            elif name == "complexity":
                avg = result.get("average_complexity", "?")
                high = result.get("high_complexity_count", 0)
                print(f"  {icon} Complexity:  avg {avg}, {high} high-complexity functions")
            elif name == "security":
                high = result.get("high_severity", 0)
                med = result.get("medium_severity", 0)
                low = result.get("low_severity", 0)
                print(f"  {icon} Security:    {high} high, {med} medium, {low} low severity")
            elif name == "docstrings":
                coverage = result.get("coverage_percent", "?")
                print(f"  {icon} Docstrings:  {coverage}% coverage")

        # Print overall report
        report_task = workflow.tasks.get("report")
        if report_task and report_task.result:
            report = report_task.result.get("report", {})

            print()
            print("-" * 60)
            score = report.get("overall_score", 0)
            grade = report.get("grade", "?")
            print(f"Overall Score: {score:.0f}/100  (Grade: {grade})")

            if report.get("recommendations"):
                print()
                print("Recommendations:")
                for rec in report["recommendations"]:
                    print(f"    {rec}")

        print()
        return 0 if summary["success"] else 1

    except Exception as e:
        print(f" Code quality check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
