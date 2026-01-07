#!/usr/bin/env python3
"""
Script to generate README.md files for directories that have AGENTS.md but no README.md.
Uses AGENTS.md content as a template and enhances with technical details.
"""

import os
import re
from pathlib import Path
from datetime import datetime

def parse_agents_file(agents_path):
    """Parse AGENTS.md file to extract key information."""
    if not agents_path.exists():
        return None

    with open(agents_path, 'r') as f:
        content = f.read()

    # Extract basic information
    lines = content.split('\n')

    # Get module name from first line
    first_line = lines[0] if lines else ""
    module_match = re.search(r'—\s*(.+)$', first_line)
    module_name = module_match.group(1) if module_match else "Unknown Module"

    # Extract purpose
    purpose_match = re.search(r'## Purpose\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    purpose = purpose_match.group(1).strip() if purpose_match else "No purpose specified"

    # Extract active components
    components_match = re.search(r'## Active Components\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    components = components_match.group(1).strip() if components_match else "No components specified"

    # Extract operating contracts
    contracts_match = re.search(r'## Operating Contracts\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    contracts = contracts_match.group(1).strip() if contracts_match else "No contracts specified"

    # Extract related modules
    related_match = re.search(r'## Related Modules\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    related = related_match.group(1).strip() if related_match else "No related modules specified"

    return {
        'module_name': module_name,
        'purpose': purpose,
        'components': components,
        'contracts': contracts,
        'related': related
    }

def generate_readme_content(module_info, dir_path, repo_root):
    """Generate minimal README.md content based on AGENTS.md info."""

    module_name = module_info['module_name']
    purpose = module_info['purpose']

    # Get relative path
    rel_path = str(dir_path.relative_to(repo_root))

    # Get navigation links
    nav_links = generate_navigation_links(dir_path, repo_root)

    readme_content = f"""# {module_name}

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: {datetime.now().strftime('%B %Y')}

## Overview

{purpose}

## Directory Contents
"""

    # Add directory contents if available
    try:
        contents = []
        for item in sorted(dir_path.iterdir()):
            if item.name not in ['AGENTS.md', 'README.md', '.git', '__pycache__', '.pyc']:
                if item.is_dir():
                    contents.append(f"- `{item.name}/` – Subdirectory")
                else:
                    contents.append(f"- `{item.name}` – File")

        if contents:
            readme_content += "\n".join(contents) + "\n"
        else:
            readme_content += "No additional files.\n"
    except:
        readme_content += "Directory contents.\n"

    # Add navigation
    if nav_links:
        readme_content += "\n## Navigation\n"
        for link_type, link_path in nav_links.items():
            if link_type == 'parent':
                readme_content += f"- **Parent Directory**: [{dir_path.parent.name}](../README.md)\n"
            elif link_type == 'root':
                readme_content += f"- **Project Root**: [README](../../../README.md)\n"
            elif link_type == 'surface':
                surface_name = rel_path.split('/')[0]
                readme_content += f"- **{surface_name.title()} Hub**: [{surface_name}](../../../{surface_name}/README.md)\n"

    return readme_content


def generate_navigation_links(dir_path, repo_root):
    """Generate navigation links for a directory."""
    nav_links = {}

    # Root README (always exists)
    nav_links['root'] = '../../../README.md'

    # Parent directory link (if parent README exists)
    parent = dir_path.parent
    if parent != repo_root:
        parent_readme = parent / "README.md"
        if parent_readme.exists():
            nav_links['parent'] = '../README.md'

    # Surface hub (if surface README exists)
    rel_path = dir_path.relative_to(repo_root)
    if len(rel_path.parts) >= 1:
        surface_root = rel_path.parts[0]
        surface_readme = repo_root / surface_root / "README.md"
        if surface_readme.exists():
            # Calculate path to surface README
            surface_depth = len(rel_path.parts) - 1  # Go up to surface level
            surface_path = "../" * surface_depth + f"{surface_root}/README.md"
            nav_links['surface'] = surface_path

    return nav_links

def main():
    """Main function to generate README.md files for all eligible directories."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate README.md files for directories with AGENTS.md")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing README.md files')

    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    generated_count = 0

    # Find all directories with AGENTS.md
    for dir_path in repo_root.rglob("*"):
        if not dir_path.is_dir():
            continue

        # Skip common ignore patterns
        rel_path = str(dir_path.relative_to(repo_root))
        if any(pattern in rel_path for pattern in ['__pycache__', '.venv', '.git', 'node_modules']):
            continue

        agents_path = dir_path / "AGENTS.md"
        readme_path = dir_path / "README.md"

        # Check if we should generate README.md
        should_generate = agents_path.exists() and (not readme_path.exists() or args.force)

        if should_generate:
            print(f"Generating README.md for: {rel_path}")

            # Parse AGENTS.md content
            module_info = parse_agents_file(agents_path)

            if module_info:
                # Generate README.md content
                readme_content = generate_readme_content(module_info, dir_path, repo_root)

                # Write README.md file
                with open(readme_path, 'w') as f:
                    f.write(readme_content)

                generated_count += 1
                print(f"  ✅ Generated README.md for {rel_path}")
            else:
                print(f"  ⚠️  Could not parse AGENTS.md for {rel_path}")

    print(f"\n📊 Generated {generated_count} README.md files")

if __name__ == "__main__":
    main()

