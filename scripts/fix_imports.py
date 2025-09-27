#!/usr/bin/env python3
"""
Fix imports across all Codomyrmex modules.

This script updates all Python files to use proper relative imports
and integrates with the new standardized exception system.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def get_module_files(src_dir: Path) -> List[Path]:
    """Get all Python module files."""
    py_files = []
    for root, dirs, files in os.walk(src_dir):
        # Skip __pycache__ and .pytest_cache directories
        dirs[:] = [d for d in dirs if not d.startswith(('__pycache__', '.pytest_cache'))]
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(Path(root) / file)
    
    return py_files


def fix_import_patterns(content: str, file_path: Path) -> str:
    """Fix common import patterns in module files."""
    lines = content.split('\n')
    fixed_lines = []
    in_import_section = True
    
    # Determine module depth for relative imports
    src_path = Path('src/codomyrmex')
    if src_path in file_path.parents:
        relative_to_src = file_path.relative_to(src_path)
        depth = len(relative_to_src.parents) - 1  # -1 because we don't count the file itself
        if relative_to_src.name == '__init__.py':
            depth = len(relative_to_src.parents)
    else:
        depth = 0
    
    relative_prefix = '.' * (depth + 1) if depth >= 0 else ''
    
    for line in lines:
        original_line = line
        
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Check if we're still in import section
        if not (line.startswith('import ') or line.startswith('from ') or 
                line.strip() == '' or line.strip().startswith('#') or
                '"""' in line or "'''" in line):
            in_import_section = False
        
        if in_import_section and ('from ' in line or 'import ' in line):
            # Fix common problematic patterns
            
            # Fix sys.path manipulation patterns
            if 'sys.path' in line and ('insert' in line or 'append' in line):
                # Comment out sys.path manipulations
                fixed_lines.append(f'# {line}  # Fixed: removed sys.path manipulation')
                continue
            
            # Fix PROJECT_ROOT and SCRIPT_DIR patterns
            if any(pattern in line for pattern in ['PROJECT_ROOT', 'SCRIPT_DIR', 'os.path.dirname(os.path.abspath(__file__))']):
                fixed_lines.append(f'# {line}  # Fixed: removed path manipulation')
                continue
            
            # Fix specific module imports to use relative imports
            module_imports = {
                'logging_monitoring': f'{relative_prefix}logging_monitoring',
                'static_analysis': f'{relative_prefix}static_analysis',
                'data_visualization': f'{relative_prefix}data_visualization',
                'code_execution_sandbox': f'{relative_prefix}code_execution_sandbox',
                'git_operations': f'{relative_prefix}git_operations',
                'environment_setup': f'{relative_prefix}environment_setup',
                'project_orchestration': f'{relative_prefix}project_orchestration',
                'performance': f'{relative_prefix}performance',
                'config_management': f'{relative_prefix}config_management',
                'ai_code_editing': f'{relative_prefix}ai_code_editing',
                'exceptions': f'{relative_prefix}exceptions',
            }
            
            # Only apply fixes to imports that look like they're importing from codomyrmex modules
            line_modified = False
            for old_import, new_import in module_imports.items():
                patterns = [
                    f'from {old_import}',
                    f'import {old_import}',
                ]
                
                for pattern in patterns:
                    if pattern in line and not line.strip().startswith('#'):
                        # Make sure it's not already a relative import
                        if not ('from .' in line or 'from codomyrmex.' in line):
                            if f'from {old_import}' in line:
                                line = line.replace(f'from {old_import}', f'from {new_import}')
                                line_modified = True
                            elif f'import {old_import}' == line.strip():
                                line = f'from {new_import} import *'
                                line_modified = True
            
            # Add try-except blocks for relative imports
            if line_modified and 'from .' in line:
                # Create fallback import pattern
                module_name = None
                if 'from .' in line and 'import' in line:
                    import_part = line.split('import')[0].replace('from ', '').strip()
                    if import_part.startswith('.'):
                        # Convert relative import to absolute for fallback
                        module_name = 'codomyrmex.' + import_part.lstrip('.')
                
                if module_name:
                    fixed_lines.append('try:')
                    fixed_lines.append(f'    {line}')
                    fixed_lines.append('except ImportError:')
                    fallback_line = line.replace(import_part, module_name)
                    fixed_lines.append(f'    {fallback_line}')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def add_exception_imports(content: str, file_path: Path) -> str:
    """Add standardized exception imports to modules."""
    lines = content.split('\n')
    
    # Check if exceptions are already imported
    has_exception_imports = any('from .exceptions import' in line or 
                              'from codomyrmex.exceptions import' in line 
                              for line in lines)
    
    if has_exception_imports:
        return content
    
    # Find where to insert exception imports
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_index = i + 1
        elif line.strip() and not line.strip().startswith('#') and not '"""' in line:
            break
    
    # Determine appropriate relative import depth
    src_path = Path('src/codomyrmex')
    if src_path in file_path.parents:
        relative_to_src = file_path.relative_to(src_path)
        depth = len(relative_to_src.parents) - 1
        if relative_to_src.name == '__init__.py':
            depth = len(relative_to_src.parents)
        relative_prefix = '.' * (depth + 1) if depth >= 0 else ''
    else:
        relative_prefix = ''
    
    # Exception imports to add
    exception_imports = f'''
# Import standardized exceptions
try:
    from {relative_prefix}exceptions import (
        CodomyrmexError,
        ConfigurationError,
        FileOperationError,
        ValidationError,
        create_error_context,
    )
except ImportError:
    try:
        from codomyrmex.exceptions import (
            CodomyrmexError,
            ConfigurationError,
            FileOperationError,
            ValidationError,
            create_error_context,
        )
    except ImportError:
        # Fallback to standard exceptions
        class CodomyrmexError(Exception):
            pass
        class ConfigurationError(Exception):
            pass
        class FileOperationError(Exception):
            pass  
        class ValidationError(Exception):
            pass
        def create_error_context(**kwargs):
            return kwargs
'''
    
    # Only add if the file looks like it might benefit from exceptions
    content_lower = content.lower()
    needs_exceptions = any(keyword in content_lower for keyword in [
        'raise ', 'except ', 'error', 'exception', 'validate', 'config'
    ])
    
    if needs_exceptions and '__init__.py' not in str(file_path):
        lines.insert(insert_index, exception_imports)
    
    return '\n'.join(lines)


