#!/usr/bin/env python3
"""
Error Handling Pattern Audit Script

This script reviews error handling patterns across all modules to identify
inconsistencies and ensure standardization.
"""

if __name__ == "__main__":
    import ast
    import re
    from pathlib import Path
    from typing import List, Dict, Tuple, Any
    import json
    from dataclasses import dataclass, asdict
    import sys


    @dataclass
    class ErrorHandlingPattern:
        """Represents an error handling pattern found in code."""
        file_path: str
        line_number: int
        pattern_type: str  # 'logger_usage', 'exception_raise', 'exception_catch', 'import_pattern'
        details: str
        is_standard: bool = False
        recommendation: str = ""


    def find_python_files(project_root: Path) -> List[Path]:
        """Find all Python files in the project."""
        import os
        python_files = []
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', 'htmlcov', '.mypy_cache', '.ruff_cache', 'build', 'dist'}

        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        return sorted(python_files)


    def audit_logger_usage(tree: ast.AST, file_path: Path) -> List[ErrorHandlingPattern]:
        """Audit logger usage patterns."""
        patterns = []
        standard_imports = ['logging_monitoring', 'get_logger']
        has_standard_logger = False
        has_nonstandard_logger = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if 'logging' in alias.name and 'logging_monitoring' not in alias.name:
                        if alias.name == 'logging':
                            patterns.append(ErrorHandlingPattern(
                                file_path=str(file_path.relative_to(Path.cwd())),
                                line_number=node.lineno,
                                pattern_type='logger_import',
                                details=f"Direct 'logging' import found: {alias.name}",
                                is_standard=False,
                                recommendation="Use 'from codomyrmex.logging_monitoring.logger_config import get_logger'"
                            ))
                            has_nonstandard_logger = True
            elif isinstance(node, ast.ImportFrom):
                if node.module and 'logging_monitoring' in node.module:
                    if any('get_logger' in alias.name for alias in node.names):
                        has_standard_logger = True
                elif node.module == 'logging':
                    patterns.append(ErrorHandlingPattern(
                        file_path=str(file_path.relative_to(Path.cwd())),
                        line_number=node.lineno,
                        pattern_type='logger_import',
                        details=f"Direct 'logging' import found: from {node.module}",
                        is_standard=False,
                        recommendation="Use 'from codomyrmex.logging_monitoring.logger_config import get_logger'"
                    ))
                    has_nonstandard_logger = True

        # Check for logger = get_logger(__name__) pattern
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'logger':
                        if isinstance(node.value, ast.Call):
                            if isinstance(node.value.func, ast.Name) and node.value.func.id == 'get_logger':
                                has_standard_logger = True
                                patterns.append(ErrorHandlingPattern(
                                    file_path=str(file_path.relative_to(Path.cwd())),
                                    line_number=node.lineno,
                                    pattern_type='logger_usage',
                                    details="Standard logger pattern: logger = get_logger(__name__)",
                                    is_standard=True,
                                    recommendation=""
                                ))

        return patterns


    def audit_exception_handling(tree: ast.AST, file_path: Path) -> List[ErrorHandlingPattern]:
        """Audit exception handling patterns."""
        patterns = []

        for node in ast.walk(tree):
            # Check for bare except clauses
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    patterns.append(ErrorHandlingPattern(
                        file_path=str(file_path.relative_to(Path.cwd())),
                        line_number=node.lineno,
                        pattern_type='exception_catch',
                        details="Bare except clause found (catches all exceptions)",
                        is_standard=False,
                        recommendation="Use specific exception types instead of bare except"
                    ))
                elif isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                    patterns.append(ErrorHandlingPattern(
                        file_path=str(file_path.relative_to(Path.cwd())),
                        line_number=node.lineno,
                        pattern_type='exception_catch',
                        details="Generic 'Exception' catch - should be more specific",
                        is_standard=False,
                        recommendation="Catch specific exception types (e.g., ValueError, FileNotFoundError)"
                    ))

            # Check for raises
            elif isinstance(node, ast.Raise):
                if node.exc:
                    if isinstance(node.exc, ast.Call):
                        if isinstance(node.exc.func, ast.Name):
                            exc_name = node.exc.func.id
                            # Check if using CodomyrmexError hierarchy
                            if exc_name in ['ValueError', 'TypeError', 'KeyError'] and 'codomyrmex' in str(file_path):
                                patterns.append(ErrorHandlingPattern(
                                    file_path=str(file_path.relative_to(Path.cwd())),
                                    line_number=node.lineno,
                                    pattern_type='exception_raise',
                                    details=f"Using built-in exception: {exc_name}",
                                    is_standard=True,  # Built-ins are fine for basic cases
                                    recommendation="Consider using CodomyrmexError hierarchy for module-specific errors"
                                ))

        return patterns


    def audit_file(file_path: Path) -> List[ErrorHandlingPattern]:
        """Audit error handling patterns in a single file."""
        patterns = []

        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))

            patterns.extend(audit_logger_usage(tree, file_path))
            patterns.extend(audit_exception_handling(tree, file_path))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)

        return patterns


    def main():
        """Main function."""
        import os

        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        src_dir = project_root / 'src' / 'codomyrmex'
        output_dir = project_root / "@output"
        output_dir.mkdir(exist_ok=True)

        print("Auditing error handling patterns across codebase...")
        print("=" * 80)

        all_patterns = []
        python_files = find_python_files(src_dir)

        for py_file in python_files:
            patterns = audit_file(py_file)
            all_patterns.extend(patterns)

        print(f"\nAnalyzed {len(python_files)} Python files")
        print(f"Found {len(all_patterns)} error handling patterns")

        # Categorize
        by_type = {}
        non_standard = []

        for pattern in all_patterns:
            if pattern.pattern_type not in by_type:
                by_type[pattern.pattern_type] = []
            by_type[pattern.pattern_type].append(pattern)

            if not pattern.is_standard:
                non_standard.append(pattern)

        print("\nPattern Summary:")
        for pattern_type, patterns_list in by_type.items():
            standard_count = sum(1 for p in patterns_list if p.is_standard)
            non_standard_count = len(patterns_list) - standard_count
            print(f"  {pattern_type:20}: {len(patterns_list):4} total ({standard_count} standard, {non_standard_count} non-standard)")

        print(f"\nNon-standard patterns found: {len(non_standard)}")

        # Save report
        report = {
            'total_files_analyzed': len(python_files),
            'total_patterns': len(all_patterns),
            'non_standard_count': len(non_standard),
            'by_type': {k: [asdict(p) for p in v] for k, v in by_type.items()},
            'non_standard_patterns': [asdict(p) for p in non_standard]
        }

        json_path = output_dir / "error_handling_audit_report.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nReport saved to: {json_path}")

        # Print non-standard patterns
        if non_standard:
            print("\n" + "=" * 80)
            print("NON-STANDARD PATTERNS:")
            print("=" * 80)
            for pattern in non_standard[:20]:  # Show first 20
                print(f"\n{pattern.file_path}:{pattern.line_number}")
                print(f"  Type: {pattern.pattern_type}")
                print(f"  Issue: {pattern.details}")
                print(f"  Recommendation: {pattern.recommendation}")

        return 0


    if __name__ == '__main__':
        sys.exit(main())

