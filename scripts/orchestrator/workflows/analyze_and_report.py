#!/usr/bin/env python3
"""Workflow: Analyze codebase and generate comprehensive report.

This workflow:
1. Runs static analysis on the codebase
2. Analyzes dependencies and checks for issues
3. Runs tests with coverage
4. Generates a comprehensive HTML report

Usage:
    python analyze_and_report.py [--path PATH] [--output OUTPUT]
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator import Workflow, RetryPolicy, TaskResult
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


async def run_static_analysis(path: Path = None, _task_results: dict = None) -> dict:
    """Run static analysis on the codebase."""
    from codomyrmex.static_analysis import analyze_code_quality

    target_path = path or project_root / "src"
    logger.info(f"Running static analysis on {target_path}")

    try:
        result = analyze_code_quality(str(target_path))
        return {
            "success": True,
            "metrics": result,
            "issues_count": len(result.get("issues", [])) if isinstance(result, dict) else 0
        }
    except Exception as e:
        logger.error(f"Static analysis failed: {e}")
        return {"success": False, "error": str(e)}


async def analyze_dependencies(_task_results: dict = None) -> dict:
    """Analyze project dependencies."""
    from codomyrmex.tools.dependency_analyzer import DependencyAnalyzer

    logger.info("Analyzing dependencies")

    try:
        analyzer = DependencyAnalyzer(project_root)
        result = analyzer.analyze()
        return {
            "success": True,
            "modules": len(result.get("modules", [])),
            "circular_dependencies": result.get("circular_dependencies", []),
            "violations": result.get("violations", [])
        }
    except Exception as e:
        logger.error(f"Dependency analysis failed: {e}")
        return {"success": False, "error": str(e)}


async def run_tests(_task_results: dict = None) -> dict:
    """Run tests with coverage."""
    import subprocess

    logger.info("Running tests with coverage")

    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "src/codomyrmex/tests/unit",
             "--cov=src/codomyrmex", "-q", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=project_root
        )

        # Parse coverage from output
        coverage = 0.0
        for line in result.stdout.split("\n"):
            if "TOTAL" in line and "%" in line:
                parts = line.split()
                for part in parts:
                    if part.endswith("%"):
                        try:
                            coverage = float(part.rstrip("%"))
                        except ValueError:
                            pass

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "coverage_percent": coverage,
            "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
        }
    except Exception as e:
        logger.error(f"Tests failed: {e}")
        return {"success": False, "error": str(e)}


async def generate_report(output_path: Path = None, _task_results: dict = None) -> dict:
    """Generate comprehensive HTML report from analysis results."""
    output = output_path or project_root / "output" / "analysis_report.html"
    output.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating report to {output}")

    # Get results from previous tasks
    static_result = _task_results.get("static_analysis", TaskResult(success=False)).value or {}
    deps_result = _task_results.get("dependencies", TaskResult(success=False)).value or {}
    test_result = _task_results.get("tests", TaskResult(success=False)).value or {}

    # Generate HTML report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Codomyrmex Analysis Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 16px 0;
                 box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .success {{ color: #22c55e; }} .error {{ color: #ef4444; }}
        h1 {{ color: #1e293b; }} h2 {{ color: #475569; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        .metric {{ display: inline-block; padding: 8px 16px; background: #f1f5f9; border-radius: 4px; margin: 4px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        pre {{ background: #1e293b; color: #e2e8f0; padding: 16px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>🐜 Codomyrmex Analysis Report</h1>
    <p>Generated: {timestamp}</p>

    <div class="card">
        <h2>📊 Static Analysis</h2>
        <p class="{'success' if static_result.get('success') else 'error'}">
            Status: {'✅ Passed' if static_result.get('success') else '❌ Failed'}
        </p>
        <div class="metric">
            <div>Issues Found</div>
            <div class="metric-value">{static_result.get('issues_count', 'N/A')}</div>
        </div>
    </div>

    <div class="card">
        <h2>🔗 Dependencies</h2>
        <p class="{'success' if deps_result.get('success') else 'error'}">
            Status: {'✅ Analyzed' if deps_result.get('success') else '❌ Failed'}
        </p>
        <div class="metric">
            <div>Modules</div>
            <div class="metric-value">{deps_result.get('modules', 'N/A')}</div>
        </div>
        <div class="metric">
            <div>Circular Deps</div>
            <div class="metric-value">{len(deps_result.get('circular_dependencies', []))}</div>
        </div>
        <div class="metric">
            <div>Violations</div>
            <div class="metric-value">{len(deps_result.get('violations', []))}</div>
        </div>
    </div>

    <div class="card">
        <h2>🧪 Tests</h2>
        <p class="{'success' if test_result.get('success') else 'error'}">
            Status: {'✅ Passed' if test_result.get('success') else '❌ Failed'}
        </p>
        <div class="metric">
            <div>Coverage</div>
            <div class="metric-value">{test_result.get('coverage_percent', 0):.1f}%</div>
        </div>
    </div>

    <div class="card">
        <h2>📋 Summary</h2>
        <ul>
            <li>Static Analysis: {'✅' if static_result.get('success') else '❌'}</li>
            <li>Dependencies: {'✅' if deps_result.get('success') else '❌'}</li>
            <li>Tests: {'✅' if test_result.get('success') else '❌'}</li>
        </ul>
    </div>
</body>
</html>
"""

    with open(output, "w") as f:
        f.write(html)

    return {
        "success": True,
        "output_file": str(output),
        "sections": ["static_analysis", "dependencies", "tests"]
    }


async def main() -> int:
    """Run the analysis workflow."""
    parser = argparse.ArgumentParser(description="Analyze codebase and generate report")
    parser.add_argument("--path", type=Path, help="Path to analyze")
    parser.add_argument("--output", type=Path, help="Output report path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Progress callback
    def on_progress(task: str, status: str, details: dict):
        if args.verbose:
            print(f"  [{status.upper()}] {task}")

    # Create workflow
    workflow = Workflow(
        name="analyze_and_report",
        timeout=600,  # 10 minutes total
        fail_fast=False,  # Continue even if some tasks fail
        progress_callback=on_progress
    )

    # Add tasks with retry for flaky operations
    workflow.add_task(
        name="static_analysis",
        action=run_static_analysis,
        kwargs={"path": args.path},
        timeout=120,
        retry_policy=RetryPolicy(max_attempts=2)
    )

    workflow.add_task(
        name="dependencies",
        action=analyze_dependencies,
        timeout=60
    )

    workflow.add_task(
        name="tests",
        action=run_tests,
        timeout=300,
        retry_policy=RetryPolicy(max_attempts=2)
    )

    # Report depends on all analysis tasks
    workflow.add_task(
        name="report",
        action=generate_report,
        dependencies=["static_analysis", "dependencies", "tests"],
        kwargs={"output_path": args.output},
        timeout=30
    )

    print("🔍 Running analysis workflow...")
    print()

    try:
        results = await workflow.run()
        summary = workflow.get_summary()

        print()
        print("=" * 50)
        print(f"Workflow {'completed' if summary['success'] else 'completed with errors'}")
        print(f"  Tasks: {summary['completed']}/{summary['total_tasks']} completed")
        print(f"  Time:  {summary['elapsed_time']:.1f}s")

        if summary["failed"] > 0:
            print(f"  Failed: {summary['failed']}")

        # Show report location
        report_result = workflow.get_task_result("report")
        if report_result and report_result.success:
            print(f"\n📄 Report: {report_result.value.get('output_file', 'N/A')}")

        return 0 if summary["success"] else 1

    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        logger.exception("Workflow error")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
