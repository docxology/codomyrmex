"""Comprehensive unit tests for module_template.scaffold module.

Covers:
- scaffold_new_module: name validation, directory creation, file copying, customization
- _copy_and_customize: text replacement, description injection, error handling
- _create_core_module: class generation, template content
- list_template_files: file listing
- TEMPLATE_FILES: constant verification

Zero-Mock Policy: all tests use real filesystem via tempfile.
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.module_template.scaffold import (
    TEMPLATE_FILES,
    _create_core_module,
    list_template_files,
    scaffold_new_module,
)


# ===========================================================================
# TEMPLATE_FILES constant
# ===========================================================================

@pytest.mark.unit
class TestTemplateFiles:
    """Tests for TEMPLATE_FILES constant."""

    def test_is_list(self):
        assert isinstance(TEMPLATE_FILES, list)

    def test_contains_expected_files(self):
        for expected in ("__init__.py", "README.md", "AGENTS.md", "SPEC.md"):
            assert expected in TEMPLATE_FILES

    def test_all_strings(self):
        for f in TEMPLATE_FILES:
            assert isinstance(f, str)

    def test_has_reasonable_count(self):
        assert len(TEMPLATE_FILES) >= 5


# ===========================================================================
# scaffold_new_module - name validation
# ===========================================================================

@pytest.mark.unit
class TestScaffoldNameValidation:
    """Tests for module name validation in scaffold_new_module."""

    def test_invalid_name_uppercase(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Invalid module name"):
                scaffold_new_module("MyModule", target_path=Path(tmpdir))

    def test_invalid_name_starts_with_number(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Invalid module name"):
                scaffold_new_module("1bad", target_path=Path(tmpdir))

    def test_invalid_name_has_dash(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Invalid module name"):
                scaffold_new_module("my-module", target_path=Path(tmpdir))

    def test_invalid_name_has_space(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Invalid module name"):
                scaffold_new_module("my module", target_path=Path(tmpdir))

    def test_invalid_name_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Invalid module name"):
                scaffold_new_module("", target_path=Path(tmpdir))

    def test_valid_name_simple(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("mymod", target_path=Path(tmpdir))
            assert path.exists()
            assert path.name == "mymod"

    def test_valid_name_with_underscores(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("my_new_module", target_path=Path(tmpdir))
            assert path.exists()
            assert path.name == "my_new_module"

    def test_valid_name_with_numbers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("module2", target_path=Path(tmpdir))
            assert path.exists()


# ===========================================================================
# scaffold_new_module - directory creation
# ===========================================================================

@pytest.mark.unit
class TestScaffoldDirectoryCreation:
    """Tests for directory creation in scaffold_new_module."""

    def test_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("testmod", target_path=Path(tmpdir))
            assert path.is_dir()

    def test_directory_already_exists_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "existing"
            target.mkdir()
            with pytest.raises(FileExistsError, match="already exists"):
                scaffold_new_module("existing", target_path=Path(tmpdir))

    def test_returns_correct_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("newmod", target_path=Path(tmpdir))
            expected = Path(tmpdir) / "newmod"
            assert path == expected


# ===========================================================================
# scaffold_new_module - file creation
# ===========================================================================

@pytest.mark.unit
class TestScaffoldFileCreation:
    """Tests for file creation and customization."""

    def test_creates_core_module_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("testmod", target_path=Path(tmpdir))
            core_file = path / "testmod.py"
            assert core_file.exists()

    def test_core_module_contains_class(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("testmod", target_path=Path(tmpdir))
            core_file = path / "testmod.py"
            content = core_file.read_text()
            assert "class Testmod" in content

    def test_core_module_snake_case_to_class(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("my_cool_mod", target_path=Path(tmpdir))
            core_file = path / "my_cool_mod.py"
            content = core_file.read_text()
            assert "class MyCoolMod" in content

    def test_init_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("testmod", target_path=Path(tmpdir))
            init_file = path / "__init__.py"
            assert init_file.exists()

    def test_description_in_core_module(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module(
                "testmod",
                target_path=Path(tmpdir),
                description="A testing module for validation.",
            )
            core_file = path / "testmod.py"
            content = core_file.read_text()
            assert "A testing module for validation." in content

    def test_no_description_uses_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("testmod", target_path=Path(tmpdir))
            core_file = path / "testmod.py"
            content = core_file.read_text()
            assert "Core implementation for this module." in content

    def test_text_replacements_in_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = scaffold_new_module("testmod", target_path=Path(tmpdir))
            # Check that __init__.py has module name replacement
            init_file = path / "__init__.py"
            if init_file.exists():
                content = init_file.read_text()
                # module_template should be replaced with testmod
                assert "module_template" not in content or "testmod" in content


# ===========================================================================
# _create_core_module
# ===========================================================================

@pytest.mark.unit
class TestCreateCoreModule:
    """Tests for _create_core_module function."""

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "my_mod.py"
            _create_core_module(path, "my_mod", "Test description")
            assert path.exists()

    def test_file_content_has_class(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data_processor.py"
            _create_core_module(path, "data_processor", "Process data.")
            content = path.read_text()
            assert "class DataProcessor" in content
            assert "Process data." in content

    def test_file_has_process_method(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mymod.py"
            _create_core_module(path, "mymod", "")
            content = path.read_text()
            assert "def process(" in content

    def test_file_has_factory_function(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mymod.py"
            _create_core_module(path, "mymod", "")
            content = path.read_text()
            assert "def create_mymod" in content

    def test_process_raises_not_implemented(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mymod.py"
            _create_core_module(path, "mymod", "")
            content = path.read_text()
            assert "NotImplementedError" in content


# ===========================================================================
# list_template_files
# ===========================================================================

@pytest.mark.unit
class TestListTemplateFiles:
    """Tests for list_template_files function."""

    def test_returns_list(self):
        result = list_template_files()
        assert isinstance(result, list)

    def test_contains_strings(self):
        result = list_template_files()
        for item in result:
            assert isinstance(item, str)

    def test_includes_scaffold_py(self):
        result = list_template_files()
        assert "scaffold.py" in result

    def test_excludes_hidden_files(self):
        result = list_template_files()
        # .gitignore should not appear since the function filters startswith('.')
        for item in result:
            assert not item.startswith(".")

    def test_non_empty(self):
        result = list_template_files()
        assert len(result) > 0
