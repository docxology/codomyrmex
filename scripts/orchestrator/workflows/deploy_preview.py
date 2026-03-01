#!/usr/bin/env python3
"""Deploy preview workflow.

Deploy a preview/staging environment:
1. Build the application
2. Run pre-deployment checks
3. Deploy to preview environment
4. Run smoke tests
5. Generate deployment report

Usage:
    python deploy_preview.py [--env ENV] [--skip-tests] [--dry-run]
"""

import argparse
import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator import Workflow, RetryPolicy
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_error


async def build_application(_task_results: dict = None) -> Dict[str, Any]:
    """Build the application for deployment."""
    result = subprocess.run(
        ["uv", "build"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=300
    )

    # Check for built artifacts
    dist_dir = project_root / "dist"
    artifacts = list(dist_dir.glob("*")) if dist_dir.exists() else []

    return {
        "success": result.returncode == 0,
        "artifacts": [f.name for f in artifacts],
        "build_output": result.stdout[:500] if result.stdout else ""
    }


async def run_pre_deployment_checks(_task_results: dict = None) -> Dict[str, Any]:
    """Run pre-deployment validation checks."""
    checks = {
        "lint": False,
        "types": False,
        "security": False
    }

    # Quick lint check
    lint_result = subprocess.run(
        ["uv", "run", "ruff", "check", "src/", "--select=E,F", "--quiet"],
        capture_output=True,
        cwd=project_root,
        timeout=60
    )
    checks["lint"] = lint_result.returncode == 0

    # Quick type check on critical modules
    type_result = subprocess.run(
        ["uv", "run", "mypy", "src/codomyrmex/orchestrator", "--ignore-missing-imports", "--no-error-summary"],
        capture_output=True,
        cwd=project_root,
        timeout=120
    )
    checks["types"] = type_result.returncode == 0

    # Quick security check
    security_result = subprocess.run(
        ["uv", "run", "bandit", "-r", "src/codomyrmex", "-ll", "-q"],
        capture_output=True,
        cwd=project_root,
        timeout=120
    )
    checks["security"] = security_result.returncode == 0

    all_passed = all(checks.values())

    return {
        "success": all_passed,
        "checks": checks,
        "message": "All pre-deployment checks passed" if all_passed else "Some checks failed"
    }


async def deploy_to_preview(task_results: dict = None, _task_results: dict = None, env: str = "preview", dry_run: bool = False) -> Dict[str, Any]:
    """Deploy to preview environment."""
    # Handle both naming conventions and TaskResult objects
    results = task_results or _task_results or {}
    
    # Get build artifacts - handle TaskResult objects
    build_result_obj = results.get("build")
    if build_result_obj is not None:
        # If it's a TaskResult, extract .value; if it's a dict, use directly
        build_result = getattr(build_result_obj, "value", build_result_obj) or {}
    else:
        build_result = {}
    
    artifacts = build_result.get("artifacts", []) if isinstance(build_result, dict) else []

    if not artifacts:
        return {
            "success": False,
            "error": "No build artifacts found"
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"Would deploy {artifacts} to {env}",
            "environment": env
        }

    # Simulate deployment (in real scenario, this would deploy to actual infrastructure)
    deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Example: deploy using pip install to a virtual environment
    deploy_cmd = ["echo", f"Deploying {artifacts[0]} to {env}"]

    result = subprocess.run(
        deploy_cmd,
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=300
    )

    return {
        "success": True,
        "deployment_id": deployment_id,
        "environment": env,
        "artifacts_deployed": artifacts,
        "timestamp": datetime.now().isoformat()
    }


async def run_smoke_tests(task_results: dict = None, _task_results: dict = None, skip: bool = False) -> Dict[str, Any]:
    """Run smoke tests against deployed preview."""
    if skip:
        return {
            "success": True,
            "skipped": True,
            "message": "Smoke tests skipped"
        }

    # Handle both naming conventions and TaskResult objects
    results = task_results or _task_results or {}
    deploy_obj = results.get("deploy")
    deployment = getattr(deploy_obj, "value", deploy_obj) if deploy_obj else {}
    deployment = deployment or {}
    
    if deployment.get("dry_run"):
        return {
            "success": True,
            "skipped": True,
            "message": "Smoke tests skipped for dry run"
        }

    # Run a quick subset of tests
    result = subprocess.run(
        ["uv", "run", "pytest", "src/codomyrmex/tests/unit", "-q", "--tb=no", "-x", "-k", "test_basic or test_init"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=120
    )

    # Parse test results
    passed = result.stdout.count(" passed")
    failed = result.stdout.count(" failed")

    return {
        "success": result.returncode == 0,
        "tests_passed": passed,
        "tests_failed": failed,
        "output": result.stdout[-300:] if result.stdout else ""
    }


def _extract_result(obj) -> dict:
    """Extract value from TaskResult or return dict directly."""
    if obj is None:
        return {}
    value = getattr(obj, "value", obj)
    return value if isinstance(value, dict) else {}


async def generate_deployment_report(task_results: dict = None, _task_results: dict = None) -> Dict[str, Any]:
    """Generate deployment report."""
    # Handle both naming conventions
    results = task_results or _task_results or {}
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "stages": {}
    }

    # Aggregate all stage results
    for stage_name, result_obj in results.items():
        result = _extract_result(result_obj)
        if isinstance(result, dict):
            report["stages"][stage_name] = {
                "success": result.get("success", False),
                "summary": _summarize_result(result)
            }
            if not result.get("success", True):
                report["status"] = "partial_failure"

    # Check for overall success
    all_success = all(
        _extract_result(r).get("success", False)
        for r in results.values()
    )
    report["status"] = "success" if all_success else "failure"

    # Add deployment details
    deploy_result = _extract_result(results.get("deploy"))
    report["deployment"] = {
        "id": deploy_result.get("deployment_id", "N/A"),
        "environment": deploy_result.get("environment", "unknown"),
        "dry_run": deploy_result.get("dry_run", False)
    }

    return {
        "success": True,
        "report": report
    }


def _summarize_result(result: Dict[str, Any]) -> str:
    """Create summary string from result."""
    if result.get("dry_run"):
        return "Dry run completed"
    if result.get("skipped"):
        return "Skipped"
    if result.get("error"):
        return f"Error: {result['error'][:50]}"
    if result.get("success"):
        return "Completed successfully"
    return "Failed"


async def main() -> int:
    """Run deployment workflow."""
    setup_logging()
    parser = argparse.ArgumentParser(description="Deploy to preview environment")
    parser.add_argument("--env", default="preview", help="Target environment")
    parser.add_argument("--skip-tests", action="store_true", help="Skip smoke tests")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without actual deployment")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print_info(f"Deploying to {args.env} environment...")
    if args.dry_run:
        print_info("(DRY RUN - no actual deployment)")
    print()

    workflow = Workflow(
        name="deploy_preview",
        timeout=1800,
        fail_fast=True
    )

    # Build
    workflow.add_task(
        name="build",
        action=build_application,
        timeout=300,
        retry_policy=RetryPolicy(max_attempts=2)
    )

    # Pre-deployment checks
    workflow.add_task(
        name="pre_checks",
        action=run_pre_deployment_checks,
        dependencies=["build"],
        timeout=300
    )

    # Deploy
    async def deploy_action(_task_results: dict = None) -> Dict[str, Any]:
        return await deploy_to_preview(_task_results, env=args.env, dry_run=args.dry_run)

    workflow.add_task(
        name="deploy",
        action=deploy_action,
        dependencies=["pre_checks"],
        timeout=300
    )

    # Smoke tests
    async def smoke_test_action(_task_results: dict = None) -> Dict[str, Any]:
        return await run_smoke_tests(_task_results, skip=args.skip_tests)

    workflow.add_task(
        name="smoke_tests",
        action=smoke_test_action,
        dependencies=["deploy"],
        timeout=180
    )

    # Report
    workflow.add_task(
        name="report",
        action=generate_deployment_report,
        dependencies=["build", "pre_checks", "deploy", "smoke_tests"],
        timeout=30
    )

    try:
        await workflow.run()
        summary = workflow.get_summary()

        print()
        print("=" * 60)
        print(f"Deployment {'Completed' if summary['success'] else 'Failed'}")
        print("=" * 60)

        # Print stage results
        for name, task in workflow.tasks.items():
            icon = "" if task.status.value == "completed" else ""
            result = task.result or {}

            if name == "build":
                artifacts = result.get("artifacts", [])
                print(f"  {icon} Build: {len(artifacts)} artifact(s)")
            elif name == "pre_checks":
                checks = result.get("checks", {})
                passed = sum(1 for v in checks.values() if v)
                print(f"  {icon} Pre-checks: {passed}/{len(checks)} passed")
            elif name == "deploy":
                env = result.get("environment", "unknown")
                deploy_id = result.get("deployment_id", "N/A")
                print(f"  {icon} Deploy: {env} ({deploy_id})")
            elif name == "smoke_tests":
                if result.get("skipped"):
                    print(f"  {icon} Smoke tests: skipped")
                else:
                    passed = result.get("tests_passed", 0)
                    print(f"  {icon} Smoke tests: {passed} passed")
            elif name == "report":
                continue

        # Print deployment summary
        report_task = workflow.tasks.get("report")
        if report_task and report_task.result:
            report = report_task.result.get("report", {})
            deployment = report.get("deployment", {})

            print()
            print(f"Deployment ID: {deployment.get('id', 'N/A')}")
            print(f"Environment:   {deployment.get('environment', 'unknown')}")
            print(f"Status:        {report.get('status', 'unknown')}")

        return 0 if summary["success"] else 1

    except Exception as e:
        print_error(f"Deployment failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
