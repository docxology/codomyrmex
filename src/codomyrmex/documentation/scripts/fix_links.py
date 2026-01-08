from pathlib import Path
import os
import re


from codomyrmex.logging_monitoring import get_logger





























































"""Core functionality module

"""Core functionality module

This module provides fix_links functionality including:
- 1 functions: fix_documentation
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module provides fix_links functionality including:
- 1 functions: fix_documentation
- 0 classes: 

Usage:
    # Example usage here
"""
def fix_documentation(root_dir):
    """Brief description of fix_documentation.

Args:
    root_dir : Description of root_dir

    Returns: Description of return value
"""
    root_path = Path(root_dir).absolute()
    
    # regexes
    example_tutorial_pattern = re.compile(r'- \[Example Tutorial\]\(\./tutorials/example_tutorial\.md\)\n?')
    contributing_pattern = re.compile(r'\[Contributing Guidelines\]\(\.\./\.\./\.\./\.\./\.\./\.\./docs/project/contributing\.md\)')
    
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith(".md"):
                filepath = Path(root) / file
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Fix example tutorial links
                new_content = example_tutorial_pattern.sub('', content)
                
                # Fix contributing links (add one more level or fix relative path)
                # For files in src/codomyrmex/documentation/docs/modules/*/docs/index.md
                if "src/codomyrmex/documentation/docs/modules" in str(filepath):
                    depth = len(filepath.relative_to(root_path).parts) - 1
                    dots = "../" * depth
                    new_contributing = f"[Contributing Guidelines]({dots}docs/project/contributing.md)"
                    # This is a bit complex to do with regex if there are many different depths, 
                    # but most are at the same depth.
                    # Let's just do a generic replacement if it matches the broken one.
                    new_content = new_content.replace("../../../../../../docs/project/contributing.md", "../../../../../../../docs/project/contributing.md")
                
                if new_content != content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Fixed {filepath.relative_to(root_path)}")

if __name__ == "__main__":
    fix_documentation(os.getcwd())
