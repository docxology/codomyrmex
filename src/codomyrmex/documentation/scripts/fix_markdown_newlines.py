#!/usr/bin/env python3
"""
This module provides fix_markdown_newlines functionality including:
- 1 functions: fix_newlines
- 0 classes: 

Usage:
    # Example usage here
"""
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def fix_newlines(directory):
    """Brief description of fix_newlines.

Args:
    directory : Description of directory

    Returns: Description of return value
"""
    for root, dirs, files in os.walk(directory):
        if any(exclude in root for exclude in ['.git', 'venv', 'node_modules', '__pycache__']):
            continue
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if '\\n' in content:
                        print(f"Fixing {path}")
                        # Be careful not to replace legitimate code examples that might have \\n
                        # But in this case, the whole file is likely one line.
                        # The doc_scaffolder bug writes the whole file with \\n instead of \n
                        new_content = content.replace('\\n', '\n')
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    fix_newlines(".")
