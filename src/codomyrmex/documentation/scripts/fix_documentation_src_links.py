from pathlib import Path
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""Fix src/README.md links in documentation subdirectories."""


"""Main entry point and utility functions

This module provides fix_documentation_src_links functionality including:
- 2 functions: fix_src_links, main
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
def fix_src_links(file_path: Path) -> bool:
    """Fix links to src/README.md."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Fix ../../../src/README.md - calculate correct depth
        # From src/codomyrmex/documentation/*, src/README.md is at ../../src/README.md
        # But the pattern might vary, so let's be more specific
        content = re.sub(
            r'\[src\]\(\.\./\.\./\.\./src/README\.md\)',
            r'[src](../../src/README.md)',
            content
        )
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix src links in documentation directory."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    doc_dir = base_path / "src/codomyrmex/documentation"
    fixed_count = 0
    
    for readme in doc_dir.rglob("README.md"):
        if fix_src_links(readme):
            fixed_count += 1
            print(f"Fixed: {readme.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()

