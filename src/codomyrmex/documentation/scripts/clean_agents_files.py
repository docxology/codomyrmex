from pathlib import Path
import argparse
import re

from codomyrmex.logging_monitoring import get_logger




















#!/usr/bin/env python3
"""
Clean AGENTS.md files by removing conceptual items from Active Components.

This script identifies and removes items that are not actual files/directories
"""


# Script removes conceptual items from Active Components sections, while preserving the actual file listings.

#!/usr/bin/env python3
"""


logger = get_logger(__name__)

class AgentsCleaner:
    """Clean AGENTS.md files by removing conceptual items."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.fixed_count = 0

    def get_actual_files(self, directory: Path) -> set[str]:
        """Get all actual files and directories in a given directory."""
        if not directory.exists():
            return set()

        items = set()
        try:
            for item in directory.iterdir():
                if item.name.startswith('.'):
                    continue  # Skip hidden files
                if item.name == 'AGENTS.md':
                    continue  # Don't include AGENTS.md itself
                if item.is_file() or item.is_dir():
                    items.add(item.name)
        except PermissionError:
            pass

        return items

    def clean_agents_file(self, agents_file: Path, dry_run: bool = True) -> bool:
        """Clean a single AGENTS.md file."""
        directory = agents_file.parent
        actual_items = self.get_actual_files(directory)

        content = agents_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Find Active Components section
        active_start = -1
        for i, line in enumerate(lines):
            if line.strip() == '## Active Components':
                active_start = i
                break

        if active_start == -1:
            return True  # No Active Components section to clean

        # Find the end of Active Components section (next ## section)
        active_end = len(lines)
        for i in range(active_start + 1, len(lines)):
            if lines[i].startswith('## '):
                active_end = i
                break

        # Extract Active Components section
        active_section = lines[active_start:active_end]

        # Identify conceptual items (not actual files)
        conceptual_items = []
        for line in active_section:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                # Extract item name
                item_text = line[2:].strip()
                if '**' in item_text:
                    # Bold items are likely conceptual
                    conceptual_items.append(line)
                elif ':' in item_text and not item_text.startswith('`'):
                    # Items with descriptions but no backticks are likely conceptual
                    conceptual_items.append(line)
                elif item_text.startswith('**') and item_text.endswith('**'):
                    # Double-starred items are conceptual
                    conceptual_items.append(line)
                elif any(phrase in item_text.lower() for phrase in [
                    'basic workflows', 'custom templates', 'dependency workflows',
                    'migration status', 'output directory', 'data schemas',
                    'input datasets', 'intermediate results', 'reference data',
                    'development', 'production', 'workflow configurations',
                    'docker configuration', 'validation reports', 'quality analysis',
                    'dashboards', 'test validation results', 'baseline audit'
                ]):
                    conceptual_items.append(line)

        if not conceptual_items:
            return True  # No conceptual items to remove

        if dry_run:
            print(f"🔧 Would clean {agents_file.relative_to(self.repo_root)}: Remove {len(conceptual_items)} conceptual items")
            return False

        # Remove conceptual items
        cleaned_section = []
        for line in active_section:
            if line not in conceptual_items:
                cleaned_section.append(line)

        # Replace the section
        lines[active_start:active_end] = cleaned_section

        # Write back
        agents_file.write_text('\n'.join(lines), encoding='utf-8')

        print(f"✅ Cleaned {agents_file.relative_to(self.repo_root)}: Removed {len(conceptual_items)} conceptual items")
        self.fixed_count += 1
        return True

    def clean_all_agents_files(self, dry_run: bool = True) -> dict:
        """Clean all AGENTS.md files in the repository."""
        agents_files = list(self.repo_root.rglob("AGENTS.md"))

        results = {
            'total': len(agents_files),
            'cleaned': 0,
            'already_clean': 0
        }

        for agents_file in agents_files:
            try:
                cleaned = self.clean_agents_file(agents_file, dry_run=dry_run)
                if cleaned:
                    results['already_clean'] += 1
                elif not dry_run:
                    results['cleaned'] += 1
            except Exception as e:
                print(f"❌ Error cleaning {agents_file}: {e}")

        return results


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description='Clean AGENTS.md files by removing conceptual items')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be cleaned without making changes')
    parser.add_argument('--clean', action='store_true',
                       help='Actually clean the files')

    args = parser.parse_args()

    if args.clean:
        args.dry_run = False

    cleaner = AgentsCleaner(args.repo_root)

    print("🧹 AGENTS.md Cleaner")
    print("=" * 50)

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("Use --clean to apply cleaning")
    else:
        print("CLEANING MODE - Files will be modified")

    print()

    results = cleaner.clean_all_agents_files(dry_run=args.dry_run)

    print()
    print("📊 Results:")
    print(f"Total AGENTS.md files: {results['total']}")
    print(f"Already clean: {results['already_clean']}")
    if not args.dry_run:
        print(f"Cleaned: {results['cleaned']}")

    if args.dry_run and results['total'] > results['already_clean']:
        print()
        print("Files needing cleaning:")
        # Re-run to show which files need cleaning
        cleaner.clean_all_agents_files(dry_run=True)


if __name__ == '__main__':
    main()
