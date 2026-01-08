from pathlib import Path
import re
import sys


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""
"""Core functionality module

This module provides fix_tutorial_references functionality including:
- 1 functions: fix_tutorial_references
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
Fix broken references in example_tutorial.md files.

Updates references to API_SPECIFICATION.md and USAGE_EXAMPLES.md
to point to existing files or remove references if files don't exist.
"""



def fix_tutorial_references():
    """Fix broken references in tutorial files."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Find all example_tutorial.md files
    tutorial_files = list(repo_root.rglob('**/example_tutorial.md'))
    
    print(f"Fixing references in {len(tutorial_files)} tutorial files...\n")
    
    fixed_count = 0
    
    for tutorial_file in tutorial_files:
        try:
            content = tutorial_file.read_text(encoding='utf-8')
            module_path = tutorial_file.parent.parent.parent  # Go up from docs/tutorials/example_tutorial.md
            
            # Check what files exist
            api_spec_exists = (module_path / 'API_SPECIFICATION.md').exists()
            usage_examples_exists = (module_path / 'USAGE_EXAMPLES.md').exists()
            readme_exists = (module_path / 'README.md').exists()
            
            original_content = content
            
            # Fix API_SPECIFICATION.md references
            if '../API_SPECIFICATION.md' in content:
                if api_spec_exists:
                    # Keep the reference
                    pass
                else:
                    # Replace with README link or remove
                    if readme_exists:
                        content = content.replace(
                            '../API_SPECIFICATION.md',
                            '../README.md#api-reference'
                        )
                    else:
                        # Remove the reference line
                        content = re.sub(
                            r'\[.*?\]\(\.\./API_SPECIFICATION\.md\)[^\n]*\n?',
                            '',
                            content
                        )
            
            # Fix USAGE_EXAMPLES.md references
            if '../USAGE_EXAMPLES.md' in content:
                if usage_examples_exists:
                    # Keep the reference
                    pass
                else:
                    # Replace with README link or remove
                    if readme_exists:
                        content = content.replace(
                            '../USAGE_EXAMPLES.md',
                            '../README.md#usage-examples'
                        )
                    else:
                        # Remove the reference line
                        content = re.sub(
                            r'\[.*?\]\(\.\./USAGE_EXAMPLES\.md\)[^\n]*\n?',
                            '',
                            content
                        )
            
            if content != original_content:
                tutorial_file.write_text(content, encoding='utf-8')
                rel_path = tutorial_file.relative_to(repo_root)
                print(f"✅ Fixed: {rel_path}")
                fixed_count += 1
                
        except Exception as e:
            rel_path = tutorial_file.relative_to(repo_root)
            print(f"❌ Error fixing {rel_path}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} tutorial files")
    return 0


if __name__ == '__main__':
    sys.exit(fix_tutorial_references())

