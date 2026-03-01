"""Orchestrator Core.

Main entry point and execution loop for running and reporting on scripts.

This module provides:
- main(): Entry point for script orchestration
- Discovery, execution, and reporting of Python scripts
"""

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.logging_monitoring.core.logger_config import LogContext
from codomyrmex.logging_monitoring.handlers.performance import PerformanceLogger

logger = get_logger(__name__)


import argparse
import sys
from datetime import datetime
from pathlib import Path

from codomyrmex.utils.cli_helpers import (
    ProgressReporter,
    print_error,
    print_info,
    print_section,
    print_success,
    print_warning,
    print_with_color,
)

from .config import get_script_config, load_config
from .discovery import discover_scripts
from .execution.runner import run_script
from .observability.reporting import (
    generate_report,
    generate_script_documentation,
    save_log,
)


def _parse_args(argv=None) -> argparse.Namespace:
    """Parse command-line arguments for the orchestrator.

    Args:
        argv: Argument list (defaults to sys.argv if None).

    Returns:
        Parsed argument namespace.
    """
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
        default=None,  # Will default to scripts dir parent / output / script_logs
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

    return parser.parse_args(argv)


def _resolve_scripts_dir(args: argparse.Namespace) -> Path | None:
    """Determine the scripts directory from arguments or heuristics.

    Args:
        args: Parsed arguments.

    Returns:
        Resolved scripts directory path, or None if it cannot be determined.
    """
    if args.scripts_dir:
        return args.scripts_dir.resolve()

    # Fallback heuristics
    cwd = Path.cwd()
    if (cwd / "scripts").exists():
        return (cwd / "scripts").resolve()
    elif cwd.name == "scripts":
        return cwd.resolve()
    else:
        # Try to find from run_all_scripts path in sys.argv[0] if present
        caller = Path(sys.argv[0]).resolve()
        if caller.parent.name == "scripts":
            return caller.parent

    return None


def _discover_and_display_scripts(
    scripts_dir: Path, args: argparse.Namespace, config: dict
) -> tuple[list[Path], int]:
    """Discover scripts and display them grouped by subdirectory.

    Args:
        scripts_dir: Root directory to search.
        args: Parsed arguments (subdirs, filter, max_depth, verbose, dry_run).
        config: Loaded orchestrator config.

    Returns:
        Tuple of (discovered scripts list, exit code if early exit needed or -1 to continue).
    """
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
        return scripts, 0

    # Group by subdirectory for display
    by_subdir: dict[str, list[Path]] = {}
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
                print(f"  WOULD SKIP: {script.name} ({script_config.get('skip_reason', 'Configured to skip')})")
                skipped_count += 1

        print(f"  Skipped by config: {skipped_count}")
        return scripts, 0

    return scripts, -1  # -1 signals "continue execution"


def _execute_scripts(
    scripts: list[Path], scripts_dir: Path, args: argparse.Namespace, config: dict
) -> list[dict]:
    """Execute all discovered scripts and collect results.

    Args:
        scripts: List of script paths to execute.
        scripts_dir: Root scripts directory.
        args: Parsed arguments (timeout, verbose).
        config: Loaded orchestrator config.

    Returns:
        List of result dictionaries for each script.
    """
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

        # Use improved subdirectory for logging to avoid collisions (e.g. module/examples/)
        result["subdirectory"] = str(script.relative_to(scripts_dir).parent)

        # Save individual log
        log_file = save_log(result, args.output_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
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
    return results


def _report_results(results: list[dict], args: argparse.Namespace, run_id: str) -> int:
    """Generate and display the summary report.

    Args:
        results: List of script execution result dicts.
        args: Parsed arguments (output_dir).
        run_id: Unique run identifier.

    Returns:
        Exit code (0 if all passed, 1 if any failed/errored/timed out).
    """
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
        status_marker = "PASS" if stats["failed"] == 0 else "FAIL"
        print(f"  {status_marker} {subdir}: {stats['passed']}/{stats['total']} passed")

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
            print(f"  FAIL {r['subdirectory']}/{r['name']}")
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

    return summary, 1 if summary["failed"] + summary["error"] + summary["timeout"] > 0 else 0


def main(argv=None):
    """Main entry point for the script orchestrator.

    Parses arguments, discovers scripts, executes them, and reports results.
    Delegates to private helper functions for each phase.

    Args:
        argv: Optional argument list (defaults to sys.argv).

    Returns:
        Exit code (0 for success, 1 for failures).
    """
    args = _parse_args(argv)

    # Determine scripts_dir
    scripts_dir = _resolve_scripts_dir(args)
    if scripts_dir is None:
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
    perf_logger = PerformanceLogger("orchestrator.performance")

    print_section("SCRIPT ORCHESTRATOR")
    print_info(f"Scripts directory: {scripts_dir}")
    print_info(f"Run ID: {run_id}")

    # Discover scripts
    scripts, early_exit = _discover_and_display_scripts(scripts_dir, args, config)
    if early_exit >= 0:
        return early_exit

    # Execute scripts with LogContext for correlation ID
    with LogContext(correlation_id=run_id) as ctx:
        logger.info("Orchestrator run started", extra={
            "event": "RUN_STARTED",
            "run_id": run_id,
            "scripts_dir": str(scripts_dir),
            "scripts_count": len(scripts),
            "timeout": args.timeout,
        })
        perf_logger.start_timer("full_run", {"scripts_count": len(scripts)})

        print_section("Executing Scripts", separator="-")
        print_info(f"Timeout per script: {args.timeout}s")
        print()

        results = _execute_scripts(scripts, scripts_dir, args, config)

        # Generate summary report
        summary, exit_code = _report_results(results, args, run_id)

        # Log RUN_COMPLETED event
        run_duration = perf_logger.end_timer("full_run")
        logger.info("Orchestrator run completed", extra={
            "event": "RUN_COMPLETED",
            "run_id": run_id,
            "total_scripts": summary["total_scripts"],
            "passed": summary["passed"],
            "failed": summary["failed"],
            "timeout": summary["timeout"],
            "error": summary["error"],
            "total_execution_time": summary["total_execution_time"],
        })

        return exit_code


if __name__ == "__main__":
    sys.exit(main())
