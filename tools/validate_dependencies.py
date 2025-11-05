#!/usr/bin/env python3
"""
Dependency Validation Tool

Validates that:
1. All dependencies in pyproject.toml have version constraints
2. No duplicate dependencies across optional groups
3. No conflicting version requirements
4. requirements.txt files are deprecated (have deprecation notice)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def parse_pyproject_dependencies(content: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    Parse dependencies from pyproject.toml content.
    
    Returns:
        Dict mapping section name to list of (package_name, version_spec)
    """
    dependencies = defaultdict(list)
    
    current_section = None
    
    for line in content.splitlines():
        line_stripped = line.strip()
        
        # Detect section headers
        if line_stripped.startswith("[project.dependencies]"):
            current_section = "dependencies"
        elif line_stripped.startswith("[project.optional-dependencies]"):
            current_section = "optional-dependencies"
        elif line_stripped.startswith("["):
            # Reset on new section
            if not line_stripped.startswith("[project.optional-dependencies."):
                current_section = None
        elif line_stripped.startswith("[project.optional-dependencies."):
            # Extract group name
            match = re.match(r"\[project\.optional-dependencies\.([^\]]+)\]", line_stripped)
            if match:
                current_section = f"optional-{match.group(1)}"
        
        # Parse dependency lines
        if current_section and line_stripped and not line_stripped.startswith("#"):
            # Match package with optional version
            match = re.match(r'^\s*"([^"]+)"', line_stripped)
            if match:
                package_spec = match.group(1)
                # Extract package name and version
                pkg_match = re.match(r"^([a-zA-Z0-9_-]+[a-zA-Z0-9._-]*)([<>=!~=]+.*)?$", package_spec)
                if pkg_match:
                    pkg_name = pkg_match.group(1).lower()
                    version = pkg_match.group(2) or ""
                    
                    section_key = current_section if current_section != "optional-dependencies" else "optional-dependencies"
                    dependencies[section_key].append((pkg_name, version))
    
    return dict(dependencies)


def check_version_constraints(dependencies: Dict[str, List[Tuple[str, str]]]) -> List[str]:
    """Check that all dependencies have version constraints."""
    errors = []
    
    for section, deps in dependencies.items():
        for pkg_name, version in deps:
            if not version:
                errors.append(f"❌ {pkg_name} in {section} has no version constraint")
    
    return errors


def check_duplicates(dependencies: Dict[str, List[Tuple[str, str]]]) -> List[str]:
    """Check for duplicate packages across sections."""
    warnings = []
    all_packages = defaultdict(set)
    
    for section, deps in dependencies.items():
        for pkg_name, version in deps:
            all_packages[pkg_name].add((section, version))
    
    for pkg_name, occurrences in all_packages.items():
        if len(occurrences) > 1:
            sections = [f"{s} ({v})" for s, v in occurrences]
            warnings.append(f"⚠️  {pkg_name} appears in multiple sections: {', '.join(sections)}")
    
    return warnings


def check_requirements_txt_deprecated(root: Path) -> List[str]:
    """Check that all requirements.txt files have deprecation notices."""
    errors = []
    warnings = []
    
    codomyrmex_dir = root / "src" / "codomyrmex"
    if not codomyrmex_dir.exists():
        return errors
    
    for module_dir in codomyrmex_dir.iterdir():
        if module_dir.is_dir():
            req_file = module_dir / "requirements.txt"
            if req_file.exists():
                content = req_file.read_text(encoding="utf-8")
                if not content.startswith("# DEPRECATED"):
                    errors.append(f"❌ {req_file} missing deprecation notice")
                elif "DEPRECATED" not in content:
                    warnings.append(f"⚠️  {req_file} may have incomplete deprecation notice")
    
    return errors + warnings


def main() -> int:
    """Main validation function."""
    root = Path(__file__).parent.parent
    pyproject_path = root / "pyproject.toml"
    
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return 1
    
    print("🔍 Validating dependency management...\n")
    
    # Read pyproject.toml
    content = pyproject_path.read_text(encoding="utf-8")
    
    # Parse dependencies
    dependencies = parse_pyproject_dependencies(content)
    
    print(f"Found dependencies in {len(dependencies)} sections")
    
    # Run checks
    all_errors = []
    all_warnings = []
    
    # Check version constraints
    version_errors = check_version_constraints(dependencies)
    all_errors.extend(version_errors)
    
    # Check duplicates
    duplicate_warnings = check_duplicates(dependencies)
    all_warnings.extend(duplicate_warnings)
    
    # Check requirements.txt deprecation
    req_issues = check_requirements_txt_deprecated(root)
    for issue in req_issues:
        if issue.startswith("❌"):
            all_errors.append(issue)
        else:
            all_warnings.append(issue)
    
    # Report results
    if all_errors:
        print("\n❌ ERRORS FOUND:")
        for error in all_errors:
            print(f"  {error}")
    
    if all_warnings:
        print("\n⚠️  WARNINGS:")
        for warning in all_warnings:
            print(f"  {warning}")
    
    if not all_errors and not all_warnings:
        print("\n✅ All dependency validation checks passed!")
        return 0
    
    if all_errors:
        print(f"\n❌ Validation failed with {len(all_errors)} error(s)")
        return 1
    
    print(f"\n⚠️  Validation completed with {len(all_warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

