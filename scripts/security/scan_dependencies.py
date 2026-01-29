#!/usr/bin/env python3
"""
Scan Python dependencies for known vulnerabilities.

Usage:
    python scan_dependencies.py [--requirements FILE] [--verbose]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess
import json
import re


def find_requirements_files(path: str = ".") -> list:
    """Find requirements files in the project."""
    patterns = [
        "requirements.txt",
        "requirements*.txt",
        "pyproject.toml",
        "setup.py",
    ]
    found = []
    root = Path(path)
    
    for f in root.glob("requirements*.txt"):
        found.append(f)
    
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        found.append(pyproject)
    
    return found


def parse_requirements(file_path: Path) -> list:
    """Parse requirements file and extract package names with versions."""
    packages = []
    
    if file_path.suffix == ".txt":
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    # Extract package name and version
                    match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!~]+.*)?', line)
                    if match:
                        packages.append({
                            "name": match.group(1),
                            "version_spec": match.group(2) or "",
                            "line": line
                        })
    
    elif file_path.name == "pyproject.toml":
        with open(file_path, "r") as f:
            content = f.read()
            # Simple extraction of dependencies
            dep_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if dep_match:
                deps = dep_match.group(1)
                for line in deps.split("\n"):
                    line = line.strip().strip('",')
                    if line:
                        match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                        if match:
                            packages.append({
                                "name": match.group(1),
                                "version_spec": "",
                                "line": line
                            })
    
    return packages


def check_pip_audit() -> bool:
    """Check if pip-audit is available."""
    try:
        result = subprocess.run(["pip-audit", "--version"], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def run_pip_audit(requirements_file: Path) -> dict:
    """Run pip-audit on requirements file."""
    try:
        result = subprocess.run(
            ["pip-audit", "-r", str(requirements_file), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.stdout:
            return json.loads(result.stdout)
        return {"dependencies": [], "vulnerabilities": []}
    except Exception as e:
        return {"error": str(e)}


def check_known_vulnerabilities(packages: list) -> list:
    """Check packages against a list of known vulnerable packages."""
    # Common packages with known vulnerabilities (simplified example)
    KNOWN_VULNS = {
        "urllib3": {"below": "1.26.5", "cve": "CVE-2021-33503", "severity": "HIGH"},
        "requests": {"below": "2.25.0", "cve": "CVE-2018-18074", "severity": "MEDIUM"},
        "pyyaml": {"below": "5.4", "cve": "CVE-2020-14343", "severity": "CRITICAL"},
        "flask": {"below": "2.0.0", "cve": "CVE-2018-1000656", "severity": "HIGH"},
        "django": {"below": "3.2.4", "cve": "CVE-2021-33203", "severity": "MEDIUM"},
        "pillow": {"below": "8.3.2", "cve": "CVE-2021-34552", "severity": "HIGH"},
        "cryptography": {"below": "3.3.2", "cve": "CVE-2020-36242", "severity": "MEDIUM"},
        "jinja2": {"below": "2.11.3", "cve": "CVE-2020-28493", "severity": "HIGH"},
    }
    
    findings = []
    for pkg in packages:
        name_lower = pkg["name"].lower()
        if name_lower in KNOWN_VULNS:
            vuln = KNOWN_VULNS[name_lower]
            findings.append({
                "package": pkg["name"],
                "version_spec": pkg["version_spec"],
                "cve": vuln["cve"],
                "severity": vuln["severity"],
                "fix": f"Update to version >= {vuln['below']}",
                "note": "Version check requires manual verification"
            })
    
    return findings


def main():
    parser = argparse.ArgumentParser(description="Scan dependencies for vulnerabilities")
    parser.add_argument("--requirements", "-r", default=None, help="Requirements file to scan")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all packages")
    parser.add_argument("--use-pip-audit", action="store_true", help="Use pip-audit if available")
    args = parser.parse_args()
    
    print("🔍 Dependency Security Scanner\n")
    
    # Find requirements files
    if args.requirements:
        req_files = [Path(args.requirements)]
    else:
        req_files = find_requirements_files(".")
    
    if not req_files:
        print("❌ No requirements files found")
        print("   Looking for: requirements.txt, pyproject.toml")
        return 1
    
    print(f"📋 Found {len(req_files)} requirements file(s):\n")
    
    total_vulns = 0
    
    for req_file in req_files:
        print(f"📄 {req_file}")
        
        packages = parse_requirements(req_file)
        print(f"   Packages: {len(packages)}")
        
        if args.verbose:
            for pkg in packages[:10]:
                print(f"     - {pkg['name']}{pkg['version_spec']}")
            if len(packages) > 10:
                print(f"     ... and {len(packages) - 10} more")
        
        # Check with pip-audit if requested and available
        if args.use_pip_audit and check_pip_audit():
            print("   Running pip-audit...")
            audit_result = run_pip_audit(req_file)
            if "vulnerabilities" in audit_result:
                vulns = audit_result["vulnerabilities"]
                if vulns:
                    print(f"\n   ⚠️  Found {len(vulns)} vulnerabilities:")
                    for v in vulns:
                        print(f"      • {v.get('name', 'unknown')}: {v.get('id', 'N/A')}")
                    total_vulns += len(vulns)
        else:
            # Use built-in check
            findings = check_known_vulnerabilities(packages)
            if findings:
                print(f"\n   ⚠️  Potential issues ({len(findings)}):")
                for f in findings:
                    severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(f["severity"], "⚪")
                    print(f"      {severity_icon} {f['package']}: {f['cve']} ({f['severity']})")
                    print(f"         → {f['fix']}")
                total_vulns += len(findings)
        
        print()
    
    # Summary
    if total_vulns == 0:
        print("✅ No known vulnerabilities detected")
        print("   Note: Run with --use-pip-audit for comprehensive scanning")
    else:
        print(f"⚠️  Total potential issues: {total_vulns}")
        print("   Review and update affected packages")
    
    return 0 if total_vulns == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
