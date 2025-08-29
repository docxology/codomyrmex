"""Unit tests for template module."""

import pytest
import sys
import os
from pathlib import Path


class TestTemplate:
    """Test cases for template module functionality."""

    def test_template_directory_exists(self, code_dir):
        """Test that template directory exists."""
        template_dir = code_dir / "template"
        assert template_dir.exists()
        assert template_dir.is_dir()

    def test_template_directory_is_empty(self, code_dir):
        """Test that template directory is empty (as expected for a template)."""
        template_dir = code_dir / "template"

        # List all items in the template directory
        items = list(template_dir.iterdir())

        # Template directory should be empty or contain only hidden files
        non_hidden_items = [item for item in items if not item.name.startswith('.')]

        # The template directory is expected to be empty
        assert len(non_hidden_items) == 0

    def test_template_module_discovery(self, code_dir):
        """Test that the template module can be discovered."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # Test that the template directory is accessible
        template_path = code_dir / "template"
        assert template_path.exists()

        # Verify it's a directory that can be used as a module base
        assert template_path.is_dir()

    def test_template_as_placeholder(self, code_dir):
        """Test that template serves as a proper placeholder directory."""
        template_dir = code_dir / "template"

        # Template should exist as an empty directory
        assert template_dir.exists()
        assert template_dir.is_dir()

        # Should be usable as a starting point (empty means no conflicts)
        items = list(template_dir.iterdir())
        assert len(items) == 0 or all(item.name.startswith('.') for item in items)

    def test_template_directory_structure(self, code_dir):
        """Test template directory structure."""
        template_dir = code_dir / "template"

        # Basic directory properties
        assert template_dir.exists()
        assert template_dir.is_dir()

        # Should be readable and writable (for copying as template)
        assert os.access(template_dir, os.R_OK)
        assert os.access(template_dir, os.W_OK)

    def test_template_module_inheritance_pattern(self, code_dir):
        """Test that template follows the module inheritance pattern."""
        # The template directory should follow the same pattern as other modules
        # but be empty to serve as a clean starting point

        template_dir = code_dir / "template"
        assert template_dir.exists()

        # While template is empty, other modules have __init__.py
        # This test verifies the template is truly empty as intended
        python_files = list(template_dir.glob("*.py"))
        assert len(python_files) == 0

        # Should not have subdirectories (unlike other modules)
        subdirs = [item for item in template_dir.iterdir() if item.is_dir()]
        assert len(subdirs) == 0

    def test_template_can_be_copied(self, code_dir, tmp_path):
        """Test that template directory can be copied (used as template)."""
        import shutil

        template_dir = code_dir / "template"
        target_dir = tmp_path / "copied_template"

        # Should be able to copy the template directory
        shutil.copytree(template_dir, target_dir)

        # Copied directory should exist and be empty
        assert target_dir.exists()
        assert target_dir.is_dir()

        copied_items = list(target_dir.iterdir())
        assert len(copied_items) == 0

    def test_template_module_path_resolution(self, code_dir):
        """Test template module path resolution."""
        template_dir = code_dir / "template"

        # Path should be absolute and resolvable
        assert template_dir.is_absolute()
        assert template_dir.exists()

        # Should be able to resolve relative to code directory
        assert template_dir == code_dir / "template"

    def test_template_placeholder_behavior(self, code_dir):
        """Test that template behaves as expected placeholder."""
        template_dir = code_dir / "template"

        # Should exist but be empty
        assert template_dir.exists()
        assert template_dir.is_dir()

        # Empty directory is the expected state for a template
        contents = list(template_dir.iterdir())
        assert len(contents) == 0

    def test_template_vs_other_modules(self, code_dir):
        """Test how template differs from other modules."""
        template_dir = code_dir / "template"

        # Template should be empty while other modules have content
        assert template_dir.exists()

        # Compare with a known module that has content
        ai_code_editing_dir = code_dir / "codomyrmex" / "ai_code_editing"
        assert ai_code_editing_dir.exists()

        # Template should have fewer items than a developed module
        template_items = list(template_dir.iterdir())
        ai_items = list(ai_code_editing_dir.iterdir())

        # Template should be much emptier than developed modules
        assert len(template_items) <= len(ai_items)

        # Specifically, template should have no Python files
        python_files = list(template_dir.glob("*.py"))
        assert len(python_files) == 0
