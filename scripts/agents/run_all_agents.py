#!/usr/bin/env python3
"""
Run All Agent Examples

Executes all agent example scripts in sequence, reporting results.
Useful for validating agent ecosystem health.
"""
import subprocess
import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import (
    setup_logging, print_success, print_error, print_info, print_section, print_warning
)

# All example scripts to run (in recommended order)
EXAMPLE_SCRIPTS = [
    "basic_usage.py",
    "agent_diagnostics.py",
    "code_editor_example.py",
    "theory_example.py",
    "droid_example.py",
    "claude_example.py",
    "codex_example.py",
    "gemini_example.py",
    "jules_example.py",
    "opencode_example.py",
    "multi_agent_workflow.py",
    "advanced_workflow.py",
]


def run_script(script_path: Path) -> tuple[bool, str]:
    """Run a single script and return (success, output)."""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout per script
            cwd=script_path.parent,
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: Script exceeded 120 seconds"
    except Exception as e:
        return False, f"ERROR: {str(e)}"


def main():
    setup_logging()
    print_section("Running All Agent Examples")

    # Scripts are now in the same directory (flattened structure)
    scripts_dir = Path(__file__).resolve().parent

    results = {}
    passed = 0
    failed = 0

    for script_name in EXAMPLE_SCRIPTS:
        script_path = scripts_dir / script_name
        
        if not script_path.exists():
            print_warning(f"  SKIP: {script_name} (not found)")
            results[script_name] = ("skipped", "File not found")
            continue

        print_info(f"\n[{script_name}] Running...")
        success, output = run_script(script_path)

        if success:
            print_success(f"  PASS: {script_name}")
            results[script_name] = ("passed", output)
            passed += 1
        else:
            print_error(f"  FAIL: {script_name}")
            # Show first few lines of error output
            error_lines = output.strip().split('\n')[:5]
            for line in error_lines:
                print_info(f"    {line}")
            results[script_name] = ("failed", output)
            failed += 1

    # Summary
    print_section("Summary")
    total = passed + failed
    print_info(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        print_warning("\nFailed Scripts:")
        for name, (status, _) in results.items():
            if status == "failed":
                print_error(f"  - {name}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
