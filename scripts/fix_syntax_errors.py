#!/usr/bin/env python3
"""
Fix syntax errors in Codomyrmex modules.

This script identifies and fixes common syntax errors that may have been
introduced during import standardization.
"""

import ast
import os
import sys
from pathlib import Path
from typing import List
import re


def fix_empty_if_blocks(content: str) -> str:
    """Fix empty if blocks that cause syntax errors."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if (line.strip().startswith('if ') and line.strip().endswith(':')) or \
           (line.strip().startswith('elif ') and line.strip().endswith(':')) or \
           (line.strip().startswith('else:')) or \
           (line.strip().startswith('try:')) or \
           (line.strip().startswith('except ') and line.strip().endswith(':')) or \
           (line.strip().startswith('finally:')):
            
            # Check if the next line is indented or if it's an empty block
            next_line_idx = i + 1
            while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                next_line_idx += 1
            
            # If there's no next line or next line is not indented, add pass
            if (next_line_idx >= len(lines) or 
                len(lines[next_line_idx]) - len(lines[next_line_idx].lstrip()) <= len(line) - len(line.lstrip())):
                fixed_lines.append(line)
                # Add pass statement with proper indentation
                indent = ' ' * (len(line) - len(line.lstrip()) + 4)
                fixed_lines.append(indent + 'pass')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_import_syntax_errors(content: str) -> str:
    """Fix import-related syntax errors."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix logger import conflicts
        if 'from .logging_monitoring.logger_config import get_logger' in line:
            # Make sure this import is not duplicate
            if not any('get_logger' in prev_line for prev_line in fixed_lines[-5:]):
                fixed_lines.append(line)
        elif 'from ..logging_monitoring.logger_config import get_logger' in line:
            if not any('get_logger' in prev_line for prev_line in fixed_lines[-5:]):
                fixed_lines.append(line)
        elif 'logger = get_logger(__name__)' in line:
            # Make sure logger is not already defined
            if not any('logger = ' in prev_line and 'get_logger' in prev_line for prev_line in fixed_lines):
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_syntax_in_file(file_path: Path) -> bool:
    """Fix syntax errors in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {file_path}: encoding issue")
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    original_content = content
    
    # Apply fixes
    content = fix_empty_if_blocks(content)
    content = fix_import_syntax_errors(content)
    
    # Check if content was modified
    if content != original_content:
        # Verify the fixed content is syntactically valid
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"Syntax error still present in {file_path}: {e}")
            return False
        
        # Write back the fixed content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed syntax errors in {file_path}")
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False
    
    return False


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


def main():
    """Main function to fix syntax errors."""
    src_dir = Path('src/codomyrmex')
    
    if not src_dir.exists():
        print(f"Source directory {src_dir} not found!")
        sys.exit(1)
    
    print("Fixing syntax errors in Codomyrmex modules...")
    
    python_files = get_python_files(src_dir)
    print(f"Found {len(python_files)} Python files")
    
    syntax_fixes = 0
    
    for file_path in python_files:
        if fix_syntax_in_file(file_path):
            syntax_fixes += 1
    
    print(f"\nSummary:")
    print(f"- Fixed syntax errors in {syntax_fixes} files")
    print("Syntax error fixing complete!")


if __name__ == '__main__':
    main()