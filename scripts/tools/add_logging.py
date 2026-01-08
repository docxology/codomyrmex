#!/usr/bin/env python3
"""
Automated logging injection across Codomyrmex modules.

This script automatically adds logging statements to Python files that don't have them,
following the project's logging patterns.
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import argparse
import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Any


class LoggingInjector:
    """Inject logging statements into Python modules."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "loggers_added": 0,
            "imports_added": 0
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed."""
        # Skip test files, __init__.py, and files in certain directories
        if (file_path.name.startswith("test_") or
            file_path.name == "__init__.py" or
            "test" in str(file_path) or
            "__pycache__" in str(file_path)):
            return False

        return file_path.suffix == ".py"

    def has_logging_import(self, content: str) -> bool:
        """Check if file already imports logging."""
        return "import logging" in content or "from codomyrmex.logging_monitoring" in content

    def has_logger_usage(self, content: str) -> bool:
        """Check if file already uses logging."""
        patterns = [
            r"logger\s*=",
            r"get_logger",
            r"logging\.",
            r"logger\."
        ]
        return any(re.search(pattern, content) for pattern in patterns)

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for logging needs."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "needs_import": not self.has_logging_import(content),
                "needs_logger": not self.has_logger_usage(content),
                "has_functions": bool(re.search(r'def \w+', content)),
                "has_classes": bool(re.search(r'class \w+', content)),
                "line_count": len(content.split('\n'))
            }
        except Exception as e:
            return {"error": str(e)}

    def inject_logging(self, file_path: Path) -> bool:
        """Inject logging into a Python file."""
        analysis = self.analyze_file(file_path)

        if "error" in analysis:
            print(f"  ❌ Error analyzing {file_path}: {analysis['error']}")
            return False

        if not (analysis["needs_import"] or analysis["needs_logger"]):
            print(f"  ⏭️  {file_path.name} already has logging")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            modified = False
            new_lines = []

            # Add import if needed
            if analysis["needs_import"]:
                # Find a good place to insert import (after existing imports)
                import_section_end = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(("import ", "from ")):
                        import_section_end = i + 1
                    elif line.strip() and not line.strip().startswith(("import ", "from ", '"""', "'''", "#")):
                        break

                # Insert logging import
                import_line = "from codomyrmex.logging_monitoring import get_logger\n"
                new_lines = lines[:import_section_end]
                new_lines.append(import_line)
                new_lines.extend(lines[import_section_end:])
                modified = True
                self.stats["imports_added"] += 1

            # Add logger if needed
            if analysis["needs_logger"]:
                # Find a good place for logger (after imports, before first function/class)
                logger_line = "logger = get_logger(__name__)\n"

                # Look for the end of imports and beginning of code
                insert_pos = len(new_lines) if modified else len(lines)

                for i in range(len(new_lines) if modified else len(lines)):
                    line = new_lines[i] if modified else lines[i]
                    if (line.strip() and
                        not line.strip().startswith(("import ", "from ", '"""', "'''", "#", "logger"))):
                        insert_pos = i
                        break

                # Insert logger
                if modified:
                    new_lines.insert(insert_pos, logger_line)
                else:
                    lines.insert(insert_pos, logger_line)
                    new_lines = lines

                modified = True
                self.stats["loggers_added"] += 1

            # Write back if modified
            if modified and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)

            self.stats["files_processed"] += 1
            if modified:
                self.stats["files_modified"] += 1

            status = " (dry run)" if self.dry_run else ""
            print(f"  {'✅' if modified else '⏭️'} {file_path.name}{status}")
            return modified

        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return False

    def process_directory(self, directory: Path, recursive: bool = True):
        """Process all Python files in a directory."""
        pattern = "**/*.py" if recursive else "*.py"

        for file_path in directory.glob(pattern):
            if self.should_process_file(file_path):
                self.inject_logging(file_path)

    def print_summary(self):
        """Print processing summary."""
        print("📊 Logging Injection Summary:")
        print(f"  Files processed: {self.stats['files_processed']}")
        print(f"  Files modified: {self.stats['files_modified']}")
        print(f"  Imports added: {self.stats['imports_added']}")
        print(f"  Loggers added: {self.stats['loggers_added']}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Add logging to Codomyrmex modules")
    parser.add_argument("--path", default="src/codomyrmex", help="Path to process")
    parser.add_argument("--recursive", action="store_true", default=True, help="Process subdirectories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--pattern", default="**/*.py", help="File pattern to match")

    args = parser.parse_args()

    print("🔧 Codomyrmex Logging Injection Tool")
    print("=" * 50)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print()

    injector = LoggingInjector(dry_run=args.dry_run)
    target_path = Path(args.path)

    if target_path.is_file():
        if injector.should_process_file(target_path):
            injector.inject_logging(target_path)
    elif target_path.is_dir():
        injector.process_directory(target_path, args.recursive)
    else:
        print(f"❌ Path not found: {args.path}")
        return 1

    injector.print_summary()

    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")
    
    return 0


if __name__ == "__main__":
    exit(main())