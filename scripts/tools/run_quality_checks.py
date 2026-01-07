#!/usr/bin/env python3
"""
Run all code quality checks and generate reports.

This script runs ruff, pylint, mypy, and bandit on the codebase,
generates reports, and categorizes issues by severity.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def run_command(cmd: List[str], description: str) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"{description} timed out after 5 minutes"
    except Exception as e:
        return 1, "", str(e)


def run_ruff_check() -> Dict[str, Any]:
    """Run ruff check and parse results."""
    cmd = ["ruff", "check", "src/codomyrmex/", "--output-format", "json"]
    exit_code, stdout, stderr = run_command(cmd, "ruff check")

    issues = []
    if exit_code == 0:
        # No issues or empty output
        if stdout.strip():
            try:
                issues = json.loads(stdout)
            except json.JSONDecodeError:
                pass
    else:
        # Try to parse JSON output even on error
        if stdout.strip():
            try:
                issues = json.loads(stdout)
            except json.JSONDecodeError:
                # Fallback to text parsing
                for line in stdout.split('\n'):
                    if line.strip() and not line.startswith('warning'):
                        issues.append({'message': line})

    return {
        'tool': 'ruff',
        'exit_code': exit_code,
        'issues': issues,
        'stderr': stderr,
        'total_issues': len(issues)
    }


def run_bandit_check() -> Dict[str, Any]:
    """Run bandit security check and parse results."""
    cmd = ["bandit", "-r", "src/codomyrmex/", "-f", "json", "-ll"]
    exit_code, stdout, stderr = run_command(cmd, "bandit security check")

    issues = []
    if stdout.strip():
        try:
            result = json.loads(stdout)
            issues = result.get('results', [])
        except json.JSONDecodeError:
            pass

    # Categorize by severity
    critical = [i for i in issues if i.get('issue_severity') == 'HIGH' and 'security' in str(i.get('test_id', '')).lower()]
    high = [i for i in issues if i.get('issue_severity') == 'HIGH']
    medium = [i for i in issues if i.get('issue_severity') == 'MEDIUM']
    low = [i for i in issues if i.get('issue_severity') == 'LOW']

    return {
        'tool': 'bandit',
        'exit_code': exit_code,
        'issues': issues,
        'stderr': stderr,
        'total_issues': len(issues),
        'by_severity': {
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low
        }
    }


def run_mypy_check() -> Dict[str, Any]:
    """Run mypy type checking."""
    cmd = ["mypy", "src/codomyrmex/", "--no-error-summary", "--show-error-codes"]
    exit_code, stdout, stderr = run_command(cmd, "mypy type checking")

    errors = []
    for line in stdout.split('\n'):
        if line.strip() and ('error:' in line or 'note:' in line):
            errors.append(line.strip())

    return {
        'tool': 'mypy',
        'exit_code': exit_code,
        'errors': errors,
        'stderr': stderr,
        'total_errors': len([e for e in errors if 'error:' in e])
    }


def run_pylint_check() -> Dict[str, Any]:
    """Run pylint check."""
    # Use a more lenient approach - pylint can be very verbose
    cmd = ["pylint", "src/codomyrmex/", "--output-format=json", "--disable=all", "--enable=E,F"]
    exit_code, stdout, stderr = run_command(cmd, "pylint check (errors and fatal only)")

    issues = []
    if stdout.strip():
        try:
            issues = json.loads(stdout)
        except json.JSONDecodeError:
            pass

    return {
        'tool': 'pylint',
        'exit_code': exit_code,
        'issues': issues,
        'stderr': stderr,
        'total_issues': len(issues)
    }


def generate_summary_report(results: Dict[str, Dict[str, Any]]) -> str:
    """Generate a human-readable summary report."""
    report = []
    report.append("=" * 80)
    report.append("CODE QUALITY CHECK SUMMARY")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("")

    for tool_name, result in results.items():
        report.append(f"\n{tool_name.upper()}:")
        report.append("-" * 80)

        if tool_name == 'bandit':
            report.append(f"Total Issues: {result['total_issues']}")
            report.append(f"  Critical: {len(result['by_severity']['critical'])}")
            report.append(f"  High: {len(result['by_severity']['high'])}")
            report.append(f"  Medium: {len(result['by_severity']['medium'])}")
            report.append(f"  Low: {len(result['by_severity']['low'])}")
        elif tool_name == 'mypy':
            report.append(f"Total Type Errors: {result['total_errors']}")
        else:
            report.append(f"Total Issues: {result['total_issues']}")

        report.append(f"Exit Code: {result['exit_code']}")
        if result['exit_code'] != 0:
            report.append("  ⚠️  Issues found")
        else:
            report.append("  ✅ No issues found")

    report.append("\n" + "=" * 80)
    return "\n".join(report)


def main():
    """Main function to run all quality checks."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    output_dir = project_root / "@output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("Starting comprehensive code quality checks...")
    print("=" * 80)

    results = {}

    # Run all checks
    results['ruff'] = run_ruff_check()
    results['bandit'] = run_bandit_check()
    results['mypy'] = run_mypy_check()
    results['pylint'] = run_pylint_check()

    # Save detailed JSON report
    json_report_path = output_dir / f"quality_check_report_{timestamp}.json"
    with open(json_report_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nDetailed JSON report saved to: {json_report_path}")

    # Generate and save summary report
    summary = generate_summary_report(results)
    summary_path = output_dir / f"quality_check_summary_{timestamp}.txt"
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"Summary report saved to: {summary_path}")

    # Print summary to console
    print("\n" + summary)

    # Determine overall exit code
    overall_exit = 0
    for tool_name, result in results.items():
        if result['exit_code'] != 0:
            overall_exit = 1
            break

    if overall_exit == 0:
        print("\n✅ All quality checks passed!")
    else:
        print("\n⚠️  Some quality checks found issues. Review reports above.")

    return overall_exit


if __name__ == '__main__':
    sys.exit(main())

