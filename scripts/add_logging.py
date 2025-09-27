#!/usr/bin/env python3
"""
Add comprehensive logging to all Codomyrmex modules.

This script adds proper logging imports and logger instances
to modules that don't have them yet.
"""

import os
import sys
from pathlib import Path
from typing import List, Set
import re


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


def has_logging_setup(content: str) -> bool:
    """Check if the file already has logging setup."""
    return any(pattern in content for pattern in [
        'import logging',
        'from logging',
        'logger = ',
        'Logger',
        'get_logger'
    ])


def should_add_logging(content: str) -> bool:
    """Determine if this file would benefit from logging."""
    # Skip files that are too small or simple
    lines = content.split('\n')
    non_comment_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    if len(non_comment_lines) < 10:
        return False
    
    # Add logging to files that have functions/classes and would benefit from it
    has_functions = any(
        re.match(r'^\s*def\s+\w+', line) or re.match(r'^\s*class\s+\w+', line)
        for line in lines
    )
    
    has_error_handling = any(
        'raise ' in line or 'except ' in line or 'try:' in line
        for line in lines
        if not line.strip().startswith('#')
    )
    
    has_operations = any(
        pattern in content for pattern in [
            'execute', 'process', 'run', 'build', 'deploy', 'analyze',
            'generate', 'create', 'manager', 'orchestrat', 'monitor'
        ]
    )
    
    return has_functions and (has_error_handling or has_operations)


def add_logging_to_file(file_path: Path) -> bool:
    """Add logging setup to a file that needs it."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {file_path}: encoding issue")
        return False
    
    if has_logging_setup(content) or not should_add_logging(content):
        return False
    
    lines = content.split('\n')
    
    # Find where to insert logging imports (after other imports)
    insert_index = 0
    import_section_end = 0
    docstring_end = 0
    
    # Skip docstrings at the top
    in_multiline_docstring = False
    docstring_delimiter = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Handle multiline docstrings
        if not in_multiline_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_delimiter = '"""' if stripped.startswith('"""') else "'''"
                if not (stripped.endswith(docstring_delimiter) and len(stripped) > 3):
                    in_multiline_docstring = True
                docstring_end = i + 1
        else:
            if docstring_delimiter in line:
                in_multiline_docstring = False
                docstring_end = i + 1
        
        # Track import section
        if stripped.startswith('from ') or stripped.startswith('import '):
            import_section_end = i + 1
        elif stripped and not stripped.startswith('#') and not in_multiline_docstring:
            if import_section_end > 0:
                break
    
    # Determine where to insert logging import
    insert_index = max(docstring_end, import_section_end)
    
    # Create logging import and logger setup
    logging_imports = []
    
    # Add import for logger config
    src_path = Path('src/codomyrmex')
    if src_path in file_path.parents:
        relative_to_src = file_path.relative_to(src_path)
        depth = len(relative_to_src.parents)
        if relative_to_src.name == '__init__.py':
            depth -= 1
        
        if depth == 0:
            logging_imports.append("from .logging_monitoring.logger_config import get_logger")
        elif depth == 1:
            logging_imports.append("from ..logging_monitoring.logger_config import get_logger")
        else:
            logging_imports.append("from codomyrmex.logging_monitoring.logger_config import get_logger")
    else:
        logging_imports.append("from codomyrmex.logging_monitoring.logger_config import get_logger")
    
    # Add logger instance creation
    logger_setup = f"logger = get_logger(__name__)"
    
    # Insert the imports and logger setup
    new_lines = (
        lines[:insert_index] + 
        logging_imports + 
        [''] + 
        [logger_setup] + 
        [''] + 
        lines[insert_index:]
    )
    
    new_content = '\n'.join(new_lines)
    
    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added logging to {file_path}")
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False


def main():
    """Main function to add logging to modules."""
    src_dir = Path('src/codomyrmex')
    
    if not src_dir.exists():
        print(f"Source directory {src_dir} not found!")
        sys.exit(1)
    
    print("Adding comprehensive logging to Codomyrmex modules...")
    
    python_files = get_python_files(src_dir)
    print(f"Found {len(python_files)} Python files")
    
    logging_added = 0
    
    # Skip certain files that don't need logging
    skip_files = {
        'exceptions.py',
        '__init__.py',
        'logger_config.py'
    }
    
    for file_path in python_files:
        if file_path.name in skip_files:
            continue
            
        if add_logging_to_file(file_path):
            logging_added += 1
    
    print(f"\nSummary:")
    print(f"- Added logging to {logging_added} files")
    print("Logging integration complete!")


if __name__ == '__main__':
    main()