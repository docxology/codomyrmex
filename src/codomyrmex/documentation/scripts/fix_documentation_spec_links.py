from pathlib import Path
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""Fix broken SPEC.md links in documentation subdirectories."""


"""Main entry point and utility functions

This module provides fix_documentation_spec_links functionality including:
- 3 functions: calculate_correct_path, fix_spec_links, main
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
def calculate_correct_path(from_file: Path, base_path: Path) -> str:
    """Calculate correct relative path from documentation SPEC to module SPEC."""
    # From: src/codomyrmex/documentation/docs/modules/{module}/SPEC.md
    # To: src/codomyrmex/{module}/SPEC.md
    
    # Get the module name from the path
    module_name = from_file.parent.name
    
    # Calculate depth from root
    rel_path = from_file.parent.relative_to(base_path)
    depth = len(rel_path.parts)
    
    # Build correct path: go up depth levels, then to src/codomyrmex/{module}/SPEC.md
    return "../" * depth + f"src/codomyrmex/{module_name}/SPEC.md"

def fix_spec_links(file_path: Path, base_path: Path) -> bool:
    """Fix SPEC.md links in a file."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Calculate correct path
        correct_path = calculate_correct_path(file_path, base_path)
        
        # Fix the link pattern [src/codomyrmex/{module}/SPEC.md](../../../../../{module}/SPEC.md)
        # Match various incorrect patterns
        module_name = file_path.parent.name
        patterns = [
            (rf'\[src/codomyrmex/{re.escape(module_name)}/SPEC\.md\]\(\.\./\.\./\.\./\.\./\.\./\.\./{re.escape(module_name)}/SPEC\.md\)', 
             f'[src/codomyrmex/{module_name}/SPEC.md]({correct_path})'),
            (rf'\[src/codomyrmex/{re.escape(module_name)}/SPEC\.md\]\(\.\./\.\./\.\./\.\./\.\./{re.escape(module_name)}/SPEC\.md\)', 
             f'[src/codomyrmex/{module_name}/SPEC.md]({correct_path})'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix SPEC links in documentation directory."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    doc_dir = base_path / "src/codomyrmex/documentation/docs/modules"
    fixed_count = 0
    
    for spec_file in doc_dir.rglob("SPEC.md"):
        if fix_spec_links(spec_file, base_path):
            fixed_count += 1
            print(f"Fixed: {spec_file.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()

