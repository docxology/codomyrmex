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

# Constants
SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    "venv", 
    ".venv", 
    "node_modules",
    "build",
    "dist",
    "egg-info",
    "output",
    "_templates",
    "module_template",
    "examples",
    "tests",
    ".cursor",
    ".DS_Store"
}

SKIP_PATTERNS = {
    "__init__.py",
    "conftest.py",
    "_orchestrator_utils.py",
    "run_all_scripts.py"
}

def load_config(scripts_dir: Path) -> Dict[str, Any]:
    """Load script configuration."""
    config_path = scripts_dir / "scripts_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            pass
    return {"default": {}, "scripts": {}}

def get_script_config(script_path: Path, scripts_dir: Path, global_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get configuration for a specific script."""
    rel_path = str(script_path.relative_to(scripts_dir))
    
    # Try alternate path separator for windows compatibility/robustness if needed, 
    # but here just ensure we match the json keys
    
    config = global_config.get("default", {}).copy()
    
    # Direct match
    if rel_path in global_config.get("scripts", {}):
        config.update(global_config["scripts"][rel_path])
        return config
        
    # Check if any key in config ends with the script name or relative path
    # This handles "tools/audit_methods.py" key matching "scripts/tools/audit_methods.py" if needed
    for key, val in global_config.get("scripts", {}).items():
        if rel_path.endswith(key):
            config.update(val)
            return config
            
    return config

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
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run a single script and capture output.
    
    Args:
        script_path: Path to the script
        timeout: Timeout in seconds
        env: Environment variables
        cwd: Working directory
        config: Script configuration
        
    Returns:
        Execution result dictionary
    """
    script_config = config or {}
    timeout = script_config.get("timeout", timeout)
    allowed_exit_codes = script_config.get("allowed_exit_codes", [0])
    
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
    
    # Merge env from config
    if "env" in script_config:
        run_env.update(script_config["env"])
    
    # Add project src to PYTHONPATH
    project_root = script_path.parent.parent.parent
    src_path = project_root / "src"
    if src_path.exists():
        pythonpath = run_env.get("PYTHONPATH", "")
        # Add both src and scripts root to path
        scripts_root = project_root / "scripts"
        new_path = f"{src_path}:{scripts_root}"
        run_env["PYTHONPATH"] = f"{new_path}:{pythonpath}" if pythonpath else new_path
    
    try:
        process = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or script_path.parent,
            env=run_env,
            stdin=subprocess.DEVNULL,
        )
        
        result["exit_code"] = process.returncode
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["status"] = "passed" if process.returncode in allowed_exit_codes else "failed"
        
        if result["status"] == "passed" and process.returncode != 0:
             # Annotate passed (non-zero)
             result["stdout"] += f"\n[INFO] Script exited with code {process.returncode} (ALLOWED)"
        
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


def generate_script_documentation(scripts_dir: Path, output_file: Path) -> bool:
    """
    Generate Markdown documentation for all discovered scripts.

    Args:
        scripts_dir: Directory containing scripts
        output_file: Path to write Markdown output

    Returns:
        True if generation was successful
    """
    scripts = discover_scripts(scripts_dir)
    total_scripts = len(scripts)
    
    print_section("Generating Script Documentation")
    print_info(f"Target: {output_file}")
    print_info(f"Scripts to process: {total_scripts}")
    
    with open(output_file, "w") as f:
        # Write Header
        f.write("# Codomyrmex Script Reference\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This document contains auto-generated documentation for all scripts in the `scripts/` directory.\n\n")
        
        # Table of Contents
        f.write("## Table of Contents\n\n")
        categories = {}
        for script in scripts:
            rel_path = script.relative_to(scripts_dir)
            category = rel_path.parts[0] if len(rel_path.parts) > 1 else "_root"
            if category not in categories:
                categories[category] = []
            categories[category].append(script)
            
        for category in sorted(categories.keys()):
            f.write(f"- [{category}](#{category.lower()})\n")
            
        f.write("\n---\n\n")
        
        success_count = 0
        fail_count = 0
        
        # Process Categories
        for category in sorted(categories.keys()):
            f.write(f"## {category}\n\n")
            
            for script in sorted(categories[category]):
                rel_path = script.relative_to(scripts_dir)
                script_name = script.name
                
                print(f"Processing: {rel_path}...", end="", flush=True)
                
                # Get Help Text
                try:
                    # Run with --help
                    # Using same environment as main execution
                    env = os.environ.copy()
                    # Add project src to PYTHONPATH
                    project_root = script.parent.parent.parent
                    src_path = project_root / "src"
                    if src_path.exists():
                        pythonpath = env.get("PYTHONPATH", "")
                        env["PYTHONPATH"] = f"{src_path}:{pythonpath}" if pythonpath else str(src_path)
                    
                    cmd = [sys.executable, str(script), "--help"]
                    
                    process = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5,
                        env=env,
                        cwd=script.parent,
                        stdin=subprocess.DEVNULL
                    )
                    
                    if process.returncode == 0:
                        help_text = process.stdout
                        success_count += 1
                        print(" ✅")
                    else:
                        help_text = f"Failed to get help text (Exit Code: {process.returncode})\n\nStderr:\n{process.stderr}"
                        fail_count += 1
                        print(" ❌")
                        
                except subprocess.TimeoutExpired:
                    help_text = "Timed out getting help text"
                    fail_count += 1
                    print(" ⏰")
                except Exception as e:
                    help_text = f"Error generating docs: {str(e)}"
                    fail_count += 1
                    print(" 💥")
                
                # Write Entry
                f.write(f"### {script_name}\n\n")
                f.write(f"**Path**: `{rel_path}`\n\n")
                f.write("```text\n")
                f.write(help_text.strip())
                f.write("\n```\n\n")
                
            f.write("---\n\n")
            
    print_section("Documentation Generation Complete")
    print_info(f"Successful: {success_count}")
    print_info(f"Failed: {fail_count}")
    print_success(f"Documentation written to {output_file}")
    
    return True


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
  %(prog)s --generate-docs docs/scripts.md # Generate Markdown documentation
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
    
    parser.add_argument(
        "--generate-docs",
        help="Generate Markdown documentation to this file path",
    )
    
    args = parser.parse_args()
    
    # Setup paths
    scripts_dir = Path(__file__).parent.resolve()
    
    # Load configuration
    config = load_config(scripts_dir)
    
    # Handle Doc Generation
    if args.generate_docs:
        output_file = Path(args.generate_docs).resolve()
        success = generate_script_documentation(scripts_dir, output_file)
        return 0 if success else 1
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
        
        # Show skip status from config
        skipped_count = 0
        for script in scripts:
            script_config = get_script_config(script, scripts_dir, config)
            if script_config.get("skip"):
                 print(f"⚠️  WOULD SKIP: {script.name} ({script_config.get('skip_reason', 'Configured to skip')})")
                 skipped_count += 1
        
        print(f"ℹ️  Skipped by config: {skipped_count}")
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
            
        # Get script config
        script_config = get_script_config(script, scripts_dir, config)
        
        # Check if skipped
        if script_config.get("skip"):
            # Add skipped result
            results.append({
                "script": str(script),
                "name": script.name,
                "subdirectory": script.parent.name,
                "status": "skipped",
                "execution_time": 0.0,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "error": script_config.get('skip_reason', 'Configured to skip'),
                "stdout": "",
                "stderr": "", 
                "exit_code": None
            })
            continue
        
        result = run_script(
            script,
            timeout=args.timeout,
            cwd=scripts_dir.parent,  # Run from project root
            config=script_config
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
