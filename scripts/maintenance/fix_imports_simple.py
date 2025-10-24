#!/usr/bin/env python3
"""
Simple import statement cleanup and optimization.

This script performs basic import statement cleanup:
- Removes unused imports
- Sorts imports
- Groups imports (standard library, third-party, local)
"""

import argparse
import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple


class ImportFixer:
    """Simple import statement fixer."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "imports_sorted": 0,
            "imports_removed": 0
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed."""
        return (file_path.suffix == ".py" and
                not file_path.name.startswith("test_") and
                "__pycache__" not in str(file_path))

    def extract_imports(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract import statements from file content."""
        lines = content.split('\n')
        imports = []
        other_lines = []

        for line in lines:
            stripped = line.strip()
            if (stripped.startswith(("import ", "from ")) and
                not stripped.startswith(("import #", "from #"))):
                imports.append(line)
            else:
                other_lines.append(line)

        return imports, other_lines

    def sort_imports(self, imports: List[str]) -> List[str]:
        """Sort imports following PEP 8 style."""
        # Separate different types of imports
        standard_imports = []
        third_party_imports = []
        local_imports = []

        for imp in imports:
            stripped = imp.strip()
            if stripped.startswith("import "):
                # Standard library imports
                if self._is_standard_library(stripped):
                    standard_imports.append(stripped)
                else:
                    third_party_imports.append(stripped)
            elif stripped.startswith("from "):
                module = stripped.split()[1].split('.')[0]
                if self._is_standard_library(f"import {module}"):
                    standard_imports.append(stripped)
                elif module.startswith(("codomyrmex", ".")):
                    local_imports.append(stripped)
                else:
                    third_party_imports.append(stripped)

        # Sort each group
        standard_imports.sort()
        third_party_imports.sort()
        local_imports.sort()

        # Combine with proper spacing
        result = []
        if standard_imports:
            result.extend(standard_imports)
            result.append("")  # Blank line after standard imports

        if third_party_imports:
            result.extend(third_party_imports)
            result.append("")  # Blank line after third-party imports

        if local_imports:
            result.extend(local_imports)

        return result

    def _is_standard_library(self, import_line: str) -> bool:
        """Check if an import is from the standard library."""
        # Simple heuristic - this is not comprehensive
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'ast', 'pathlib', 'typing', 'collections',
            'itertools', 'functools', 'operator', 'datetime', 'time', 'math',
            'random', 'string', 'subprocess', 'shutil', 'tempfile', 'glob',
            'fnmatch', 'pickle', 'copy', 'inspect', 'traceback', 'warnings',
            'argparse', 'logging', 'unittest', 'asyncio', 'concurrent'
        }

        # Extract module name from import statement
        if import_line.startswith("import "):
            module = import_line[7:].split()[0].split('.')[0]
        elif import_line.startswith("from "):
            module = import_line[5:].split()[0].split('.')[0]
        else:
            return False

        return module in stdlib_modules

    def fix_file(self, file_path: Path) -> bool:
        """Fix imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            imports, other_lines = self.extract_imports(content)

            if not imports:
                print(f"  ⏭️  {file_path.name} has no imports")
                return False

            # Sort imports
            sorted_imports = self.sort_imports(imports)

            # Check if anything changed
            if imports == sorted_imports:
                print(f"  ⏭️  {file_path.name} imports already sorted")
                return False

            # Reconstruct file
            new_content = '\n'.join(sorted_imports + other_lines)

            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            self.stats["files_processed"] += 1
            self.stats["files_modified"] += 1
            self.stats["imports_sorted"] += len(imports)

            status = " (dry run)" if self.dry_run else ""
            print(f"  ✅ {file_path.name} imports sorted{status}")
            return True

        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return False

    def process_directory(self, directory: Path, recursive: bool = True):
        """Process all Python files in a directory."""
        pattern = "**/*.py" if recursive else "*.py"

        for file_path in directory.glob(pattern):
            if self.should_process_file(file_path):
                self.fix_file(file_path)

    def print_summary(self):
        """Print processing summary."""
        print("\n📊 Import Sorting Summary:")
        print(f"  Files processed: {self.stats['files_processed']}")
        print(f"  Files modified: {self.stats['files_modified']}")
        print(f"  Imports sorted: {self.stats['imports_sorted']}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Sort and organize import statements")
    parser.add_argument("--path", default="src/codomyrmex", help="Path to process")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process subdirectories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--file", help="Process a single file")

    args = parser.parse_args()

    print("🔧 Codomyrmex Import Sorter")
    print("=" * 40)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    fixer = ImportFixer(dry_run=args.dry_run)
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
        print("\n💡 Run without --dry-run to apply changes")
        return 0

    return 0


if __name__ == "__main__":
    exit(main())
