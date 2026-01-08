import os
import re


from codomyrmex.logging_monitoring import get_logger





























































"""Core functionality module

"""Core functionality module

This module provides fix_src_doubling functionality including:
- 1 functions: fix_src_doubling
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module provides fix_src_doubling functionality including:
- 1 functions: fix_src_doubling
- 0 classes: 

Usage:
    # Example usage here
"""
def fix_src_doubling(directory):
    # Matches [label](.../src/README.md)
    # We want to change it to [label](.../README.md)
    """Brief description of fix_src_doubling.

Args:
    directory : Description of directory

    Returns: Description of return value
"""
    pattern = re.compile(r'\[([^\]]+)\]\(((\.\./)+)src/README\.md\)')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = pattern.sub(r'[\1](\2README.md)', content)
                    
                    if new_content != content:
                        print(f"Fixing src doubling in {path}")
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    # Target the documentation module's docs
    fix_src_doubling("src/codomyrmex/documentation/docs/")
    # Also check the root docs
    fix_src_doubling("docs/")
