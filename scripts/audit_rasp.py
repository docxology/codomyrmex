#!/usr/bin/env python3
"""
Audit RASP (README, AGENTS, SPEC, PAI) documentation breadth.
Scans all submodules in src/codomyrmex and reports missing files.
"""

import os
from pathlib import Path
from typing import List, Set, Dict
import sys

# Define the expected RASP files
RASP_FILES = {"README.md", "AGENTS.md", "SPEC.md", "PAI.md"}

def get_submodules(base_path: Path) -> List[Path]:
    """
    Get all subdirectories in the base path that contain an __init__.py file.
    """
    submodules = []
    if not base_path.exists():
        print(f"Error: Base path {base_path} does not exist.")
        return []

    for item in base_path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            submodules.append(item)
            # Recursively check for nested submodules if needed? 
            # For now, let's stick to top-level modules or walk deeply?
            # The prompt implies "all 78 modules", so likely deep traversal is needed.
            # But let's start with direct children and maybe recursive if they are packages.
            
    # Let's do a os.walk to find all packages
    all_packages = []
    for root, dirs, files in os.walk(base_path):
        if "__init__.py" in files:
            all_packages.append(Path(root))
    
    return all_packages

def audit_module(module_path: Path) -> List[str]:
    """
    Check for RASP files in a module directory.
    Returns a list of missing files.
    """
    missing = []
    for rasp_file in RASP_FILES:
        if not (module_path / rasp_file).exists():
            missing.append(rasp_file)
    return missing

def main():
    base_dir = Path("src/codomyrmex")
    if not base_dir.exists():
        # Fallback if running from root
        base_dir = Path.cwd() / "src/codomyrmex"
    
    # Check if we are in the right place
    if not base_dir.exists():
        print(f"Critical Error: Could not find src/codomyrmex at {base_dir}")
        sys.exit(1)

    print(f"Auditing RASP documentation in {base_dir}...\n")
    
    packages = get_submodules(base_dir)
    report: Dict[str, List[str]] = {}
    
    for pkg in packages:
        # Skip internal utility dirs if they don't look like semantic modules
        # For now, audit everything with __init__.py
        missing = audit_module(pkg)
        rel_path = pkg.relative_to(base_dir.parent) # e.g. codomyrmex/utils
        
        # We might want to skip the top level 'codomyrmex' if it's just the entry point,
        # but it definitely should have RASP too if it's the main package.
        
        if missing:
            report[str(rel_path)] = missing

    # Print Report
    if not report:
        print("✅ SUCCESS: All modules have complete RASP documentation!")
        sys.exit(0)
        
    print(f"❌ FOUND ISSUES: {len(report)} modules are missing RASP files.")
    print("-" * 60)
    print(f"{'Module':<40} | {'Missing Files'}")
    print("-" * 60)
    
    sorted_modules = sorted(report.keys())
    for mod in sorted_modules:
        missing_str = ", ".join(sorted(report[mod]))
        print(f"{mod:<40} | {missing_str}")
    
    print("-" * 60)
    print(f"\nTotal modules audited: {len(packages)}")
    sys.exit(1)

if __name__ == "__main__":
    main()
