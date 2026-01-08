from pathlib import Path
from typing import Dict, List
import argparse
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""
"""Main entry point and utility functions

This module provides fix_navigation_links functionality including:
- 6 functions: main, __init__, get_repo_structure...
- 1 classes: NavigationLinkFixer

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
Fix navigation links in AGENTS.md files that point to non-existent files.
"""



class NavigationLinkFixer:
    """Fix navigation links in AGENTS.md files."""

    def __init__(self, repo_root: Path):
    """Brief description of __init__.

Args:
    self : Description of self
    repo_root : Description of repo_root

    Returns: Description of return value
"""
        self.repo_root = repo_root
        self.fixed_count = 0

    def get_repo_structure(self) -> Dict[str, List[str]]:
        """Get the repository structure for validation."""
        structure = {}
        for path in self.repo_root.rglob('*'):
            if path.is_file() and path.name not in ['AGENTS.md']:
                rel_path = str(path.relative_to(self.repo_root))
                dir_path = str(path.parent.relative_to(self.repo_root)) if path.parent != self.repo_root else '.'
                if dir_path not in structure:
                    structure[dir_path] = []
                structure[dir_path].append(rel_path)
        return structure

    def validate_navigation_link(self, link_target: str, agents_file: Path) -> bool:
        """Check if a navigation link target exists."""
        try:
            # Convert relative link to absolute path
            if link_target.startswith('../'):
                # Calculate absolute path from agents file location
                current_dir = agents_file.parent
                target_path = current_dir / link_target
                target_path = target_path.resolve()
                return target_path.exists() and target_path.is_file()
            elif link_target.startswith('./') or not link_target.startswith('/'):
                # Relative to current directory
                current_dir = agents_file.parent
                target_path = current_dir / link_target
                target_path = target_path.resolve()
                return target_path.exists() and target_path.is_file()
            else:
                # Absolute path
                return False
        except:
            return False

    def fix_navigation_links(self, agents_file: Path, dry_run: bool = True) -> bool:
        """Fix navigation links in a single AGENTS.md file."""
        content = agents_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Find Navigation Links section
        nav_start = -1
        for i, line in enumerate(lines):
            if line.strip() == '## Navigation Links':
                nav_start = i
                break

        if nav_start == -1:
            return True  # No navigation section

        # Find end of navigation section
        nav_end = len(lines)
        for i in range(nav_start + 1, len(lines)):
            if lines[i].startswith('## ') or lines[i].startswith('---'):
                nav_end = i
                break

        # Extract navigation section
        nav_section = lines[nav_start:nav_end]

        # Find invalid links
        invalid_links = []
        for i, line in enumerate(nav_section):
            # Look for markdown links [text](target)
            link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
            if link_match:
                link_text = link_match.group(1)
                link_target = link_match.group(2)

                if not self.validate_navigation_link(link_target, agents_file):
                    invalid_links.append((i, line, link_target))

        if not invalid_links:
            return True  # All links valid

        if dry_run:
            print(f"🔧 Would fix {agents_file.relative_to(self.repo_root)}: {len(invalid_links)} invalid navigation links")
            for _, line, target in invalid_links:
                print(f"   ❌ {target}")
            return False

        # Remove invalid navigation links
        lines_to_remove = set()
        for line_idx, _, _ in invalid_links:
            lines_to_remove.add(nav_start + line_idx)

        # Remove lines in reverse order to maintain indices
        for line_idx in sorted(lines_to_remove, reverse=True):
            if line_idx < len(lines):
                lines.pop(line_idx)

        # Write back
        agents_file.write_text('\n'.join(lines), encoding='utf-8')

        print(f"✅ Fixed {agents_file.relative_to(self.repo_root)}: Removed {len(invalid_links)} invalid navigation links")
        self.fixed_count += 1
        return True

    def fix_all_navigation_links(self, dry_run: bool = True) -> Dict:
        """Fix navigation links in all AGENTS.md files."""
        agents_files = list(self.repo_root.rglob("AGENTS.md"))

        results = {
            'total': len(agents_files),
            'fixed': 0,
            'already_good': 0
        }

        for agents_file in agents_files:
            try:
                fixed = self.fix_navigation_links(agents_file, dry_run=dry_run)
                if fixed:
                    results['already_good'] += 1
                elif not dry_run:
                    results['fixed'] += 1
            except Exception as e:
                print(f"❌ Error fixing navigation in {agents_file}: {e}")

        return results


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description='Fix navigation links in AGENTS.md files')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be fixed without making changes')
    parser.add_argument('--fix', action='store_true',
                       help='Actually fix the navigation links')

    args = parser.parse_args()

    if args.fix:
        args.dry_run = False

    fixer = NavigationLinkFixer(args.repo_root)

    print("🔗 AGENTS.md Navigation Link Fixer")
    print("=" * 50)

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("Use --fix to apply fixes")
    else:
        print("APPLYING FIXES - Invalid navigation links will be removed")

    print()

    results = fixer.fix_all_navigation_links(dry_run=args.dry_run)

    print()
    print("📊 Results:")
    print(f"Total AGENTS.md files: {results['total']}")
    print(f"Already good: {results['already_good']}")
    if not args.dry_run:
        print(f"Fixed: {results['fixed']}")

    if args.dry_run and results['total'] > results['already_good']:
        print()
        print("Files needing fixes:")
        # Re-run to show which files need fixing
        fixer.fix_all_navigation_links(dry_run=True)


if __name__ == '__main__':
    main()

