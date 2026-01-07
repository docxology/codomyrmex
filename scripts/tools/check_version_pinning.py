#!/usr/bin/env python3
"""
Check and report version pinning status across all requirements.txt files.

This script identifies dependencies that are not pinned to exact versions
and reports them for review and pinning.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
import sys


def find_requirements_files(project_root: Path) -> List[Path]:
    """Find all requirements.txt files in the project."""
    requirements_files = []
    for root, dirs, files in os.walk(project_root):
        # Skip hidden directories and common ignore patterns
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', '.venv']]
        for file in files:
            if file == 'requirements.txt':
                requirements_files.append(Path(root) / file)
    return sorted(requirements_files)


def parse_requirement_line(line: str) -> Tuple[str, str, bool]:
    """
    Parse a requirements line and determine if it's pinned.

    Returns: (package_name, version_spec, is_pinned)
    """
    line = line.strip()

    # Skip comments and empty lines
    if not line or line.startswith('#'):
        return ('', '', True)

    # Remove inline comments
    if '#' in line:
        line = line.split('#')[0].strip()

    # Pattern: package==version (exact pin)
    exact_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)==([0-9.]+[a-zA-Z0-9_.-]*)$', line)
    if exact_match:
        return (exact_match.group(1), exact_match.group(2), True)

    # Pattern: package>=version (not pinned)
    ge_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*>=\s*([0-9.]+[a-zA-Z0-9_.-]*)$', line)
    if ge_match:
        return (ge_match.group(1), f">={ge_match.group(2)}", False)

    # Pattern: package~=version (compatible release, not pinned)
    compat_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*~=\s*([0-9.]+[a-zA-Z0-9_.-]*)$', line)
    if compat_match:
        return (compat_match.group(1), f"~={compat_match.group(2)}", False)

    # Pattern: package>version (not pinned)
    gt_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*>\s*([0-9.]+[a-zA-Z0-9_.-]*)$', line)
    if gt_match:
        return (gt_match.group(1), f">{gt_match.group(2)}", False)

    # Pattern: package (no version, not pinned)
    no_version_match = re.match(r'^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*$', line)
    if no_version_match:
        return (no_version_match.group(1), 'no version', False)

    # Other patterns (URLs, git, etc.) - consider as pinned if they have a specific ref
    if '@' in line or 'git+' in line or 'http' in line:
        return (line, 'external', True)  # External dependencies are considered pinned if they have refs

    return (line, 'unknown', False)


def check_file(file_path: Path) -> Dict[str, List[Tuple[int, str, str]]]:
    """
    Check a requirements file for unpinned dependencies.

    Returns: Dictionary with 'unpinned' and 'pinned' lists of (line_num, package, version_spec)
    """
    result = {'unpinned': [], 'pinned': []}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                package, version_spec, is_pinned = parse_requirement_line(line)
                if package:  # Skip empty/comment lines
                    entry = (line_num, package, version_spec)
                    if is_pinned:
                        result['pinned'].append(entry)
                    else:
                        result['unpinned'].append(entry)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)

    return result


def main():
    """Main function to check version pinning."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    print(f"Checking version pinning in requirements files")
    print("=" * 80)

    requirements_files = find_requirements_files(project_root)

    if not requirements_files:
        print("No requirements.txt files found.")
        return 0

    total_unpinned = 0
    total_pinned = 0
    files_with_issues = []

    for req_file in requirements_files:
        rel_path = req_file.relative_to(project_root)
        result = check_file(req_file)

        unpinned_count = len(result['unpinned'])
        pinned_count = len(result['pinned'])

        total_unpinned += unpinned_count
        total_pinned += pinned_count

        if unpinned_count > 0:
            files_with_issues.append((rel_path, result))
            print(f"\n❌ {rel_path}: {unpinned_count} unpinned, {pinned_count} pinned")
            for line_num, package, version_spec in result['unpinned']:
                print(f"   Line {line_num}: {package} {version_spec}")
        else:
            print(f"✅ {rel_path}: All {pinned_count} dependencies pinned")

    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Total files checked: {len(requirements_files)}")
    print(f"  Files with unpinned dependencies: {len(files_with_issues)}")
    print(f"  Total pinned dependencies: {total_pinned}")
    print(f"  Total unpinned dependencies: {total_unpinned}")

    if files_with_issues:
        print(f"\n⚠️  Action Required: Pin {total_unpinned} dependencies to exact versions (==)")
        return 1
    else:
        print("\n✅ All dependencies are pinned to exact versions!")
        return 0


if __name__ == '__main__':
    sys.exit(main())

