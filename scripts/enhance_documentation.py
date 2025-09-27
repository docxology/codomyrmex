#!/usr/bin/env python3
"""
Enhance documentation across all Codomyrmex modules.

This script adds proper docstrings to functions and classes
that are missing them, improving code documentation quality.
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re


class DocumentationEnhancer(ast.NodeVisitor):
    """AST visitor to analyze and enhance documentation."""
    
    def __init__(self):
        self.missing_docs = []
        self.current_file = None
        self.lines = []
        self.modifications = []
    
    def set_file_context(self, file_path: Path, content: str):
        """Set the current file context."""
        self.current_file = file_path
        self.lines = content.split('\n')
        self.missing_docs = []
        self.modifications = []
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions."""
        self._check_docstring(node, 'function')
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definitions."""
        self._check_docstring(node, 'async function')
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions."""
        self._check_docstring(node, 'class')
        self.generic_visit(node)
    
    def _check_docstring(self, node, node_type):
        """Check if a node has a docstring and suggest one if missing."""
        docstring = ast.get_docstring(node)
        
        # Skip private methods and special methods unless they're important
        if node.name.startswith('_') and not node.name.startswith('__'):
            return
        
        # Skip very short functions (likely simple getters/setters)
        if node_type == 'function' and len(node.body) <= 2:
            return
            
        if not docstring:
            # Generate a basic docstring template
            suggested_docstring = self._generate_docstring_template(node, node_type)
            
            self.missing_docs.append({
                'type': node_type,
                'name': node.name,
                'line': node.lineno,
                'suggested_docstring': suggested_docstring
            })
    
    def _generate_docstring_template(self, node, node_type):
        """Generate a basic docstring template."""
        if node_type == 'class':
            return f'"""{node.name.replace("_", " ").title()}.\n\n    A class for handling {node.name.lower()} operations.\n    """'
        
        # For functions, analyze parameters and return type
        args = []
        if hasattr(node, 'args'):
            args = [arg.arg for arg in node.args.args if arg.arg != 'self']
        
        docstring_parts = [f'"""{node.name.replace("_", " ").title()}.']
        
        if args:
            docstring_parts.append('\n\n    Args:')
            for arg in args:
                # Make educated guesses about parameter purpose
                purpose = self._guess_parameter_purpose(arg)
                docstring_parts.append(f'        {arg}: {purpose}')
        
        # Check if function likely returns something
        has_return = self._has_return_statement(node)
        if has_return:
            docstring_parts.append('\n\n    Returns:')
            docstring_parts.append('        The result of the operation.')
        
        docstring_parts.append('\n    """')
        
        return ''.join(docstring_parts)
    
    def _guess_parameter_purpose(self, param_name: str) -> str:
        """Make educated guesses about parameter purposes."""
        param_lower = param_name.lower()
        
        if 'path' in param_lower or 'file' in param_lower:
            return 'Path to the file or directory.'
        elif 'name' in param_lower:
            return 'Name identifier.'
        elif 'config' in param_lower:
            return 'Configuration settings.'
        elif 'data' in param_lower:
            return 'Data to process.'
        elif 'options' in param_lower or 'params' in param_lower:
            return 'Additional options or parameters.'
        elif 'url' in param_lower:
            return 'URL endpoint.'
        elif 'id' in param_lower:
            return 'Unique identifier.'
        elif 'key' in param_lower:
            return 'Key for identification or access.'
        elif 'value' in param_lower:
            return 'Value to be processed.'
        else:
            return 'Parameter for the operation.'
    
    def _has_return_statement(self, node) -> bool:
        """Check if a function has return statements with values."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
        return False


def add_docstrings_to_file(file_path: Path) -> bool:
    """Add missing docstrings to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {file_path}: encoding issue")
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    # Skip files that are too small or are test files
    if len(content) < 500:
        return False
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"Skipping {file_path}: syntax error - {e}")
        return False
    
    enhancer = DocumentationEnhancer()
    enhancer.set_file_context(file_path, content)
    enhancer.visit(tree)
    
    if not enhancer.missing_docs:
        return False
    
    # Apply modifications (add docstrings)
    lines = content.split('\n')
    modifications_made = False
    
    # Sort by line number in reverse order to avoid line number shifts
    for missing_doc in sorted(enhancer.missing_docs, key=lambda x: x['line'], reverse=True):
        line_idx = missing_doc['line'] - 1
        
        # Find the line after the function/class definition
        insert_line = line_idx
        while insert_line < len(lines) and lines[insert_line].strip().endswith(':'):
            insert_line += 1
        
        # Check if there's already a docstring on the next line
        if insert_line < len(lines) and ('"""' in lines[insert_line] or "'''" in lines[insert_line]):
            continue
        
        # Insert the docstring with proper indentation
        base_indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
        indent = ' ' * (base_indent + 4)  # Add extra indentation for docstring
        
        docstring_lines = missing_doc['suggested_docstring'].split('\n')
        indented_docstring = []
        for i, ds_line in enumerate(docstring_lines):
            if i == 0:
                indented_docstring.append(indent + ds_line)
            else:
                indented_docstring.append(indent + ds_line if ds_line.strip() else '')
        
        # Insert the docstring
        for i, ds_line in enumerate(reversed(indented_docstring)):
            lines.insert(insert_line, ds_line)
        
        modifications_made = True
    
    if modifications_made:
        new_content = '\n'.join(lines)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Enhanced documentation in {file_path} ({len(enhancer.missing_docs)} docstrings added)")
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
    """Main function to enhance documentation."""
    src_dir = Path('src/codomyrmex')
    
    if not src_dir.exists():
        print(f"Source directory {src_dir} not found!")
        sys.exit(1)
    
    print("Enhancing documentation in Codomyrmex modules...")
    
    python_files = get_python_files(src_dir)
    print(f"Found {len(python_files)} Python files")
    
    documentation_enhanced = 0
    
    # Skip certain files
    skip_files = {
        '__init__.py',  # Usually simple
        'exceptions.py',  # Already well documented
    }
    
    for file_path in python_files:
        if file_path.name in skip_files:
            continue
            
        if add_docstrings_to_file(file_path):
            documentation_enhanced += 1
    
    print(f"\nSummary:")
    print(f"- Enhanced documentation in {documentation_enhanced} files")
    print("Documentation enhancement complete!")


if __name__ == '__main__':
    main()