#!/usr/bin/env python3
"""
Simple import standardization script for Codomyrmex modules.

This script focuses on adding proper exception imports and basic
import standardization without complex regex patterns.
"""

import os
import sys
from pathlib import Path
from typing import List


def get_python_files(src_dir: Path) -> List[Path]:
    """Get all Python module files."""
    py_files = []
    for root, dirs, files in os.walk(src_dir):
        # Skip __pycache__ and .pytest_cache directories
        dirs[:] = [d for d in dirs if not d.startswith(('__pycache__', '.pytest_cache'))]
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(Path(root) / file)
    
    return py_files


def add_exception_imports_if_needed(file_path: Path) -> bool:
    """Add exception imports to files that need them."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {file_path}: encoding issue")
        return False
    
    lines = content.split('\n')
    
    # Check if exceptions are already imported
    has_exception_imports = any(
        'from codomyrmex.exceptions import' in line or
        'from .exceptions import' in line or
        'from ..exceptions import' in line or
        'import codomyrmex.exceptions' in line
        for line in lines
    )
    
    # Check if the file uses exception-like patterns that would benefit from our exceptions
    uses_exceptions = any(
        'raise ' in line or
        'except ' in line or
        'Exception' in line or
        'Error' in line
        for line in lines
        if not line.strip().startswith('#')
    )
    
    # Skip if already has imports or doesn't need them
    if has_exception_imports or not uses_exceptions:
        return False
    
    # Find where to insert exception imports (after other imports)
    insert_index = 0
    import_section_end = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('from ') or stripped.startswith('import '):
            import_section_end = i + 1
        elif stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
            if import_section_end > 0:
                break
    
    # Add exception import after existing imports
    if import_section_end > 0:
        insert_index = import_section_end
    
    # Determine appropriate import path
    src_path = Path('src/codomyrmex')
    if src_path in file_path.parents:
        relative_to_src = file_path.relative_to(src_path)
        depth = len(relative_to_src.parents)
        if relative_to_src.name == '__init__.py':
            depth -= 1
        
        if depth == 0:
            import_line = "from .exceptions import CodomyrmexError"
        elif depth == 1:
            import_line = "from ..exceptions import CodomyrmexError"
        else:
            import_line = "from codomyrmex.exceptions import CodomyrmexError"
    else:
        import_line = "from codomyrmex.exceptions import CodomyrmexError"
    
    # Insert the import
    new_lines = lines[:insert_index] + [import_line] + lines[insert_index:]
    new_content = '\n'.join(new_lines)
    
    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added exception import to {file_path}")
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False


def remove_sys_path_manipulations(file_path: Path) -> bool:
    """Remove or comment out sys.path manipulations."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {file_path}: encoding issue")
        return False
    
    lines = content.split('\n')
    modified = False
    
    for i, line in enumerate(lines):
        if 'sys.path' in line and ('insert' in line or 'append' in line):
            if not line.strip().startswith('#'):
                lines[i] = f"# {line}  # Removed sys.path manipulation"
                modified = True
    
    if modified:
        new_content = '\n'.join(lines)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Removed sys.path manipulations from {file_path}")
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    
    return False


def main():
    """Main function to run import standardization."""
    src_dir = Path('src/codomyrmex')
    
    if not src_dir.exists():
        print(f"Source directory {src_dir} not found!")
        sys.exit(1)
    
    print("Standardizing imports in Codomyrmex modules...")
    
    python_files = get_python_files(src_dir)
    print(f"Found {len(python_files)} Python files")
    
    exception_imports_added = 0
    sys_path_fixes = 0
    
    for file_path in python_files:
        # Skip the exceptions.py file itself
        if file_path.name == 'exceptions.py':
            continue
            
        # Add exception imports if needed
        if add_exception_imports_if_needed(file_path):
            exception_imports_added += 1
        
        # Remove sys.path manipulations
        if remove_sys_path_manipulations(file_path):
            sys_path_fixes += 1
    
    print(f"\nSummary:")
    print(f"- Added exception imports to {exception_imports_added} files")
    print(f"- Fixed sys.path manipulations in {sys_path_fixes} files")
    print("Import standardization complete!")


if __name__ == '__main__':
    main()