#!/usr/bin/env python3
"""
Script to help pin dependency versions in requirements.txt files.

This script checks currently installed versions and suggests exact pins.
Note: This should be run in a clean environment with all dependencies installed.
"""

import subprocess
import sys
from pathlib import Path
import re


def get_installed_version(package_name: str) -> str:
    """Get the currently installed version of a package."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package_name],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return None


def pin_requirements_file(file_path: Path, dry_run: bool = True) -> int:
    """Pin versions in a requirements.txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return 0

    updated_count = 0
    new_lines = []

    for line in lines:
        original_line = line
        line = line.rstrip()

        # Skip comments and empty lines
        if not line or line.startswith('#'):
            new_lines.append(original_line)
            continue

        # Remove inline comments
        inline_comment = ''
        if '#' in line:
            parts = line.split('#', 1)
            line = parts[0].strip()
            inline_comment = ' #' + parts[1]

        # Check for >= or ~= patterns
        ge_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*>=\s*([0-9.]+[a-zA-Z0-9_.-]*)$', line)
        compat_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*~=\s*([0-9.]+[a-zA-Z0-9_.-]*)$', line)
        no_version_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*$', line)

        package_name = None
        if ge_match:
            package_name = ge_match.group(1)
        elif compat_match:
            package_name = compat_match.group(1)
        elif no_version_match:
            package_name = no_version_match.group(1)

        if package_name:
            installed_version = get_installed_version(package_name)
            if installed_version:
                new_line = f"{package_name}=={installed_version}{inline_comment}\n"
                if new_line.strip() != original_line.strip():
                    updated_count += 1
                    if not dry_run:
                        print(f"  Pinning {package_name}: {installed_version}")
                new_lines.append(new_line)
            else:
                # Keep original if version can't be determined
                new_lines.append(original_line)
        else:
            new_lines.append(original_line)

    if not dry_run and updated_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return updated_count


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Pin dependency versions in requirements.txt files')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be changed without modifying files (default)')
    parser.add_argument('--apply', action='store_true',
                       help='Actually apply the changes to files')
    parser.add_argument('files', nargs='*', help='Specific requirements.txt files to process (default: all)')

    args = parser.parse_args()

    if args.apply:
        dry_run = False
        print("⚠️  WARNING: This will modify requirements.txt files!")
        response = input("Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return 1
    else:
        dry_run = True
        print("🔍 DRY RUN MODE - No files will be modified")
        print("Use --apply to actually update files\n")

    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    if args.files:
        requirements_files = [Path(f) for f in args.files]
    else:
        requirements_files = list(project_root.rglob('requirements.txt'))
        # Filter out common ignore patterns
        requirements_files = [
            f for f in requirements_files
            if '.venv' not in str(f) and 'venv' not in str(f) and '__pycache__' not in str(f)
        ]

    total_updated = 0
    for req_file in sorted(requirements_files):
        rel_path = req_file.relative_to(project_root)
        print(f"\n📄 {rel_path}")
        updated = pin_requirements_file(req_file, dry_run=dry_run)
        total_updated += updated
        if updated > 0:
            print(f"  Would update {updated} dependencies" if dry_run else f"  Updated {updated} dependencies")
        else:
            print("  No changes needed")

    print(f"\n{'Would update' if dry_run else 'Updated'} {total_updated} dependencies across {len(requirements_files)} files")
    if dry_run:
        print("\nTo apply these changes, run with --apply flag")

    return 0


if __name__ == '__main__':
    sys.exit(main())

