from codomyrmex.logging_monitoring import get_logger
"""Orchestrator Core.

Main entry point and utility functions.

This module provides core functionality including:
- 1 functions: main
- 0 classes: 

Usage:
    from core import FunctionName, ClassName
    # Example usage here

Main entry point and execution loop.
"""

logger = get_logger(__name__)

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from codomyrmex.utils.cli_helpers import (
    ProgressReporter,
    print_section,
    print_info,
    print_success,
    print_error,
    print_warning,
    print_with_color,
)

from .config import load_config, get_script_config
from .discovery import discover_scripts
from .runner import run_script
from .reporting import save_log, generate_report, generate_script_documentation


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
        default=None, # Will default to scripts dir parent / output / script_logs
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
    
    # Optional: pass scripts_dir explicitly if calling from somewhere else
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        help="Root directory of scripts to orchestrate",
    )
    
    parser.add_argument(
        "--generate-docs",
        help="Generate Markdown documentation to this file path",
    )
    
    args = parser.parse_args()
    
    # Determine scripts_dir
    # If not provided, assume we are running from a script in scripts/ or
    # try to locate it relative to current working directory
    if args.scripts_dir:
        scripts_dir = args.scripts_dir.resolve()
    else:
        # Fallback: assume run_all_scripts.py is the caller or we are in project root
        # This is a bit heuristical; ideally the caller passes it
        cwd = Path.cwd()
        if (cwd / "scripts").exists():
            scripts_dir = (cwd / "scripts").resolve()
        elif cwd.name == "scripts":
            scripts_dir = cwd.resolve()
        else:
             # Try to find from run_all_scripts path in sys.argv[0] if present
             caller = Path(sys.argv[0]).resolve()
             if caller.parent.name == "scripts":
                 scripts_dir = caller.parent
             else:
                 print_error("Could not determine scripts directory. Please use --scripts-dir")
                 return 1
    
    if not args.output_dir:
        # Default output dir relative to project root (parent of scripts dir)
        args.output_dir = scripts_dir.parent / "output" / "script_logs"
    
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
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] [{i}/{len(scripts)}] Running: {relative_path}")
            
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
        timestamp = datetime.now().strftime("%H:%M:%S")
        if result["status"] == "passed":
            if args.verbose:
                print_success(f"  [{timestamp}] {result['name']} ({result['execution_time']:.1f}s)")
        elif result["status"] == "failed":
            print_error(f"  [{timestamp}] {result['name']} (exit code {result['exit_code']})")
        elif result["status"] == "timeout":
            print_warning(f"  [{timestamp}] {result['name']} (timeout after {args.timeout}s)")
        else:
            print_error(f"  [{timestamp}] {result['name']} ({result['error']})")
    
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

    # Top Slowest Scripts
    print_section("Top 5 Slowest Scripts", separator="-")
    slowest = sorted(results, key=lambda x: x["execution_time"], reverse=True)[:5]
    for r in slowest:
         print(f"  {r['execution_time']:.2f}s: {r['subdirectory']}/{r['name']}")
    
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
                # Show last line of stderr for better context (usually the Exception)
                lines = r["stderr"].strip().split("\n")
                last_line = lines[-1] if lines else ""
                print(f"     {last_line}")
                # Also show the line before if it helps (e.g. "SyntaxError: ...")
                if len(lines) > 1 and "Traceback" not in lines[-1]:
                     print(f"     {lines[-2]}")
    
    # Return non-zero if any failed
    return 1 if summary["failed"] + summary["error"] + summary["timeout"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
