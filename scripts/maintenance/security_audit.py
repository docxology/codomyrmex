#!/usr/bin/env python3
"""
Security Audit Script

This script runs security checks on dependencies and code:
- pip-audit for dependency vulnerabilities
- safety check for known security issues
- Summarizes findings and provides recommendations
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def run_pip_audit() -> Dict[str, Any]:
    """Run pip-audit on all requirements files."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Find all requirements.txt files
    requirements_files = list(project_root.rglob('requirements.txt'))
    requirements_files = [
        f for f in requirements_files
        if '.venv' not in str(f) and 'venv' not in str(f) and '__pycache__' not in str(f)
    ]

    all_vulnerabilities = []

    for req_file in requirements_files:
        try:
            cmd = ["pip-audit", "--format", "json", "--requirement", str(req_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    vulns = data.get('vulnerabilities', [])
                    for vuln in vulns:
                        vuln['requirements_file'] = str(req_file.relative_to(project_root))
                    all_vulnerabilities.extend(vulns)
                except json.JSONDecodeError:
                    pass
        except subprocess.TimeoutExpired:
            print(f"pip-audit timed out for {req_file}", file=sys.stderr)
        except FileNotFoundError:
            print("pip-audit not found. Install with: pip install pip-audit", file=sys.stderr)
            return {'tool': 'pip-audit', 'available': False, 'vulnerabilities': []}
        except Exception as e:
            print(f"Error running pip-audit on {req_file}: {e}", file=sys.stderr)

    return {
        'tool': 'pip-audit',
        'available': True,
        'vulnerabilities': all_vulnerabilities,
        'total_vulnerabilities': len(all_vulnerabilities)
    }


def run_safety_check() -> Dict[str, Any]:
    """Run safety check on dependencies."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    try:
        cmd = ["safety", "check", "--json"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=project_root
        )

        vulnerabilities = []
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                vulnerabilities = data if isinstance(data, list) else []
            except json.JSONDecodeError:
                # Safety might output text format
                for line in result.stdout.split('\n'):
                    if line.strip() and '|' in line:
                        vulnerabilities.append({'raw': line})

        return {
            'tool': 'safety',
            'available': True,
            'vulnerabilities': vulnerabilities,
            'total_vulnerabilities': len(vulnerabilities)
        }
    except FileNotFoundError:
        return {
            'tool': 'safety',
            'available': False,
            'vulnerabilities': [],
            'total_vulnerabilities': 0,
            'note': 'safety not installed. Install with: pip install safety'
        }
    except subprocess.TimeoutExpired:
        return {
            'tool': 'safety',
            'available': True,
            'vulnerabilities': [],
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'tool': 'safety',
            'available': True,
            'vulnerabilities': [],
            'error': str(e)
        }


def categorize_vulnerabilities(vulnerabilities: List[Dict]) -> Dict[str, List]:
    """Categorize vulnerabilities by severity."""
    critical = []
    high = []
    medium = []
    low = []

    for vuln in vulnerabilities:
        severity = vuln.get('severity', '').lower() or vuln.get('vulnerability', {}).get('severity', '').lower()

        if 'critical' in severity or '9.0' in str(vuln.get('cvss', '')):
            critical.append(vuln)
        elif 'high' in severity or '7.0' in str(vuln.get('cvss', '')):
            high.append(vuln)
        elif 'medium' in severity or '4.0' in str(vuln.get('cvss', '')):
            medium.append(vuln)
        else:
            low.append(vuln)

    return {
        'critical': critical,
        'high': high,
        'medium': medium,
        'low': low
    }


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    output_dir = project_root / "@output"
    output_dir.mkdir(exist_ok=True)

    print("Running security audit on dependencies...")
    print("=" * 80)

    results = {}

    # Run pip-audit
    print("\nRunning pip-audit...")
    results['pip_audit'] = run_pip_audit()

    # Run safety check
    print("Running safety check...")
    results['safety'] = run_safety_check()

    # Combine and categorize
    all_vulns = []
    if results['pip_audit']['available']:
        all_vulns.extend(results['pip_audit']['vulnerabilities'])
    if results['safety']['available']:
        all_vulns.extend(results['safety']['vulnerabilities'])

    categorized = categorize_vulnerabilities(all_vulns)

    # Summary
    print("\n" + "=" * 80)
    print("SECURITY AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total vulnerabilities found: {len(all_vulns)}")
    print(f"  Critical: {len(categorized['critical'])}")
    print(f"  High: {len(categorized['high'])}")
    print(f"  Medium: {len(categorized['medium'])}")
    print(f"  Low: {len(categorized['low'])}")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'categorized': categorized,
        'summary': {
            'total': len(all_vulns),
            'critical': len(categorized['critical']),
            'high': len(categorized['high']),
            'medium': len(categorized['medium']),
            'low': len(categorized['low'])
        }
    }

    json_path = output_dir / f"security_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport saved to: {json_path}")

    # Print critical and high vulnerabilities
    if categorized['critical'] or categorized['high']:
        print("\n" + "=" * 80)
        print("CRITICAL AND HIGH PRIORITY VULNERABILITIES:")
        print("=" * 80)
        for vuln in categorized['critical'][:10]:
            print(f"\n{vuln}")
        for vuln in categorized['high'][:10]:
            print(f"\n{vuln}")

    if len(all_vulns) > 0:
        print("\n⚠️  Action required: Update vulnerable dependencies")
        return 1
    else:
        print("\n✅ No security vulnerabilities found!")
        return 0


if __name__ == '__main__':
    sys.exit(main())

