from pathlib import Path
from typing import List, Set
import argparse
import re
import subprocess




#!/usr/bin/env python3
"""
Add orchestrator commands to AGENTS.md Active Components sections.

This script detects CLI commands from orchestrator scripts and adds them
to the corresponding AGENTS.md files.
"""



class OrchestratorCommandFixer:
    """Fix orchestrator commands in AGENTS.md files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.fixed_count = 0

    def extract_commands_from_orchestrator(self, script_path: Path) -> List[str]:
        """Extract CLI commands from an orchestrator script."""
        if not script_path.exists():
            return []

        try:
            content = script_path.read_text(encoding='utf-8')

            # Look for subparsers.add_parser calls
            commands = []
            for line in content.split('\n'):
                # Match: subparsers.add_parser("command_name"
                match = re.search(r'subparsers\.add_parser\(\s*["\']([^"\']+)["\']', line)
                if match:
                    command = match.group(1)
                    commands.append(command)

            # Also check for simple add_parser calls
            for line in content.split('\n'):
                match = re.search(r'add_parser\(\s*["\']([^"\']+)["\']', line)
                if match:
                    command = match.group(1)
                    if command not in commands:
                        commands.append(command)

            return sorted(commands)

        except Exception as e:
            print(f"Error reading {script_path}: {e}")
            return []

    def fix_orchestrator_commands(self, agents_file: Path, dry_run: bool = True) -> bool:
        """Fix orchestrator commands in a single AGENTS.md file."""
        directory = agents_file.parent

        # Look for orchestrate.py or similar orchestrator scripts
        orchestrator_files = []
        for script_file in directory.glob("*.py"):
            if "orchestrate" in script_file.name.lower() or script_file.name in ["cli.py", "__main__.py"]:
                orchestrator_files.append(script_file)

        if not orchestrator_files:
            return True  # No orchestrator files found

        # Extract commands from all orchestrator files
        all_commands = set()
        for orchestrator_file in orchestrator_files:
            commands = self.extract_commands_from_orchestrator(orchestrator_file)
            all_commands.update(commands)

        if not all_commands:
            return True  # No commands found

        # Check if commands are already documented
        content = agents_file.read_text(encoding='utf-8')

        # Look for commands in Active Components
        documented_commands = set()
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- `') and '`' in line:
                item = line.split('`')[1]
                documented_commands.add(item)

        missing_commands = all_commands - documented_commands

        if not missing_commands:
            return True  # All commands already documented

        if dry_run:
            print(f"🔧 Would fix {agents_file.relative_to(self.repo_root)}: Add {len(missing_commands)} orchestrator commands")
            for cmd in sorted(missing_commands):
                print(f"   + {cmd}")
            return False

        # Add missing commands to Active Components
        lines = content.split('\n')

        # Find Active Components section
        active_start = -1
        for i, line in enumerate(lines):
            if line.strip() == '## Active Components':
                active_start = i
                break

        if active_start == -1:
            print(f"❌ No Active Components section in {agents_file}")
            return False

        # Find end of Active Components section
        active_end = len(lines)
        for i in range(active_start + 1, len(lines)):
            if lines[i].startswith('## '):
                active_end = i
                break

        # Add orchestrator commands section
        command_lines = ['### CLI Commands']
        for cmd in sorted(missing_commands):
            command_lines.append(f'- `{cmd}` – Command-line interface for {cmd.replace("-", " ")}')

        # Insert before the end of Active Components
        insert_pos = active_end
        lines[insert_pos:insert_pos] = [''] + command_lines + ['']

        # Write back
        agents_file.write_text('\n'.join(lines), encoding='utf-8')

        print(f"✅ Fixed {agents_file.relative_to(self.repo_root)}: Added {len(missing_commands)} CLI commands")
        self.fixed_count += 1
        return True

    def fix_all_orchestrator_commands(self, dry_run: bool = True) -> dict:
        """Fix orchestrator commands in all AGENTS.md files."""
        agents_files = list(self.repo_root.rglob("AGENTS.md"))

        results = {
            'total': len(agents_files),
            'fixed': 0,
            'already_good': 0
        }

        for agents_file in agents_files:
            try:
                fixed = self.fix_orchestrator_commands(agents_file, dry_run=dry_run)
                if fixed:
                    results['already_good'] += 1
                elif not dry_run:
                    results['fixed'] += 1
            except Exception as e:
                print(f"❌ Error fixing orchestrator commands in {agents_file}: {e}")

        return results


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description='Fix orchestrator commands in AGENTS.md files')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Show what would be fixed without making changes')
    parser.add_argument('--fix', action='store_true',
                       help='Actually fix the orchestrator commands')

    args = parser.parse_args()

    if args.fix:
        args.dry_run = False

    fixer = OrchestratorCommandFixer(args.repo_root)

    print("🖥️  AGENTS.md Orchestrator Command Fixer")
    print("=" * 50)

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("Use --fix to apply fixes")
    else:
        print("APPLYING FIXES - CLI commands will be added to Active Components")

    print()

    results = fixer.fix_all_orchestrator_commands(dry_run=args.dry_run)

    print()
    print("📊 Results:")
    print(f"Total AGENTS.md files: {results['total']}")
    print(f"Already good: {results['already_good']}")
    if not args.dry_run:
        print(f"Fixed: {results['fixed']}")

    if args.dry_run and results['total'] > results['already_good']:
        print()
        print("Files needing fixes:")
        fixer.fix_all_orchestrator_commands(dry_run=True)


if __name__ == '__main__':
    main()

