#!/usr/bin/env python3
"""Identify and report test files using mocks that need to be fixed."""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import re
from pathlib import Path
from collections import defaultdict

def analyze_test_file(file_path: Path) -> dict:
    """Analyze a test file for mock usage."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        issues = {
            'mocks_found': [],
            'mock_imports': [],
            'mock_usage': []
        }
        
        # Check for mock imports
        mock_import_patterns = [
            (r'from unittest\.mock import (.+)', 'unittest.mock import'),
            (r'from unittest import mock', 'unittest import mock'),
            (r'import mock', 'import mock'),
            (r'from mock import (.+)', 'mock import'),
        ]
        
        for pattern, description in mock_import_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                issues['mock_imports'].append({
                    'line': content[:match.start()].count('\n') + 1,
                    'pattern': description,
                    'match': match.group(0)
                })
        
        # Check for mock usage
        mock_usage_patterns = [
            (r'@patch\(', 'patch decorator'),
            (r'@mock\.', 'mock decorator'),
            (r'MagicMock\(', 'MagicMock'),
            (r'Mock\(', 'Mock'),
            (r'patch\(', 'patch function'),
            (r'\.return_value\s*=', 'mock return_value'),
            (r'\.side_effect\s*=', 'mock side_effect'),
        ]
        
        for pattern, description in mock_usage_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()
                issues['mock_usage'].append({
                    'line': line_num,
                    'pattern': description,
                    'context': line_content[:100]
                })
        
        return issues
    except Exception as e:
        return {'error': str(e)}

def main():
    """Analyze all test files for mock usage."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    testing_dir = base_path / "testing" / "unit"
    
    results = defaultdict(list)
    
    for test_file in testing_dir.rglob("test_*.py"):
        rel_path = str(test_file.relative_to(base_path))
        issues = analyze_test_file(test_file)
        
        if issues.get('mock_imports') or issues.get('mock_usage'):
            results['files_with_mocks'].append({
                'file': rel_path,
                'imports': len(issues.get('mock_imports', [])),
                'usage': len(issues.get('mock_usage', []))
            })
    
    print(f"\n=== MOCK USAGE ANALYSIS ===")
    print(f"Files using mocks: {len(results['files_with_mocks'])}\n")
    
    for item in sorted(results['files_with_mocks'], key=lambda x: x['imports'] + x['usage'], reverse=True):
        print(f"{item['file']}:")
        print(f"  Mock imports: {item['imports']}")
        print(f"  Mock usage: {item['usage']}")
        print()
    
    print("\n⚠️  These files need to be refactored to use real implementations instead of mocks.")

if __name__ == "__main__":
    main()
