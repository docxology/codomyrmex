#!/usr/bin/env python3
"""Verify tests are modular and functional (no mocks, real implementations)."""

import ast
import re
from pathlib import Path
from typing import List, Dict

def check_for_mocks(file_path: Path) -> List[str]:
    """Check if test file uses mocks."""
    issues = []
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Check for mock imports
        mock_patterns = [
            r'from unittest\.mock import',
            r'from unittest import mock',
            r'import mock',
            r'from mock import',
            r'@patch\(',
            r'@mock\.',
            r'MagicMock\(',
            r'Mock\(',
            r'patch\(',
        ]
        
        for pattern in mock_patterns:
            if re.search(pattern, content):
                issues.append(f"Uses mock: {pattern}")
        
        return issues
    except Exception as e:
        return [f"Error reading file: {e}"]

def check_cross_module_dependencies(file_path: Path, base_path: Path) -> List[str]:
    """Check if unit test has cross-module dependencies."""
    issues = []
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        # Get module name from file path
        rel_path = file_path.relative_to(base_path)
        if 'unit' in rel_path.parts:
            # Extract module name from test file name
            test_name = file_path.stem
            if test_name.startswith('test_'):
                module_name = test_name[5:]  # Remove 'test_' prefix
                module_name = module_name.replace('_comprehensive', '').replace('_enhanced', '')
            else:
                return issues
        
        # Check imports for cross-module dependencies in unit tests
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('codomyrmex.'):
                    imported_modules = [alias.name for alias in node.names]
                    for imp in imported_modules:
                        # Check if importing from different module
                        if module_name and not imp.startswith(module_name):
                            # This might be a cross-module dependency
                            # But some are OK (like logging_monitoring, exceptions)
                            allowed = ['logging_monitoring', 'exceptions', 'environment_setup']
                            if not any(allowed_mod in node.module for allowed_mod in allowed):
                                issues.append(f"Possible cross-module import: {node.module}.{imp}")
        
        return issues
    except Exception as e:
        return [f"Error parsing file: {e}"]

def main():
    """Verify all tests are modular and functional."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    testing_dir = base_path / "testing" / "unit"
    
    results = {
        'files_with_mocks': [],
        'files_with_cross_module': [],
        'total_files': 0
    }
    
    for test_file in testing_dir.rglob("test_*.py"):
        results['total_files'] += 1
        rel_path = str(test_file.relative_to(base_path))
        
        mock_issues = check_for_mocks(test_file)
        if mock_issues:
            results['files_with_mocks'].append({
                'file': rel_path,
                'issues': mock_issues
            })
        
        cross_module_issues = check_cross_module_dependencies(test_file, base_path)
        if cross_module_issues:
            results['files_with_cross_module'].append({
                'file': rel_path,
                'issues': cross_module_issues
            })
    
    print(f"\n=== MODULAR TESTING VERIFICATION ===")
    print(f"Total test files: {results['total_files']}")
    print(f"Files using mocks: {len(results['files_with_mocks'])}")
    print(f"Files with cross-module dependencies: {len(results['files_with_cross_module'])}")
    
    if results['files_with_mocks']:
        print("\n⚠️  Files using mocks (should use real implementations):")
        for item in results['files_with_mocks'][:10]:
            print(f"  - {item['file']}: {', '.join(item['issues'][:2])}")
    
    if results['files_with_cross_module']:
        print("\n⚠️  Files with cross-module dependencies (should be modular):")
        for item in results['files_with_cross_module'][:10]:
            print(f"  - {item['file']}: {', '.join(item['issues'][:2])}")

if __name__ == "__main__":
    main()

