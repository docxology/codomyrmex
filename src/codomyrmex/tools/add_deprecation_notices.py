from pathlib import Path
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""Add deprecation notices to all requirements.txt files."""



"""Main entry point and utility functions

This module provides add_deprecation_notices functionality including:
- 4 functions: get_module_name, get_dependency_location, add_deprecation_notice...
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
def get_module_name(file_path: Path) -> str:
    """Extract module name from file path."""
    match = re.search(r"codomyrmex/([^/]+)/requirements\.txt", str(file_path))
    if match:
        return match.group(1)
    return "unknown"


def get_dependency_location(module_name: str) -> str:
    """Determine where dependencies are located in pyproject.toml."""
    # Modules with optional dependencies
    optional_deps = {
        "code_review", "llm", "spatial.three_d", "performance",
        "physical_management", "security", "static_analysis"
    }
    
    if module_name in optional_deps:
        return f"pyproject.toml [project.optional-dependencies.{module_name}]"
    else:
        return "pyproject.toml [project.dependencies]"


def add_deprecation_notice(file_path: Path) -> None:
    """Add deprecation notice to requirements.txt file."""
    module_name = get_module_name(file_path)
    location = get_dependency_location(module_name)
    
    notice = f"""# DEPRECATED: This file is deprecated and will be removed in a future version.
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
# Migration completed: {location}
#
"""
    
    # Read existing content
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        
        # Check if already has deprecation notice
        if content.startswith("# DEPRECATED"):
            print(f"  ✓ {file_path.name} already has deprecation notice")
            return
        
        # Add notice at the beginning, keep original content commented
        lines = content.splitlines()
        commented_lines = []
        for line in lines:
            if line.strip() and not line.strip().startswith("#"):
                commented_lines.append(f"# {line}")
            else:
                commented_lines.append(line)
        
        new_content = notice + "\n# --- Legacy content (for reference only) ---\n"
        if commented_lines:
            new_content += "\n".join(commented_lines) + "\n"
        
        file_path.write_text(new_content, encoding="utf-8")
        print(f"  ✓ Updated {file_path.name}")
    else:
        print(f"  ⚠ {file_path.name} does not exist")


def main():
    """Main function."""
    root = Path(__file__).parent.parent.parent.parent
    codomyrmex_dir = root / "src" / "codomyrmex"
    
    requirements_files = []
    for module_dir in sorted(codomyrmex_dir.iterdir()):
        if module_dir.is_dir():
            req_file = module_dir / "requirements.txt"
            if req_file.exists():
                requirements_files.append(req_file)
    
    print(f"Found {len(requirements_files)} requirements.txt files")
    print("Adding deprecation notices...\n")
    
    for req_file in requirements_files:
        add_deprecation_notice(req_file)
    
    print("\n✅ All deprecation notices added!")


if __name__ == "__main__":
    main()

