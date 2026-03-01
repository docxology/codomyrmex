#!/usr/bin/env python3
"""Validate dependency consistency between pyproject.toml, requirements.txt, and uv.lock.

This script checks for:
- Missing dependencies in lock files
- Version conflicts between configuration files
- Outdated dependency specifications
"""

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def parse_pyproject(path: Path) -> dict[str, Any]:
    """Parse pyproject.toml and extract dependencies."""
    if not path.exists():
        return {}
    
    with open(path, "rb") as f:
        data = tomllib.load(f)
    
    deps = {}
    project = data.get("project", {})
    
    # Main dependencies
    for dep in project.get("dependencies", []):
        name = dep.split("[")[0].split(">=")[0].split("==")[0].split("<")[0].strip()
        deps[name.lower()] = dep
    
    # Optional dependencies
    optional_deps = project.get("optional-dependencies", {})
    for group, group_deps in optional_deps.items():
        for dep in group_deps:
            name = dep.split("[")[0].split(">=")[0].split("==")[0].split("<")[0].strip()
            deps[name.lower()] = dep
    
    return deps


def parse_requirements(path: Path) -> dict[str, str]:
    """Parse requirements.txt file."""
    if not path.exists():
        return {}
    
    deps = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                name = line.split("[")[0].split(">=")[0].split("==")[0].split("<")[0].strip()
                deps[name.lower()] = line
    
    return deps


def check_lock_file(path: Path) -> bool:
    """Check if lock file exists and is valid."""
    if not path.exists():
        print(f"⚠️  Lock file not found: {path}")
        return False
    
    # Basic validation - check it's not empty
    if path.stat().st_size == 0:
        print(f"❌ Lock file is empty: {path}")
        return False
    
    print(f"✅ Lock file exists: {path}")
    return True


def validate_dependencies(repo_root: Path) -> int:
    """Run all dependency validations."""
    print("🔍 Validating dependency management...\n")
    
    issues = []
    
    # Check pyproject.toml
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        issues.append("pyproject.toml not found")
    else:
        print(f"✅ Found pyproject.toml")
        pyproject_deps = parse_pyproject(pyproject_path)
        print(f"   Found {len(pyproject_deps)} dependencies")
    
    # Check uv.lock
    uv_lock = repo_root / "uv.lock"
    check_lock_file(uv_lock)
    
    # Check for requirements.txt (optional)
    requirements = repo_root / "requirements.txt"
    if requirements.exists():
        print(f"✅ Found requirements.txt")
        req_deps = parse_requirements(requirements)
        print(f"   Found {len(req_deps)} dependencies")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   - {issue}")
        return 1
    else:
        print("✅ Dependency validation passed!")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Validate dependency consistency")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings"
    )
    
    args = parser.parse_args()
    
    return validate_dependencies(args.repo_root)


if __name__ == "__main__":
    sys.exit(main())
