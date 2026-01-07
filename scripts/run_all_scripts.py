#!/usr/bin/env python3
"""
Master Script Orchestrator

Run and log all scripts in the scripts directory with comprehensive reporting.
Discovers Python scripts in subdirectories, executes them, and generates
execution reports with logs.

Usage:
    python run_all_scripts.py [--dry-run] [--timeout SECONDS] [--filter PATTERN]
    python run_all_scripts.py --subdirs documentation testing
    python run_all_scripts.py --verbose --output-dir /path/to/logs
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from _orchestrator_utils import (
        ProgressReporter,
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        print_warning,
        print_with_color,
    )
except ImportError:
    # Fallback if utilities not available
    class ProgressReporter:
        def __init__(self, *args, **kwargs): pass
        def update(self, *args, **kwargs): pass
        def complete(self, *args, **kwargs): pass
    
    def format_output(data, **kwargs): return json.dumps(data, indent=2)
    def print_error(msg, **kwargs): print(f"❌ {msg}")
    def print_info(msg): print(f"ℹ️  {msg}")
    def print_section(title, **kwargs): print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")
    def print_success(msg, **kwargs): print(f"✅ {msg}")
    def print_warning(msg, **kwargs): print(f"⚠️  {msg}")
    def print_with_color(msg, color=None, **kwargs): print(msg)

# Directories to skip when discovering scripts
SKIP_DIRS = {
    '__pycache__',
    '.git',
    '.cursor',
    'node_modules',
    '.DS_Store',
    'tests',  # Skip test subdirectories within script folders
    'examples',  # Skip examples subdirectories (they're not orchestration scripts)
}

# Script patterns to skip
SKIP_PATTERNS = {
    '__init__.py',
    'conftest.py',
    '_orchestrator_utils.py',  # Shared utilities, not runnable
}


def discover_scripts(
    scripts_dir: Path,
    subdirs: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    max_depth: int = 2,
) -> List[Path]:
    """
    Discover all Python scripts in the scripts directory.
    
    Args:
        scripts_dir: Base scripts directory
        subdirs: Optional list of subdirectory names to filter
        pattern: Optional glob pattern to filter script names
        max_depth: Maximum directory depth to search
        
    Returns:
        List of script paths
    """
    scripts = []
    
    # Get subdirectories to search
    if subdirs:
        search_dirs = [scripts_dir / subdir for subdir in subdirs if (scripts_dir / subdir).is_dir()]
    else:
        search_dirs = [d for d in scripts_dir.iterdir() if d.is_dir() and d.name not in SKIP_DIRS]
    
    for subdir in search_dirs:
        if subdir.name in SKIP_DIRS:
            continue
            
        # Find Python files
        for py_file in subdir.rglob("*.py"):
            # Check depth
            relative = py_file.relative_to(scripts_dir)
            if len(relative.parts) > max_depth + 1:  # +1 for the file itself
                continue
                
            # Skip patterns
            if py_file.name in SKIP_PATTERNS:
                continue
                
            # Check if parent directory should be skipped
            if any(part in SKIP_DIRS for part in relative.parts[:-1]):
                continue
                
            # Apply pattern filter if specified
            if pattern and pattern not in py_file.name:
                continue
                
            scripts.append(py_file)
    
    return sorted(scripts)


def run_script(
    script_path: Path,
    timeout: int = 60,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run a single script and capture output.
    
    Args:
        script_path: Path to the script
        timeout: Timeout in seconds
        env: Environment variables
        cwd: Working directory
        
    Returns:
        Execution result dictionary
    """
    result = {
        "script": str(script_path),
        "name": script_path.name,
        "subdirectory": script_path.parent.name,
        "start_time": datetime.now().isoformat(),
        "status": "unknown",
        "exit_code": None,
        "execution_time": 0.0,
        "stdout": "",
        "stderr": "",
        "error": None,
    }
    
    start_time = time.time()
    
    # Prepare environment
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    
    # Add project src to PYTHONPATH
    project_root = script_path.parent.parent.parent
    src_path = project_root / "src"
    if src_path.exists():
        pythonpath = run_env.get("PYTHONPATH", "")
        run_env["PYTHONPATH"] = f"{src_path}:{pythonpath}" if pythonpath else str(src_path)
    
    try:
        process = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or script_path.parent,
            env=run_env,
        )
        
        result["exit_code"] = process.returncode
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["status"] = "passed" if process.returncode == 0 else "failed"
        
    except subprocess.TimeoutExpired as e:
        result["status"] = "timeout"
        result["error"] = f"Script timed out after {timeout}s"
        result["stdout"] = e.stdout if e.stdout else ""
        result["stderr"] = e.stderr if e.stderr else ""
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    result["execution_time"] = time.time() - start_time
    result["end_time"] = datetime.now().isoformat()
    
    return result


