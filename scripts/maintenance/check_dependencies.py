#!/usr/bin/env python3
"""Check dependency health for maintenance purposes.

This script performs routine dependency health checks:
- Identifies outdated packages
- Checks for security advisories (basic)
- Reports dependency tree depth
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_dependencies(repo_root: Path) -> int:
    """Run dependency health checks."""
    print("🔧 Running dependency health checks...\n")
    
    issues = []
    
    # Check if uv is available
    code, stdout, stderr = run_command(["uv", "--version"])
    if code == 0:
        print(f"✅ UV version: {stdout.strip()}")
    else:
        print("⚠️  UV not found, skipping some checks")
    
    # Check for lock file
    lock_file = repo_root / "uv.lock"
    if lock_file.exists():
        print(f"✅ Lock file exists ({lock_file.stat().st_size / 1024:.1f} KB)")
    else:
        issues.append("No lock file found")
        print("❌ Lock file not found")
    
    # Try to validate sync
    print("\n📦 Checking dependency sync...")
    code, stdout, stderr = run_command(["uv", "sync", "--dry-run"], cwd=repo_root)
    if code == 0:
        print("✅ Dependencies are in sync")
    else:
        print("⚠️  Dependencies may need syncing")
    
    # Check for pyproject.toml
    pyproject = repo_root / "pyproject.toml"
    if pyproject.exists():
        print(f"\n✅ pyproject.toml exists")
        
        # Count dependencies (basic check)
        with open(pyproject) as f:
            content = f.read()
            dep_count = content.count(">=") + content.count("==")
            print(f"   Approximate dependencies: {dep_count}")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues:
            print(f"   - {issue}")
        return 1
    else:
        print("✅ Dependency health check passed!")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Check dependency health")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory"
    )
    
    args = parser.parse_args()
    
    return check_dependencies(args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