def fix_type_hints(content: str) -> str:
    """Fix deprecated type hints to use modern syntax."""
    # Replace deprecated typing imports
    content = re.sub(r'from typing import ([^\\n]*?)Dict([^\\n]*?)\\n', 
                    r'from typing import \\1\\2\\n', content)
    content = re.sub(r'from typing import ([^\\n]*?)List([^\\n]*?)\\n', 
                    r'from typing import \\1\\2\\n', content)
    
    # Replace Dict with dict
    content = re.sub(r'\\bDict\\[', 'dict[', content)
    # Replace List with list
    content = re.sub(r'\\bList\\[', 'list[', content)
    
    return content


def apply_code_formatting(content: str) -> str:
    """Apply basic code formatting improvements."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip()
        
        # Fix common spacing issues in imports
        if line.startswith('from ') and ' import ' in line:
            parts = line.split(' import ')
            if len(parts) == 2:
                from_part = parts[0].strip()
                import_part = parts[1].strip()
                line = f'{from_part} import {import_part}'
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix a single Python file."""
    changes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Apply all fixes
        content = original_content
        
        # Fix import patterns
        new_content = fix_import_patterns(content, file_path)
        if new_content != content:
            changes.append('Fixed import patterns')
            content = new_content
        
        # Add exception imports where needed
        new_content = add_exception_imports(content, file_path)
        if new_content != content:
            changes.append('Added exception imports')
            content = new_content
        
        # Fix type hints
        new_content = fix_type_hints(content)
        if new_content != content:
            changes.append('Updated type hints')
            content = new_content
        
        # Apply code formatting
        new_content = apply_code_formatting(content)
        if new_content != content:
            changes.append('Applied code formatting')
            content = new_content
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        
        return False, []
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, [f"Error: {e}"]


def main():
    """Main function to fix imports across all modules."""
    src_dir = Path('src/codomyrmex')
    
    if not src_dir.exists():
        print(f"Source directory {src_dir} not found!")
        sys.exit(1)
    
    print("Fixing imports across all Codomyrmex modules...")
    
    # Get all Python files
    py_files = get_module_files(src_dir)
    
    # Track changes
    total_files = len(py_files)
    changed_files = 0
    total_changes = []
    
    for file_path in py_files:
        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            relative_path = file_path
        print(f"Processing: {relative_path}")
        
        changed, changes = fix_file(file_path)
        if changed:
            changed_files += 1
            print(f"  ✓ Changed: {', '.join(changes)}")
            total_changes.extend(changes)
        else:
            print("  - No changes needed")
    
    # Summary
    print(f"\\nSummary:")
    print(f"  Files processed: {total_files}")
    print(f"  Files changed: {changed_files}")
    print(f"  Total changes: {len(total_changes)}")
    
    # Change type summary
    change_types = {}
    for change in total_changes:
        change_types[change] = change_types.get(change, 0) + 1
    
    if change_types:
        print(f"\\nChange types:")
        for change_type, count in change_types.items():
            print(f"  {change_type}: {count}")


if __name__ == '__main__':
    main()