#!/usr/bin/env python3
"""
Syntax error detection and automated repair.

This script analyzes Python files for syntax errors and attempts to fix common issues.
"""

import argparse
import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class SyntaxFixer:
    """Automated syntax error detection and repair."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "files_checked": 0,
            "syntax_errors_found": 0,
            "syntax_errors_fixed": 0,
            "files_modified": 0
        }

        # Common syntax fixes
        self.fix_patterns = [
            # Missing colons
            (r'^\s*(def|class|if|elif|else|for|while|with|try|except|finally)\s+[^(]*\s*$',
             r'\1:'),

            # Missing parentheses in function calls
            (r'(\w+)\s*\n\s*([^=\s]+)\s*$',
             self._fix_function_call),

            # Missing quotes in strings
            (r'(\w+)\s*=\s*([^"\'][\w\s]*[^"\'])\s*$',
             self._fix_string_quotes),

            # Indentation issues
            (r'^(\s+)(\w+)(\s*)$',
             self._fix_indentation),
        ]

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed."""
        return (file_path.suffix == ".py" and
                not file_path.name.startswith("test_") and
                "__pycache__" not in str(file_path))

    def check_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check if a file has valid Python syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            ast.parse(content, filename=str(file_path))
            return True, None

        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def _fix_function_call(self, match: re.Match) -> str:
        """Fix missing parentheses in function calls."""
        func_name = match.group(1)
        args = match.group(2).strip()

        # Check if this looks like a function call that needs parentheses
        if (args and not args.startswith(('=', ':', '#')) and
            not any(char in args for char in ['=', ':', 'if', 'else'])):
            return f"{func_name}({args})"
        return match.group(0)

    def _fix_string_quotes(self, match: re.Match) -> str:
        """Fix missing quotes in string assignments."""
        var_name = match.group(1)
        value = match.group(2).strip()

        # Only fix if it looks like a string value
        if (value and not value.startswith(('True', 'False', 'None', '[', '{', '(')) and
            not any(char.isdigit() for char in value.split()[-1])):
            return f'{var_name} = "{value}"'
        return match.group(0)

    def _fix_indentation(self, match: re.Match) -> str:
        """Fix inconsistent indentation."""
        indent = match.group(1)
        code = match.group(2)

        # Check if this line needs proper indentation
        expected_indent = len(indent)
        if expected_indent % 4 != 0:
            # Fix to 4-space indentation
            new_indent = " " * (expected_indent // 4 * 4 + 4)
            return f"{new_indent}{code}"
        return match.group(0)

    def attempt_fix(self, content: str, error_line: int) -> Tuple[str, bool]:
        """Attempt to fix syntax errors in content."""
        lines = content.split('\n')
        fixed = False

        # Try to fix the specific error line and surrounding context
        for i in range(max(0, error_line - 3), min(len(lines), error_line + 3)):
            original_line = lines[i]

            for pattern, fix_func in self.fix_patterns:
                if callable(fix_func):
                    # Custom fix function
                    new_line = fix_func(re.match(pattern, original_line))
                    if new_line and new_line != original_line:
                        lines[i] = new_line
                        fixed = True
                        break
                else:
                    # Simple pattern replacement
                    new_line = re.sub(pattern, fix_func, original_line)
                    if new_line != original_line:
                        lines[i] = new_line
                        fixed = True
                        break

        return '\n'.join(lines), fixed

    def fix_file(self, file_path: Path) -> bool:
        """Fix syntax errors in a file."""
        is_valid, error_msg = self.check_syntax(file_path)

        if is_valid:
            print(f"  ✅ {file_path.name} has valid syntax")
            return False

        print(f"  ❌ {file_path.name} has syntax errors: {error_msg}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract line number from error message
            error_line = 1
            if "Line" in error_msg:
                try:
                    error_line = int(error_msg.split("Line ")[1].split(":")[0])
                except:
                    pass

            # Attempt to fix
            fixed_content, was_fixed = self.attempt_fix(content, error_line)

            if was_fixed:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)

                # Verify the fix
                is_now_valid, _ = self.check_syntax(file_path)
                if is_now_valid:
                    print(f"  ✅ Fixed syntax errors in {file_path.name}")
                    self.stats["syntax_errors_fixed"] += 1
                    self.stats["files_modified"] += 1
                    return True
                else:
                    print(f"  ⚠️  Fix didn't resolve all errors in {file_path.name}")
            else:
                print(f"  ⚠️  Could not automatically fix {file_path.name}")

        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")

        self.stats["syntax_errors_found"] += 1
        return False

    def process_directory(self, directory: Path, recursive: bool = True):
        """Process all Python files in a directory."""
        pattern = "**/*.py" if recursive else "*.py"

        for file_path in directory.glob(pattern):
            if self.should_process_file(file_path):
                self.stats["files_checked"] += 1
                self.fix_file(file_path)

    def print_summary(self):
        """Print processing summary."""
        print("\n📊 Syntax Error Fix Summary:")
        print(f"  Files checked: {self.stats['files_checked']}")
        print(f"  Syntax errors found: {self.stats['syntax_errors_found']}")
        print(f"  Syntax errors fixed: {self.stats['syntax_errors_fixed']}")
        print(f"  Files modified: {self.stats['files_modified']}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Fix syntax errors in Python files")
    parser.add_argument("--path", default="src/codomyrmex", help="Path to process")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process subdirectories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--file", help="Process a single file")

    args = parser.parse_args()

    print("🔧 Codomyrmex Syntax Error Fixer")
    print("=" * 40)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    fixer = SyntaxFixer(dry_run=args.dry_run)
    target_path = Path(args.path)

    if args.file:
        file_path = Path(args.file)
        if fixer.should_process_file(file_path):
            fixer.fix_file(file_path)
    elif target_path.is_file():
        if fixer.should_process_file(target_path):
            fixer.fix_file(target_path)
    elif target_path.is_dir():
        fixer.process_directory(target_path, args.recursive)
    else:
        print(f"❌ Path not found: {args.path}")
        return 1

    fixer.print_summary()

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply fixes")
        return 0

    return 0


if __name__ == "__main__":
    exit(main())
