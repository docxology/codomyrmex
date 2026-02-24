import argparse
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

"""
Batch fix AGENTS.md files throughout the repository.

This script identifies and fixes common issues with AGENTS.md files:
- Missing README.md in Active Components
- Missing actual files/directories from Active Components
- Ensures proper section structure
"""




logger = get_logger(__name__)

class AgentsFileFixer:
    """Fix AGENTS.md files throughout the repository."""

    def __init__(self, repo_root: Path):
        """Execute   Init   operations natively."""
        self.repo_root = repo_root
        self.fixed_count = 0
        self.error_count = 0

    def find_agents_files(self) -> list[Path]:
        """Find all AGENTS.md files in the repository."""
        return list(self.repo_root.rglob("AGENTS.md"))

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
                    continue  # Don't include AGENTS.md itself to avoid circular references
                if item.is_file() or item.is_dir():
                    items.add(item.name)
        except PermissionError:
            pass

        return items

    def parse_agents_file(self, agents_file: Path) -> dict:
        """Parse an AGENTS.md file and extract its sections."""
        if not agents_file.exists():
            return {}

        content = agents_file.read_text(encoding='utf-8')
        sections = {}

        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def extract_active_components(self, active_components_text: str) -> set[str]:
        """Extract listed items from Active Components section."""
        items = set()

        for line in active_components_text.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                # Extract item name from markdown links or plain text
                item = line[2:].strip()
                if item.startswith('`') and '`' in item:
                    item = item.split('`')[1]
                elif '[' in item and '](' in item:
                    # Extract from markdown link
                    link_start = item.find('](')
                    if link_start > 0:
                        item = item[:link_start].strip('[')
                elif ': ' in item:
                    item = item.split(': ')[0].strip()

                # Clean up the item name
                item = item.strip('`').strip('*').strip()
                if item and not item.startswith(('**', '##', '###')):
                    items.add(item)

        return items

    def fix_agents_file(self, agents_file: Path, dry_run: bool = True) -> bool:
        """Fix a single AGENTS.md file."""
        directory = agents_file.parent
        sections = self.parse_agents_file(agents_file)

        if 'Active Components' not in sections:
            print(f"❌ {agents_file.relative_to(self.repo_root)}: Missing Active Components section")
            return False

        # Get actual files in directory
        actual_items = self.get_actual_files(directory)

        # Extract currently documented items
        documented_items = self.extract_active_components(sections['Active Components'])

        # Find missing items
        missing_items = actual_items - documented_items

        if not missing_items:
            return True  # Already complete

        if dry_run:
            print(f"🔧 Would fix {agents_file.relative_to(self.repo_root)}: Add {len(missing_items)} missing items")
            for item in sorted(missing_items):
                print(f"   + {item}")
            return False

        # Fix the file by adding missing items
        try:
            content = agents_file.read_text(encoding='utf-8')

            # Find Active Components section and add missing items
            lines = content.split('\n')
            active_components_start = -1

            for i, line in enumerate(lines):
                if line.strip() == '## Active Components':
                    active_components_start = i
                    break

            if active_components_start == -1:
                print(f"❌ Could not find Active Components section in {agents_file}")
                return False

            # Find where to insert missing items (before next ## section)
            insert_pos = active_components_start + 1
            for i in range(active_components_start + 1, len(lines)):
                if lines[i].startswith('## '):
                    insert_pos = i
                    break

            # Add missing items as a new subsection
            if missing_items:
                missing_lines = ['### Additional Files']
                for item in sorted(missing_items):
                    missing_lines.append(f'- `{item}` – {item.replace(".", " ").replace("_", " ").title()}')

                # Insert the missing items
                lines[insert_pos:insert_pos] = [''] + missing_lines + ['']

                # Write back the fixed content
                agents_file.write_text('\n'.join(lines), encoding='utf-8')

                print(f"✅ Fixed {agents_file.relative_to(self.repo_root)}: Added {len(missing_items)} items")
                self.fixed_count += 1
                return True

        except Exception as e:
            print(f"❌ Error fixing {agents_file}: {e}")
            self.error_count += 1
            return False

    def fix_all_agents_files(self, dry_run: bool = True) -> dict:
        """Fix all AGENTS.md files in the repository."""
        agents_files = self.find_agents_files()
        print(f"Found {len(agents_files)} AGENTS.md files")

        results = {
            'total': len(agents_files),
            'fixed': 0,
            'already_good': 0,
            'errors': 0,
            'details': []
        }

        for agents_file in agents_files:
            try:
                fixed = self.fix_agents_file(agents_file, dry_run=dry_run)
                if fixed:
                    results['already_good'] += 1
                elif not dry_run:
                    results['fixed'] += 1
                results['details'].append({
                    'file': str(agents_file.relative_to(self.repo_root)),
                    'status': 'fixed' if fixed and not dry_run else 'needs_fix' if not fixed else 'good'
                })
            except Exception as e:
                print(f"❌ Error processing {agents_file}: {e}")
                results['errors'] += 1
                results['details'].append({
                    'file': str(agents_file.relative_to(self.repo_root)),
                    'status': 'error',
                    'error': str(e)
                })

        return results


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description='Fix AGENTS.md files throughout repository')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be fixed without making changes')
    parser.add_argument('--fix', action='store_true',
                       help='Actually apply fixes')

    args = parser.parse_args()

    if args.fix:
        args.dry_run = False

    fixer = AgentsFileFixer(args.repo_root)

    print("🔧 AGENTS.md File Fixer")
    print("=" * 50)

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("Use --fix to apply changes")
    else:
        print("APPLYING FIXES - Files will be modified")

    print()

    results = fixer.fix_all_agents_files(dry_run=args.dry_run)

    print()
    print("📊 Results:")
    print(f"Total AGENTS.md files: {results['total']}")
    print(f"Already complete: {results['already_good']}")
    if not args.dry_run:
        print(f"Fixed: {results['fixed']}")
    print(f"Errors: {results['errors']}")

    if args.dry_run and results['details']:
        print()
        print("Files needing fixes:")
        for detail in results['details']:
            if detail['status'] == 'needs_fix':
                print(f"  • {detail['file']}")


if __name__ == '__main__':
    main()
