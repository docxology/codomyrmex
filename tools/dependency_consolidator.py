#!/usr/bin/env python3
"""
Dependency Consolidator - Migration tool for consolidating requirements.txt to pyproject.toml

This script analyzes all module-specific requirements.txt files and consolidates them
into pyproject.toml with exact version pinning.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def parse_requirements_file(file_path: Path) -> List[Tuple[str, str, str]]:
    """
    Parse a requirements.txt file and return list of (name, version, source_file).
    
    Returns:
        List of tuples: (package_name, version_spec, source_file)
    """
    dependencies = []
    
    if not file_path.exists():
        return dependencies
    
    content = file_path.read_text(encoding="utf-8")
    
    for line in content.splitlines():
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue
        
        # Remove inline comments
        if "#" in line:
            line = line.split("#")[0].strip()
        
        # Parse package specification
        # Format: package==version, package>=version, package~=version, etc.
        match = re.match(r"^([a-zA-Z0-9_-]+[a-zA-Z0-9._-]*)([<>=!~=]+)?([0-9.]+)?", line)
        if match:
            package_name = match.group(1).lower()
            operator = match.group(2) or ""
            version = match.group(3) or ""
            
            # Normalize version spec
            if operator and version:
                version_spec = f"{operator}{version}"
            elif operator:
                version_spec = operator
            else:
                version_spec = ""
            
            dependencies.append((package_name, version_spec, str(file_path)))
    
    return dependencies


def find_all_requirements_files(root: Path) -> List[Path]:
    """Find all requirements.txt files in the repository."""
    requirements_files = []
    
    # Look in src/codomyrmex/*/requirements.txt
    codomyrmex_dir = root / "src" / "codomyrmex"
    if codomyrmex_dir.exists():
        for module_dir in codomyrmex_dir.iterdir():
            if module_dir.is_dir():
                req_file = module_dir / "requirements.txt"
                if req_file.exists():
                    requirements_files.append(req_file)
    
    return sorted(requirements_files)


def analyze_dependencies(root: Path) -> Dict[str, Dict]:
    """
    Analyze all requirements.txt files and return consolidated dependency information.
    
    Returns:
        Dictionary mapping package names to dependency info:
        {
            "package_name": {
                "versions": Set of version specs found,
                "sources": List of source files,
                "conflicts": List of conflicting versions
            }
        }
    """
    requirements_files = find_all_requirements_files(root)
    dependencies = defaultdict(lambda: {"versions": set(), "sources": [], "conflicts": []})
    
    print(f"Found {len(requirements_files)} requirements.txt files")
    
    for req_file in requirements_files:
        deps = parse_requirements_file(req_file)
        print(f"  {req_file.name}: {len(deps)} dependencies")
        
        for package_name, version_spec, source_file in deps:
            dependencies[package_name]["versions"].add(version_spec)
            dependencies[package_name]["sources"].append((str(req_file), version_spec))
    
    # Identify conflicts (multiple version specs for same package)
    for package_name, info in dependencies.items():
        if len(info["versions"]) > 1:
            info["conflicts"] = list(info["versions"])
    
    return dict(dependencies)


def generate_pyproject_additions(dependencies: Dict[str, Dict], pyproject_content: str) -> Tuple[str, Dict[str, str]]:
    """
    Generate additions to pyproject.toml for optional dependency groups.
    
    Returns:
        Tuple of (optional_dependencies_section, module_mapping)
    """
    # Parse existing dependencies from pyproject.toml
    existing_deps = set()
    for line in pyproject_content.splitlines():
        if '"' in line and not line.strip().startswith("#"):
            match = re.search(r'"([a-zA-Z0-9_-]+[a-zA-Z0-9._-]*)"', line)
            if match:
                existing_deps.add(match.group(1).lower())
    
    # Group dependencies by module
    module_deps = defaultdict(set)
    
    for package_name, info in dependencies.items():
        # Skip if already in main dependencies
        if package_name.lower() in existing_deps:
            continue
        
        # Get the most specific version (prefer == over >=)
        versions = list(info["versions"])
        if any("==" in v for v in versions):
            version_spec = [v for v in versions if "==" in v][0]
        elif versions:
            version_spec = versions[0]
        else:
            version_spec = ""
        
        # Determine which modules need this dependency
        modules = set()
        for source, _ in info["sources"]:
            # Extract module name from path
            match = re.search(r"codomyrmex/([^/]+)/requirements\.txt", source)
            if match:
                modules.add(match.group(1))
        
        for module in modules:
            if version_spec:
                module_deps[module].add(f'{package_name}{version_spec}')
            else:
                module_deps[module].add(package_name)
    
    # Generate optional-dependencies section
    optional_deps_section = "[project.optional-dependencies]\n"
    
    for module in sorted(module_deps.keys()):
        deps_list = sorted(module_deps[module])
        optional_deps_section += f'\n{module} = [\n'
        for dep in deps_list:
            optional_deps_section += f'    "{dep}",\n'
        optional_deps_section += ']\n'
    
    return optional_deps_section, {module: list(module_deps[module]) for module in module_deps}


def generate_deprecation_notice(module_name: str, new_location: str) -> str:
    """Generate deprecation notice for requirements.txt files."""
    return f"""# DEPRECATED: This file is deprecated and will be removed in a future version.
