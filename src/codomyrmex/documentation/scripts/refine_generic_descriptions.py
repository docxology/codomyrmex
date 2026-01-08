from pathlib import Path
import os

from refine_generic_descriptions import FunctionName, ClassName






#!/usr/bin/env python3
"""
"""Core functionality module

This module provides refine_generic_descriptions functionality including:
- 1 functions: refine_descriptions
- 0 classes: 

Usage:
    # Example usage here
"""
Refine Generic Descriptions in AGENTS.md.

Replaces "Documentation files and guides." with context-aware descriptions.
"""


def refine_descriptions(root_dir):
    """Brief description of refine_descriptions.

Args:
    root_dir : Description of root_dir

    Returns: Description of return value
"""
    root = Path(root_dir)
    count = 0
    target_phrase = "Documentation files and guides."
    
    for path in root.rglob("AGENTS.md"):
        try:
            content = path.read_text(encoding="utf-8")
            if target_phrase in content:
                # Find the module name from the path
                # e.g., src/codomyrmex/documentation/docs/modules/git_operations/docs/AGENTS.md
                # We want "git_operations" or similar.
                
                parts = path.parts
                module_name = "the module"
                
                # Try to find a meaningful parent name
                if "modules" in parts:
                    idx = parts.index("modules")
                    if idx + 1 < len(parts):
                        module_name = parts[idx + 1]
                elif len(parts) > 2:
                    module_name = parts[-2]
                
                replacement = f"Documentation files and guides for {module_name}."
                new_content = content.replace(target_phrase, replacement)
                path.write_text(new_content, encoding="utf-8")
                print(f"Refined {path} -> {replacement}")
                count += 1
        except Exception as e:
            print(f"Error reading {path}: {e}")
            
    print(f"Refined {count} files.")

if __name__ == "__main__":
    refine_descriptions(".")