def save_log(
    result: Dict[str, Any],
    output_dir: Path,
    run_id: str,
) -> Path:
    """Save individual script log."""
    log_dir = output_dir / run_id / result["subdirectory"]
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{result['name']}.log"
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Script: {result['script']}\n")
        f.write(f"Status: {result['status']}\n")
        f.write(f"Exit Code: {result['exit_code']}\n")
        f.write(f"Execution Time: {result['execution_time']:.2f}s\n")
        f.write(f"Start: {result['start_time']}\n")
        f.write(f"End: {result.get('end_time', 'N/A')}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("STDOUT:\n")
        f.write("=" * 60 + "\n")
        f.write(result["stdout"] or "(no output)\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("STDERR:\n")
        f.write("=" * 60 + "\n")
        f.write(result["stderr"] or "(no errors)\n")
        
        if result["error"]:
            f.write("\n" + "=" * 60 + "\n")
            f.write("ERROR:\n")
            f.write("=" * 60 + "\n")
            f.write(result["error"] + "\n")
    
    return log_file


def generate_report(
    results: List[Dict[str, Any]],
    output_dir: Path,
    run_id: str,
) -> Dict[str, Any]:
    """Generate summary report."""
    summary = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "total_scripts": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "timeout": sum(1 for r in results if r["status"] == "timeout"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
        "total_execution_time": sum(r["execution_time"] for r in results),
        "by_subdirectory": {},
        "results": results,
    }
    
    # Group by subdirectory
    for result in results:
        subdir = result["subdirectory"]
        if subdir not in summary["by_subdirectory"]:
            summary["by_subdirectory"][subdir] = {
                "total": 0,
                "passed": 0,
                "failed": 0,
            }
        summary["by_subdirectory"][subdir]["total"] += 1
        if result["status"] == "passed":
            summary["by_subdirectory"][subdir]["passed"] += 1
        else:
            summary["by_subdirectory"][subdir]["failed"] += 1
    
    # Save JSON report
    report_dir = output_dir / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "summary.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        # Don't include full stdout/stderr in JSON summary
        summary_clean = summary.copy()
        summary_clean["results"] = [
            {k: v for k, v in r.items() if k not in ("stdout", "stderr")}
            for r in results
        ]
        json.dump(summary_clean, f, indent=2)
    
    return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run and log all scripts in the scripts directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dry-run                    # List scripts without running
  %(prog)s --timeout 30                 # Run with 30s timeout per script
  %(prog)s --subdirs documentation      # Run only documentation scripts
  %(prog)s --filter audit               # Run scripts containing 'audit'
  %(prog)s --verbose                    # Show detailed output
        """,
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="List scripts without executing them",
    )
    
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=60,
        help="Timeout per script in seconds (default: 60)",
    )
    
    parser.add_argument(
        "--subdirs", "-s",
        nargs="+",
        help="Subdirectories to run scripts from",
    )
    
    parser.add_argument(
        "--filter", "-f",
        help="Filter scripts by name pattern",
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path(__file__).parent.parent / "output" / "script_logs",
        help="Output directory for logs",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output",
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum directory depth to search (default: 2)",
    )
    
    args = parser.parse_args()
    
    # Setup paths
    scripts_dir = Path(__file__).parent
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_section("SCRIPT ORCHESTRATOR")
    print_info(f"Scripts directory: {scripts_dir}")
    print_info(f"Run ID: {run_id}")
    
    # Discover scripts
    print_section("Discovering Scripts", separator="-")
    scripts = discover_scripts(
        scripts_dir,
        subdirs=args.subdirs,
        pattern=args.filter,
        max_depth=args.max_depth,
    )
    
    print_info(f"Found {len(scripts)} scripts")
    
    if not scripts:
        print_warning("No scripts found matching criteria")
        return 0
    
    # Group by subdirectory for display
    by_subdir: Dict[str, List[Path]] = {}
    for script in scripts:
        subdir = script.parent.name
        if subdir not in by_subdir:
            by_subdir[subdir] = []
        by_subdir[subdir].append(script)
    
    for subdir, subdir_scripts in sorted(by_subdir.items()):
        print(f"\n  {subdir}/ ({len(subdir_scripts)} scripts)")
        if args.verbose or args.dry_run:
            for script in subdir_scripts[:10]:  # Show first 10
                print(f"    - {script.name}")
            if len(subdir_scripts) > 10:
                print(f"    ... and {len(subdir_scripts) - 10} more")
    
    if args.dry_run:
        print_section("DRY RUN MODE", separator="=")
        print_info("Scripts would be executed in the order shown above")
        print_info(f"Total: {len(scripts)} scripts")
        return 0
    
    # Execute scripts
    print_section("Executing Scripts", separator="-")
    print_info(f"Timeout per script: {args.timeout}s")
    print()
    
    results = []
    progress = ProgressReporter(total=len(scripts), prefix="Progress")
    
    for i, script in enumerate(scripts, 1):
        relative_path = script.relative_to(scripts_dir)
        progress.update(message=f"Running {relative_path}")
        
        if args.verbose:
            print(f"\n[{i}/{len(scripts)}] Running: {relative_path}")
        
        result = run_script(
            script,
            timeout=args.timeout,
            cwd=scripts_dir.parent,  # Run from project root
        )
        
        # Save individual log
        log_file = save_log(result, args.output_dir, run_id)
        result["log_file"] = str(log_file)
        
        results.append(result)
        
        # Show status
        if result["status"] == "passed":
            if args.verbose:
                print_success(f"  {result['name']} ({result['execution_time']:.1f}s)")
        elif result["status"] == "failed":
            print_error(f"  {result['name']} (exit code {result['exit_code']})")
        elif result["status"] == "timeout":
            print_warning(f"  {result['name']} (timeout after {args.timeout}s)")
        else:
            print_error(f"  {result['name']} ({result['error']})")
    
    progress.complete("Done")
    
    # Generate summary report
    print_section("Summary Report", separator="=")
    summary = generate_report(results, args.output_dir, run_id)
    
    print(f"\nTotal Scripts: {summary['total_scripts']}")
    print_with_color(f"  Passed:  {summary['passed']}", "green")
    print_with_color(f"  Failed:  {summary['failed']}", "red" if summary['failed'] > 0 else "default")
    print_with_color(f"  Timeout: {summary['timeout']}", "yellow" if summary['timeout'] > 0 else "default")
    print_with_color(f"  Error:   {summary['error']}", "red" if summary['error'] > 0 else "default")
    print(f"\nTotal Execution Time: {summary['total_execution_time']:.1f}s")
    
    # By subdirectory breakdown
    print("\nBy Subdirectory:")
    for subdir, stats in sorted(summary["by_subdirectory"].items()):
        status = "✅" if stats["failed"] == 0 else "❌"
        print(f"  {status} {subdir}: {stats['passed']}/{stats['total']} passed")
    
    print(f"\nLogs saved to: {args.output_dir / run_id}")
    print(f"Summary report: {args.output_dir / run_id / 'summary.json'}")
    
    # Show failed scripts
    failed = [r for r in results if r["status"] not in ("passed", "skipped")]
    if failed:
        print_section("Failed Scripts", separator="-")
        for r in failed:
            print(f"  ❌ {r['subdirectory']}/{r['name']}")
            if r["error"]:
                print(f"     Error: {r['error']}")
            elif r["stderr"]:
                # Show first line of stderr
                first_line = r["stderr"].strip().split("\n")[0][:100]
                print(f"     {first_line}")
    
    # Return non-zero if any failed
    return 1 if summary["failed"] + summary["error"] + summary["timeout"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
