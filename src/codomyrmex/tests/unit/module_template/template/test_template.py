"""Unit tests for template module."""

import os
import sys

import pytest


@pytest.mark.unit
class TestTemplate:
    """Test cases for template module functionality."""

    def test_template_directory_exists(self, code_dir):
        """Test that template directory exists."""
        template_dir = code_dir / "codomyrmex" / "module_template"
        assert template_dir.exists()
        assert template_dir.is_dir()

    def test_template_directory_contains_template_files(self, code_dir):
        """Test that template directory contains the expected template files."""
        template_dir = code_dir / "codomyrmex" / "module_template"

        # List all items in the template directory
        items = list(template_dir.iterdir())

        # Template directory should contain template files
        non_hidden_items = [item for item in items if not item.name.startswith('.') and not item.name.endswith('.pyc')]

        # The template directory should contain essential template files
        expected_files = ['README.md', 'AGENTS.md', '__init__.py', 'scaffold.py']
        actual_files = [item.name for item in non_hidden_items]

        for expected_file in expected_files:
            assert expected_file in actual_files, f"Expected template file {expected_file} not found"

    def test_template_module_discovery(self, code_dir):
        """Test that the template module can be discovered."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # Test that the template directory is accessible
        template_path = code_dir / "codomyrmex" / "module_template"
        assert template_path.exists()

        # Verify it's a directory that can be used as a module base
        assert template_path.is_dir()

    def test_template_as_placeholder(self, code_dir):
        """Test that template serves as a proper template directory."""
        template_dir = code_dir / "codomyrmex" / "module_template"

        # Template should exist as a directory with template files
        assert template_dir.exists()
        assert template_dir.is_dir()

        # Should contain template files for module creation
        items = list(template_dir.iterdir())
        non_hidden_items = [item for item in items if not item.name.startswith('.') and not item.name.endswith('.pyc')]

        # Should have scaffolding files (Python and documentation)
        assert len(non_hidden_items) > 0

    def test_template_directory_structure(self, code_dir):
        """Test template directory structure."""
        template_dir = code_dir / "codomyrmex" / "module_template"

        # Basic directory properties
        assert template_dir.exists()
        assert template_dir.is_dir()

        # Should be readable and writable (for copying as template)
        assert os.access(template_dir, os.R_OK)
        assert os.access(template_dir, os.W_OK)

    def test_template_module_inheritance_pattern(self, code_dir):
        """Test that template follows the module inheritance pattern."""
        # The template directory should follow the same pattern as other modules
        # and contain scaffolding files for creating new modules

        template_dir = code_dir / "codomyrmex" / "module_template"
        assert template_dir.exists()

        # Template should have Python scaffolding files
        python_files = list(template_dir.glob("*.py"))
        assert len(python_files) >= 2  # At least __init__.py and scaffold.py

        # Should have __init__.py to be a proper Python package
        assert (template_dir / "__init__.py").exists()
        assert (template_dir / "scaffold.py").exists()

    def test_template_can_be_copied(self, code_dir, tmp_path):
        """Test that template directory can be copied (used as template)."""
        import shutil

        template_dir = code_dir / "codomyrmex" / "module_template"
        target_dir = tmp_path / "copied_template"

        # Should be able to copy the template directory
        shutil.copytree(template_dir, target_dir)

        # Copied directory should exist and contain template files
        assert target_dir.exists()
        assert target_dir.is_dir()

        copied_items = list(target_dir.iterdir())
        non_hidden_items = [item for item in copied_items if not item.name.startswith('.') and not item.name.endswith('.pyc')]

        # Should contain the essential template files
        expected_files = ['README.md', 'AGENTS.md', '__init__.py', 'scaffold.py']
        copied_files = [item.name for item in non_hidden_items]

        for expected_file in expected_files:
            assert expected_file in copied_files, f"Expected template file {expected_file} not found in copy"

    def test_template_module_path_resolution(self, code_dir):
        """Test template module path resolution."""
        template_dir = code_dir / "codomyrmex" / "module_template"

        # Path should be absolute and resolvable
        assert template_dir.is_absolute()
        assert template_dir.exists()

        # Should be able to resolve relative to code directory
        assert template_dir == code_dir / "codomyrmex" / "module_template"

    def test_template_placeholder_behavior(self, code_dir):
        """Test that template behaves as expected template directory."""
        template_dir = code_dir / "codomyrmex" / "module_template"

        # Should exist and contain template files
        assert template_dir.exists()
        assert template_dir.is_dir()

        # Should contain scaffolding files for module creation
        contents = list(template_dir.iterdir())
        non_hidden_items = [item for item in contents if not item.name.startswith('.') and not item.name.endswith('.pyc')]

        # Should have scaffolding files (Python and documentation)
        assert len(non_hidden_items) > 0

    def test_template_vs_other_modules(self, code_dir):
        """Test how template differs from other modules."""
        template_dir = code_dir / "codomyrmex" / "module_template"

        # Template should have scaffolding while other modules have full implementation
        assert template_dir.exists()

        # Compare with a known module that has content
        agents_dir = code_dir / "codomyrmex" / "agents"
        assert agents_dir.exists()

        # Template should have fewer items than a fully developed module
        template_items = list(template_dir.iterdir())
        agents_items = list(agents_dir.iterdir())

        # Template should be simpler than fully developed modules
        assert len(template_items) <= len(agents_items)

        # Template should have Python scaffolding files
        python_files = list(template_dir.glob("*.py"))
        assert len(python_files) >= 2  # At least __init__.py and scaffold.py
