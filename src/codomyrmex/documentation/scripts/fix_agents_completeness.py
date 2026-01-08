from pathlib import Path
from typing import Dict, List, Set
import argparse
import json
import os
import re

from codomyrmex.logging_monitoring import get_logger




















#!/usr/bin/env python3
"""
AGENTS.md Completeness Fixer for Codomyrmex

Automatically fixes AGENTS.md files to include missing directory contents
based on validation report analysis.
"""


#!/usr/bin/env python3
"""


logger = get_logger(__name__)

def get_file_description(filename: str) -> str:
    """Get a description for a file based on its name and extension."""
    # Known files by exact name
    known_files = {
        'Makefile': 'Build automation file',
        'LICENSE': 'Project license file',
        'SECURITY.md': 'Security policy and vulnerability reporting',
        'pyproject.toml': 'Python project configuration',
        'package.json': 'Node.js package configuration',
        'setup.py': 'Python package setup script',
        'pytest.ini': 'Pytest configuration',
        'uv.lock': 'UV dependency lock file',
        'resources.json': 'Project resource definitions',
        'start_here.sh': 'Quick start script for new users',
        'coverage.json': 'Code coverage report data',
        'test.db': 'Test database file',
        'workflow.db': 'Workflow database file',
        'demo_plot.png': 'Generated demonstration plot',
    }

    if filename in known_files:
        return known_files[filename]

    # File extensions
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    extension_descriptions = {
        '.md': 'Documentation file',
        '.py': 'Python module',
        '.txt': 'Text file',
        '.json': 'Configuration file',
        '.toml': 'Configuration file',
        '.yaml': 'Configuration file',
        '.yml': 'Configuration file',
        '.sh': 'Shell script',
        '.bash': 'Shell script',
        '.js': 'JavaScript file',
        '.ts': 'TypeScript file',
        '.html': 'HTML file',
        '.css': 'CSS file',
        '.png': 'Image file',
        '.jpg': 'Image file',
        '.jpeg': 'Image file',
        '.svg': 'Vector image file',
        '.pdf': 'PDF document',
        '.db': 'Database file',
        '.sqlite': 'SQLite database file',
        '.lock': 'Lock file',
        '.ini': 'Configuration file',
        '.cfg': 'Configuration file',
        '.env': 'Environment configuration',
        '.gitignore': 'Git ignore patterns',
        '.dockerignore': 'Docker ignore patterns',
    }

    if ext in extension_descriptions:
        return extension_descriptions[ext]

    # Special patterns
    if filename.startswith('test_') or filename.endswith('_test.py'):
        return 'Test file'
    if filename.startswith('example') or filename.endswith('example.py'):
        return 'Example file'
    if 'config' in filename.lower():
        return 'Configuration file'
    if 'readme' in filename.lower():
        return 'Documentation file'

    # Default
    return 'Project file'


def load_validation_report(report_path: Path) -> Dict:
    """Load the validation report JSON."""
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_missing_items(validation: Dict) -> Set[str]:
    """Extract missing directory items from validation issues."""
    missing_items = set()

    for issue in validation.get('issues', []):
        if issue['issue_type'] == 'missing_directory_items':
            # Parse the description to extract item names
            desc = issue['description']
            if 'missing:' in desc:
                items_str = desc.split('missing:')[1].strip()
                # Split by comma and clean up
                items = [item.strip().strip('`') for item in items_str.split(',')]
                missing_items.update(items)

    return missing_items


def read_agents_file(agents_path: Path) -> str:
    """Read an AGENTS.md file."""
    if not agents_path.exists():
        return ""

    with open(agents_path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_active_components(content: str) -> List[str]:
    """Parse the Active Components section to extract current items."""
    lines = content.split('\n')
    active_components = []
    in_active_components = False

    for line in lines:
        line = line.strip()
        if line.startswith('## Active Components'):
            in_active_components = True
            continue
        elif line.startswith('##') and in_active_components:
            # We've reached the next section
            break

        if in_active_components and line.startswith('- '):
            # Extract the item name (remove markdown formatting)
            item = line[2:]  # Remove '- '
            # Remove bold formatting and links
            item = re.sub(r'\*\*([^*]+)\*\*', r'\1', item)
            item = re.sub(r'`([^`]+)`', r'\1', item)
            # Extract just the item name before any description
            if ' – ' in item:
                item = item.split(' – ')[0].strip()
            elif ' - ' in item:
                item = item.split(' - ')[0].strip()
            elif ':' in item:
                item = item.split(':')[0].strip()
            elif '–' in item:
                item = item.split('–')[0].strip()

            active_components.append(item.strip())

    return active_components


def update_active_components(content: str, missing_items: Set[str]) -> str:
    """Add missing items to the Active Components section."""
    if not missing_items:
        return content

    lines = content.split('\n')
    updated_lines = []
    in_active_components = False
    added_items = False

    for line in lines:
        updated_lines.append(line)

        if line.strip().startswith('## Active Components'):
            in_active_components = True
        elif line.strip().startswith('##') and in_active_components and not added_items:
            # We've reached the end of Active Components, add missing items before the next section
            for item in sorted(missing_items):
                # Add all missing items with appropriate descriptions
                if item.endswith('/'):
                    updated_lines.append(f"- `{item}` – Directory for {item.rstrip('/')} components.")
                else:
                    # Determine description based on file extension or known file names
                    description = get_file_description(item)
                    updated_lines.append(f"- `{item}` – {description}")
            added_items = True

    return '\n'.join(updated_lines)


def fix_agents_completeness(report_path: Path, repo_root: Path) -> int:
    """Fix AGENTS.md files to include missing directory contents."""
    report = load_validation_report(report_path)
    fixed_count = 0

    for validation in report.get('file_validations', []):
        if validation.get('is_valid', True):
            continue  # Skip already valid files

        missing_items = get_missing_items(validation)
        if not missing_items:
            continue

        agents_path = repo_root / validation['file_path']
        if not agents_path.exists():
            continue

        print(f"Fixing {validation['file_path']} - adding {len(missing_items)} missing items")

        # Read current content
        content = read_agents_file(agents_path)

        # Update the content
        updated_content = update_active_components(content, missing_items)

        # Write back
        with open(agents_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        fixed_count += 1

    return fixed_count


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Fix AGENTS.md completeness issues")
    parser.add_argument('--report', type=Path, default=Path('output/agents_structure_validation.json'),
                       help='Path to validation report JSON')
    parser.add_argument('--repo-root', type=Path, default=Path('.'),
                       help='Repository root directory')

    args = parser.parse_args()

    fixed_count = fix_agents_completeness(args.report, args.repo_root)
    print(f"Fixed {fixed_count} AGENTS.md files with missing directory items")


if __name__ == '__main__':
    main()
