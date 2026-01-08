from datetime import datetime
from pathlib import Path
from typing import Set, List
import argparse
import logging
import sys

from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging



#!/usr/bin/env python3
"""
Bootstrap script to create AGENTS.md and README.md files for every directory
under the allowed surfaces in the Codomyrmex repository.

This script ensures complete documentation coverage with explicit inventories
and proper navigation signposting.
"""


try:
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class DocumentationBootstrapper:
    """Handles bootstrapping of AGENTS.md and README.md files across the repository."""

    # Surface roots to cover
    SURFACE_ROOTS = {
        'src', 'scripts', 'docs', 'config', 'testing',
        'projects', 'cursorrules', 'examples'
    }

    # Directories to exclude from processing
    EXCLUDED_DIRS = {
        'output', '@output', '.git', 'node_modules', '__pycache__',
        '.venv', 'venv', 'dist', 'build', '.pytest_cache', '.mypy_cache'
    }

    # Files to exclude from inventories (but include README.md if it exists)
    EXCLUDED_FILES = {
        'AGENTS.md',  # Don't include ourselves, but do include README.md
        '.git', '.gitignore', '.gitattributes', '.pre-commit-config.yaml',
        '.editorconfig', '.encryption_key'
    }

    def __init__(self, repo_root: Path):
        """Initialize bootstrapper."""
        self.repo_root = repo_root.resolve()
        self.generated_count = 0
        self.updated_count = 0

    def should_process_directory(self, dir_path: Path) -> bool:
        """Check if a directory should be processed."""
        rel_path = dir_path.relative_to(self.repo_root)

        # Check if any part of the path is excluded
        for part in rel_path.parts:
            if part in self.EXCLUDED_DIRS:
                return False
            # Also exclude dot-directories (directories starting with .)
            if part.startswith('.'):
                return False

        # Check if this is under an allowed surface root
        if len(rel_path.parts) == 0:
            return False  # Skip repo root itself

        first_part = rel_path.parts[0]
        if first_part not in self.SURFACE_ROOTS:
            return False

        # Allow both surface root directories and their subdirectories
        return True

    def get_directory_inventory(self, dir_path: Path) -> List[str]:
        """Get inventory of immediate children for a directory."""
        inventory = []

        try:
            for item in sorted(dir_path.iterdir()):
                # Include README.md but exclude AGENTS.md and other excluded files
                if item.name == 'AGENTS.md':
                    continue
                if item.name in self.EXCLUDED_FILES:
                    continue
                if item.name in self.EXCLUDED_DIRS:
                    continue
                # Also exclude dot-directories
                if item.name.startswith('.'):
                    continue

                if item.is_file():
                    inventory.append(item.name)
                elif item.is_dir():
                    inventory.append(f"{item.name}/")

        except PermissionError:
            logger.warning(f"Cannot access directory: {dir_path}")
            return []

        return inventory

    def get_navigation_links(self, dir_path: Path) -> dict:
        """Generate navigation links for a directory."""
        rel_path = dir_path.relative_to(self.repo_root)
        nav_links = {}

        # Calculate path to root README
        depth = len(rel_path.parts)
        root_path = "../" * depth + "README.md"
        nav_links['root'] = root_path

        # Parent directory link (if parent README exists)
        parent = dir_path.parent
        if parent != self.repo_root:
            parent_readme = parent / "README.md"
            if parent_readme.exists():
                nav_links['parent'] = "../README.md"

        # Surface hub (if surface README exists)
        # Note: Surface READMEs may not exist for all surface roots,
        # so we don't generate these links to avoid broken references

        return nav_links

    def generate_agents_md(self, dir_path: Path) -> str:
        """Generate AGENTS.md content for a directory."""
        rel_path = dir_path.relative_to(self.repo_root)
        inventory = self.get_directory_inventory(dir_path)
        nav_links = self.get_navigation_links(dir_path)

        # Determine the purpose based on directory structure
        purpose = self._infer_directory_purpose(dir_path)

        content = f"""# Codomyrmex Agents — {rel_path}

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: {datetime.now().strftime('%B %Y')}

## Purpose
{purpose}

## Active Components
"""

        if inventory:
            for item in inventory:
                if item.endswith('/'):
                    content += f"- `{item}` – Directory containing {item.rstrip('/')} components\n"
                else:
                    content += f"- `{item}` – Project file\n"
        else:
            content += "- No active components documented\n"

        content += """
## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
"""

        if 'parent' in nav_links:
            content += f"- **📁 Parent Directory**: [{rel_path.parent.name}](../README.md) - Parent directory documentation\n"
        content += f"- **🏠 Project Root**: [README](../../../README.md) - Main project documentation\n"
        if 'surface' in nav_links:
            surface_name = rel_path.parts[0]
            content += f"- **📦 {surface_name.title()}**: [{surface_name}](../../../{surface_name}/README.md) - {surface_name} documentation hub\n"

        return content

    def generate_readme_md(self, dir_path: Path) -> str:
        """Generate README.md content for a directory."""
        rel_path = dir_path.relative_to(self.repo_root)
        inventory = self.get_directory_inventory(dir_path)
        nav_links = self.get_navigation_links(dir_path)

        # Get purpose from existing AGENTS.md or infer
        purpose = self._infer_directory_purpose(dir_path)

        content = f"""# {rel_path.name}

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: {datetime.now().strftime('%B %Y')}

## Overview

{purpose}

## Directory Contents
"""

        if inventory:
            for item in inventory:
                if item.endswith('/'):
                    content += f"- `{item}` – Subdirectory\n"
                else:
                    content += f"- `{item}` – File\n"
        else:
            content += "No files or subdirectories.\n"

        content += """
## Navigation
"""

        if 'parent' in nav_links:
            content += f"- **Parent Directory**: [{rel_path.parent.name}](../README.md)\n"
        content += "- **Project Root**: [README](../../../README.md)\n"

        return content

    def _infer_directory_purpose(self, dir_path: Path) -> str:
        """Infer the purpose of a directory based on its path and contents."""
        rel_path = dir_path.relative_to(self.repo_root)
        path_str = str(rel_path)

        # Surface-level purposes
        if len(rel_path.parts) == 1:
            surface = rel_path.parts[0]
            purposes = {
                'src': 'Hosts core source code and agent-enabled services for the Codomyrmex platform.',
                'scripts': 'Maintenance and automation utilities for project management.',
                'docs': 'Documentation components and guides for the Codomyrmex platform.',
                'config': 'Configuration templates and examples.',
                'testing': 'Test suites and validation for the Codomyrmex platform.',
                'projects': 'Project workspace and templates.',
                'cursorrules': 'Coding standards and automation rules.',
                'examples': 'Example implementations and demonstrations.'
            }
            return purposes.get(surface, f'Contains {surface} components for the Codomyrmex platform.')

        # Subdirectory purposes based on patterns
        if 'test' in path_str.lower():
            return 'Test files and validation suites.'
        if 'doc' in path_str.lower():
            return 'Documentation files and guides.'
        if 'example' in path_str.lower():
            return 'Example implementations and demonstrations.'
        if 'script' in path_str.lower():
            return 'Automation and utility scripts.'
        if 'config' in path_str.lower():
            return 'Configuration files and templates.'

        # Default purpose
        return f'Contains components for the {rel_path.parts[0]} system.'

    def process_directory(self, dir_path: Path) -> None:
        """Process a single directory, creating/updating documentation files."""
        agents_path = dir_path / 'AGENTS.md'
        readme_path = dir_path / 'README.md'

        rel_path = dir_path.relative_to(self.repo_root)

        # Create or update AGENTS.md
        content = self.generate_agents_md(dir_path)
        agents_path.write_text(content, encoding='utf-8')
        if agents_path.exists():
            logger.info(f"Updated AGENTS.md for {rel_path}")
        else:
            logger.info(f"Created AGENTS.md for {rel_path}")
        self.generated_count += 1

        # Create or update README.md
        content = self.generate_readme_md(dir_path)
        readme_path.write_text(content, encoding='utf-8')
        if readme_path.exists():
            logger.info(f"Updated README.md for {rel_path}")
        else:
            logger.info(f"Created README.md for {rel_path}")
        self.generated_count += 1

    def bootstrap_repository(self) -> None:
        """Bootstrap documentation for the entire repository."""
        logger.info("Starting documentation bootstrap...")

        # Walk through all directories under surface roots
        for surface_root in self.SURFACE_ROOTS:
            surface_path = self.repo_root / surface_root
            if not surface_path.exists():
                logger.warning(f"Surface root not found: {surface_root}")
                continue

            logger.info(f"Processing surface: {surface_root}")

            # Process the surface root directory itself
            if self.should_process_directory(surface_path):
                self.process_directory(surface_path)

            # Walk all subdirectories recursively
            for dir_path in surface_path.rglob('*'):
                if dir_path.is_dir() and self.should_process_directory(dir_path):
                    self.process_directory(dir_path)

        logger.info(f"Bootstrap complete: generated {self.generated_count} files")


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Bootstrap AGENTS.md and README.md files across the repository"
    )
    parser.add_argument(
        '--repo-root', type=Path, default=Path.cwd(),
        help='Repository root directory'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview changes without creating files'
    )

    args = parser.parse_args()

    bootstrapper = DocumentationBootstrapper(args.repo_root)

    if args.dry_run:
        print("DRY RUN MODE - No files will be created")
        print("This would process the following surfaces:")
        for surface in bootstrapper.SURFACE_ROOTS:
            print(f"  - {surface}/")
        print("\nExcluding:")
        for excluded in bootstrapper.EXCLUDED_DIRS:
            print(f"  - {excluded}/")
        return

    bootstrapper.bootstrap_repository()

    print("\n📊 Bootstrap Summary:")
    print(f"   Generated files: {bootstrapper.generated_count}")


if __name__ == '__main__':
    main()
