from pathlib import Path
import os


from codomyrmex.logging_monitoring import get_logger























































"""Core functionality module

"""Core functionality module

This module provides audit_structure functionality including:
- 2 functions: is_python_module, check_structure
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module provides audit_structure functionality including:
- 2 functions: is_python_module, check_structure
- 0 classes: 

Usage:
    # Example usage here
"""
def is_python_module(path):
    """Brief description of is_python_module.

Args:
    path : Description of path

    Returns: Description of return value
"""
    return (path / "__init__.py").exists()

def check_structure(root_path):
    """Brief description of check_structure.

Args:
    root_path : Description of root_path

    Returns: Description of return value
"""
    root = Path(root_path)
    modules = []
    errors = []

    # Walk valid python modules
    for dirpath, dirnames, filenames in os.walk(root):
        path = Path(dirpath)
        
        # Skip hidden, venv, tests, templates, and pycache
        if any(part.startswith('.') for part in path.parts) or \
           '__pycache__' in path.parts or \
           'tests' in path.parts or \
           'template' in path.parts or \
           'egg-info' in str(path):
            continue

        if is_python_module(path):
            modules.append(path)
            
            # 1. Check for Trinity Files
            missing = []
            if not (path / "README.md").exists(): missing.append("README.md")
            if not (path / "SPEC.md").exists(): missing.append("SPEC.md")
            if not (path / "AGENTS.md").exists(): missing.append("AGENTS.md")
            
            if missing:
                errors.append(f"MISSING FILES in {path.relative_to(root)}: {', '.join(missing)}")
            
            # 2. Check AGENTS.md structure if it exists
            agents_file = path / "AGENTS.md"
            if agents_file.exists():
                with open(agents_file, 'r') as f:
                    content = f.read()
                    if "- **Parent**:" not in content:
                        errors.append(f"BAD SIGNPOSTING in {path.relative_to(root)}/AGENTS.md: Missing '**Parent**:' link")
                    if "- **Self**:" not in content:
                        errors.append(f"BAD SIGNPOSTING in {path.relative_to(root)}/AGENTS.md: Missing '**Self**:' link")
                    
                    # Verify functional spec link
                    if "[Functional Spec](SPEC.md)" not in content and "(SPEC.md)" not in content:
                         errors.append(f"MISSING SPEC LINK in {path.relative_to(root)}/AGENTS.md")

    return modules, errors

if __name__ == "__main__":
    root = Path("src/codomyrmex")
    if not root.exists():
        root = Path(".") # Fallback for running from different cwd
        
    print(f"Scanning for documentation structure in {root.absolute()}...")
    modules, errors = check_structure(root)
    
    print(f"\nScanned {len(modules)} Python modules.")
    
    if errors:
        print(f"\nFOUND {len(errors)} STRUCTURAL ISSUES:")
        for e in errors:
            print(f"[FAIL] {e}")
        exit(1)
    else:
        print("\n[SUCCESS] All modules contain specific documentation and signposting!")
        exit(0)
