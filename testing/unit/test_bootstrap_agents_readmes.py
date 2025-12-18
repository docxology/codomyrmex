#!/usr/bin/env python3
"""
Unit tests for the bootstrap_agents_readmes script.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

# Import the bootstrapper
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts' / 'documentation'))
from bootstrap_agents_readmes import DocumentationBootstrapper


class TestDocumentationBootstrapper:
    """Test cases for DocumentationBootstrapper."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp()).resolve()
        self.bootstrapper = DocumentationBootstrapper(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_should_process_directory_excludes_output(self):
        """Test that output directories are excluded."""
        # Create a mock output directory
        output_dir = self.temp_dir / 'output'
        output_dir.mkdir()

        assert not self.bootstrapper.should_process_directory(output_dir)

    def test_should_process_directory_excludes_at_output(self):
        """Test that @output directories are excluded."""
        # Create a mock @output directory
        at_output_dir = self.temp_dir / '@output'
        at_output_dir.mkdir()

        assert not self.bootstrapper.should_process_directory(at_output_dir)

    def test_should_process_directory_excludes_dot_directories(self):
        """Test that dot directories are excluded."""
        # Create a mock .git directory
        dot_dir = self.temp_dir / '.git'
        dot_dir.mkdir()

        assert not self.bootstrapper.should_process_directory(dot_dir)

    def test_should_process_directory_allows_surface_roots(self):
        """Test that surface root directories are allowed."""
        # Create a mock scripts directory
        scripts_dir = self.temp_dir / 'scripts'
        scripts_dir.mkdir()

        # Temporarily patch the repo_root to make scripts_dir appear as a surface root
        with patch.object(self.bootstrapper, 'repo_root', self.temp_dir):
            assert self.bootstrapper.should_process_directory(scripts_dir)

    def test_should_process_directory_allows_surface_subdirs(self):
        """Test that subdirectories under surface roots are allowed."""
        # Create a mock scripts/documentation directory
        scripts_dir = self.temp_dir / 'scripts'
        scripts_dir.mkdir()
        doc_dir = scripts_dir / 'documentation'
        doc_dir.mkdir()

        # Temporarily patch the repo_root
        with patch.object(self.bootstrapper, 'repo_root', self.temp_dir):
            assert self.bootstrapper.should_process_directory(doc_dir)

    def test_get_directory_inventory_excludes_special_files(self):
        """Test that special files are excluded from inventory."""
        # Create test directory with various files
        test_dir = self.temp_dir / 'test'
        test_dir.mkdir()

        # Create normal files
        (test_dir / 'normal.py').touch()
        (test_dir / 'config.json').touch()

        # Create excluded files
        (test_dir / 'AGENTS.md').touch()
        (test_dir / 'README.md').touch()
        (test_dir / '.git').touch()
        (test_dir / '__pycache__').mkdir()

        inventory = self.bootstrapper.get_directory_inventory(test_dir)

        # Should include normal.py, config.json, and README.md, but exclude AGENTS.md and special dirs
        assert 'normal.py' in inventory
        assert 'config.json' in inventory
        assert 'README.md' in inventory
        assert 'AGENTS.md' not in inventory
        assert '.git' not in inventory
        assert '__pycache__/' not in inventory

    def test_generate_agents_md_basic_structure(self):
        """Test that generated AGENTS.md has required structure."""
        # Create test directory
        test_dir = self.temp_dir / 'test'
        test_dir.mkdir()
        (test_dir / 'file.py').touch()

        content = self.bootstrapper.generate_agents_md(test_dir)

        # Check required sections
        assert '# Codomyrmex Agents — test' in content
        assert '## Purpose' in content
        assert '## Active Components' in content
        assert '## Operating Contracts' in content
        assert '## Navigation Links' in content

        # Check inventory
        assert '- `file.py` – Project file' in content

    def test_generate_readme_md_basic_structure(self):
        """Test that generated README.md has basic structure."""
        # Create test directory
        test_dir = self.temp_dir / 'test'
        test_dir.mkdir()
        (test_dir / 'file.py').touch()

        content = self.bootstrapper.generate_readme_md(test_dir)

        # Check basic structure
        assert '# test' in content
        assert '## Overview' in content
        assert '## Directory Contents' in content

        # Check inventory
        assert '- `file.py` – File' in content

    def test_get_navigation_links_with_existing_files(self):
        """Test navigation link generation when parent/surface READMEs exist."""
        # Create directory structure
        scripts_dir = self.temp_dir / 'scripts'
        scripts_dir.mkdir()

        test_dir = scripts_dir / 'test'
        test_dir.mkdir()

        # Create parent README
        (scripts_dir / 'README.md').touch()

        # Temporarily patch repo_root
        with patch.object(self.bootstrapper, 'repo_root', self.temp_dir):
            nav_links = self.bootstrapper.get_navigation_links(test_dir)

            assert 'root' in nav_links
            assert nav_links['root'] == '../../README.md'
            assert 'parent' in nav_links
            assert nav_links['parent'] == '../README.md'

    def test_bootstrap_creates_files(self):
        """Test that bootstrap creates AGENTS.md and README.md files."""
        # Create test directory structure
        scripts_dir = self.temp_dir / 'scripts'
        scripts_dir.mkdir()

        test_dir = scripts_dir / 'test'
        test_dir.mkdir()
        (test_dir / 'file.py').touch()

        # Temporarily patch repo_root
        with patch.object(self.bootstrapper, 'repo_root', self.temp_dir):
            self.bootstrapper.process_directory(test_dir)

            assert (test_dir / 'AGENTS.md').exists()
            assert (test_dir / 'README.md').exists()

    def test_bootstrap_skips_excluded_directories(self):
        """Test that bootstrap skips excluded directories."""
        # Create a surface root first
        scripts_dir = self.temp_dir / 'scripts'
        scripts_dir.mkdir()

        # Create excluded directory under surface root
        output_dir = scripts_dir / 'output'
        output_dir.mkdir()

        # Temporarily patch repo_root
        with patch.object(self.bootstrapper, 'repo_root', self.temp_dir):
            # Should not process excluded directories
            assert not self.bootstrapper.should_process_directory(output_dir)


class TestIntegrationWithValidator:
    """Integration tests with AGENTS structure validator."""

    def test_generated_agents_passes_validation(self):
        """Test that generated AGENTS.md files pass structure validation."""
        # This would require importing the validator, but for now we'll test
        # that the generated content has the expected structure
        temp_dir = Path(tempfile.mkdtemp())
        try:
            bootstrapper = DocumentationBootstrapper(temp_dir)

            # Create test directory
            test_dir = temp_dir / 'scripts' / 'test'
            test_dir.mkdir(parents=True)
            (test_dir / 'file.py').touch()

            # Generate AGENTS.md
            with patch.object(bootstrapper, 'repo_root', temp_dir):
                content = bootstrapper.generate_agents_md(test_dir)

                # Check that all required sections are present
                required_sections = [
                    '## Purpose',
                    '## Active Components',
                    '## Operating Contracts',
                    '## Navigation Links'
                ]

                for section in required_sections:
                    assert section in content, f"Missing section: {section}"

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
