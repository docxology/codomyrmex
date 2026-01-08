from pathlib import Path
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""Fix duplicate navigation labels in AGENTS.md files."""


"""Main entry point and utility functions

This module provides fix_duplicate_navigation_labels functionality including:
- 2 functions: fix_duplicate_labels, main
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
def fix_duplicate_labels(content: str) -> str:
    """Fix duplicate navigation labels."""
    # Fix "Parent Directory: Parent Directory" -> "Parent Directory"
    content = re.sub(
        r'\*\*Parent Directory: Parent Directory\*\*:',
        '**Parent Directory**:',
        content
    )
    
    # Fix "Project Root: Project Root" -> "Project Root"
    content = re.sub(
        r'\*\*Project Root: Project Root\*\*:',
        '**Project Root**:',
        content
    )
    
    return content

def main():
    """Fix duplicate labels in all AGENTS.md files."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    for agents_file in base_path.rglob("AGENTS.md"):
        try:
            content = agents_file.read_text(encoding='utf-8')
            original = content
            
            content = fix_duplicate_labels(content)
            
            if content != original:
                agents_file.write_text(content, encoding='utf-8')
                fixed_count += 1
                print(f"Fixed: {agents_file.relative_to(base_path)}")
        except Exception as e:
            print(f"Error processing {agents_file}: {e}")
    
    print(f"\nCompleted: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()

