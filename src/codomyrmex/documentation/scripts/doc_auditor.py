from pathlib import Path
import os

from doc_auditor import FunctionName, ClassName








"""Core functionality module

This module provides doc_auditor functionality including:
- 1 functions: audit_docs
- 0 classes: 

Usage:
    # Example usage here
"""
def audit_docs(root_dir):
    """Brief description of audit_docs.

Args:
    root_dir : Description of root_dir

    Returns: Description of return value
"""
    root = Path(root_dir)
    missing_docs = []
    
    for path in root.rglob("*"):
        if path.is_dir() and not path.name.startswith(('.', '__')):
            # Check if it's a python module (has __init__.py) or a significant directory
            if (path / "__init__.py").exists() or (path.parent.name == "codomyrmex" and path.name != "tests"):
                required = ["README.md", "AGENTS.md", "SPEC.md"]
                for req in required:
                    if not (path / req).exists():
                        missing_docs.append(str(path / req))
    
    return missing_docs

if __name__ == "__main__":
    missing = audit_docs("src/codomyrmex")
    if missing:
        print("Missing Documentation Files:")
        for m in missing:
            print(m)
    else:
        print("No missing documentation files found!")
