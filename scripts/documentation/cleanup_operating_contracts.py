#!/usr/bin/env python3
"""
Clean up AGENTS.md files by removing incorrectly added items from Operating Contracts sections.
"""

import re
from pathlib import Path


def cleanup_operating_contracts(agents_path: Path) -> bool:
    """Remove incorrectly added directory items from Operating Contracts section."""
    if not agents_path.exists():
        return False

    content = agents_path.read_text(encoding='utf-8')
    original_content = content

    # Find the Operating Contracts section
    contracts_match = re.search(
        r'## Operating Contracts\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL | re.MULTILINE
    )

    if not contracts_match:
        return False

    contracts_content = contracts_match.group(1)

    # Remove lines that look like directory/file listings that were incorrectly added
    lines = contracts_content.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        # Skip lines that look like file/directory listings
        if (line.startswith('- `') and ('Directory for' in line or
                                      'Documentation file' in line or
                                      'Python module' in line or
                                      'Text file' in line or
                                      'Configuration file' in line or
                                      'Project file' in line)):
            continue
        cleaned_lines.append(line)

    # Reconstruct the contracts section
    new_contracts_content = '\n'.join(cleaned_lines)

    # Replace in the full content
    new_content = content.replace(contracts_match.group(1), new_contracts_content)

    if new_content != original_content:
        agents_path.write_text(new_content, encoding='utf-8')
        return True

    return False


def main():
    """Main entry point."""
    repo_root = Path('.')
    agents_files = list(repo_root.glob('**/AGENTS.md'))

    cleaned_count = 0
    for agents_file in agents_files:
        if cleanup_operating_contracts(agents_file):
            print(f"Cleaned {agents_file}")
            cleaned_count += 1

    print(f"Cleaned {cleaned_count} AGENTS.md files")


if __name__ == '__main__':
    main()
