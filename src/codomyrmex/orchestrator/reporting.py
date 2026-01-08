from codomyrmex.logging_monitoring import get_logger
"""Orchestrator Reporting.

Handles logging, summary generation, and documentation.

This module provides reporting functionality including:
- 3 functions: save_log, generate_report, generate_script_documentation
- 0 classes: 

Usage:
    from reporting import FunctionName, ClassName
    # Example usage here
"""
logger = get_logger(__name__)

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .discovery import discover_scripts
from codomyrmex.utils.cli_helpers import (
    print_section,
    print_info,
    print_success,
    print_warning,
    print_error,
)

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
        stdout = result["stdout"] or "(no output)\n"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        f.write(stdout)
        f.write("\n" + "=" * 60 + "\n")
        f.write("STDERR:\n")
        f.write("=" * 60 + "\n")
        stderr = result["stderr"] or "(no errors)\n"
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        f.write(stderr)
        
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