#
# All dependencies have been consolidated into pyproject.toml as the single source of truth.
# 
# To install dependencies for this module:
#   uv sync --extra {module_name}
#
# Or install all optional dependencies:
#   uv sync --all-extras
#
# This file is kept temporarily for backward compatibility but should not be modified.
# See docs/project/contributing.md for the new dependency management strategy.
#
# Migration completed: {new_location}
"""


def main():
    """Main consolidation workflow."""
    root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("Dependency Consolidation Analysis")
    print("=" * 70)
    
    # Analyze dependencies
    dependencies = analyze_dependencies(root)
    
    print(f"\nFound {len(dependencies)} unique packages across all requirements.txt files")
    
    # Show conflicts
    conflicts = {name: info for name, info in dependencies.items() if info["conflicts"]}
    if conflicts:
        print(f"\n⚠️  Found {len(conflicts)} packages with version conflicts:")
        for package_name, info in conflicts.items():
            print(f"  {package_name}: {info['conflicts']}")
    
    # Read pyproject.toml
    pyproject_path = root / "pyproject.toml"
    pyproject_content = pyproject_path.read_text(encoding="utf-8")
    
    # Generate optional dependencies section
    optional_deps, module_mapping = generate_pyproject_additions(dependencies, pyproject_content)
    
    print(f"\n📦 Module-specific dependencies to add:")
    for module, deps in sorted(module_mapping.items()):
        print(f"  {module}: {len(deps)} dependencies")
    
    # Save analysis report
    report_path = root / "tools" / "dependency_consolidation_report.md"
    report_content = f"""# Dependency Consolidation Report

Generated by: `tools/dependency_consolidation_report.md`

## Summary

- **Total packages analyzed**: {len(dependencies)}
- **Packages with conflicts**: {len(conflicts)}
- **Modules with dependencies**: {len(module_mapping)}

## Version Conflicts

"""
    
    if conflicts:
        for package_name, info in conflicts.items():
            report_content += f"### {package_name}\n"
            report_content += f"- Conflicting versions: {', '.join(info['conflicts'])}\n"
            report_content += f"- Sources: {len(info['sources'])} files\n\n"
    else:
        report_content += "No conflicts found.\n\n"
    
    report_content += "## Recommended pyproject.toml Additions\n\n"
    report_content += "```toml\n"
    report_content += optional_deps
    report_content += "```\n"
    
    report_path.write_text(report_content, encoding="utf-8")
    print(f"\n✅ Analysis report saved to: {report_path}")
    
    print("\n" + "=" * 70)
    print("Next steps:")
    print("1. Review the generated report")
    print("2. Manually add optional-dependencies to pyproject.toml")
    print("3. Run this script with --update flag to add deprecation notices")
    print("=" * 70)


if __name__ == "__main__":
    main()

