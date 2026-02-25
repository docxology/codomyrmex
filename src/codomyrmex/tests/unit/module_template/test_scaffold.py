"""Tests for module_template scaffold module.

Covers scaffold_new_module, _copy_and_customize, _create_core_module,
list_template_files, and error paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.module_template.scaffold import (
    TEMPLATE_FILES,
    _copy_and_customize,
    _create_core_module,
    list_template_files,
    scaffold_new_module,
)

# ---------------------------------------------------------------------------
# TEMPLATE_FILES constant
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTemplateFilesConstant:
    """Verify the TEMPLATE_FILES list is well-formed."""

    def test_is_non_empty_list(self) -> None:
        assert isinstance(TEMPLATE_FILES, list)
        assert len(TEMPLATE_FILES) > 0

    def test_contains_init_py(self) -> None:
        assert "__init__.py" in TEMPLATE_FILES

    def test_contains_readme(self) -> None:
        assert "README.md" in TEMPLATE_FILES


# ---------------------------------------------------------------------------
# scaffold_new_module
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScaffoldNewModule:
    """Tests for the primary scaffold_new_module function."""

    def test_creates_module_directory(self, tmp_path: Path) -> None:
        """scaffold_new_module should create a directory for the new module."""
        result = scaffold_new_module("test_mod", target_path=tmp_path)
        assert result.exists()
        assert result.is_dir()
        assert result.name == "test_mod"

    def test_returns_correct_path(self, tmp_path: Path) -> None:
        result = scaffold_new_module("my_module", target_path=tmp_path)
        assert result == tmp_path / "my_module"

    def test_creates_core_python_file(self, tmp_path: Path) -> None:
        """A <module_name>.py should be generated in the new module dir."""
        result = scaffold_new_module("my_module", target_path=tmp_path)
        core_file = result / "my_module.py"
        assert core_file.exists()
        content = core_file.read_text(encoding="utf-8")
        assert "class MyModule" in content

    def test_core_file_contains_description(self, tmp_path: Path) -> None:
        result = scaffold_new_module(
            "my_module", target_path=tmp_path, description="A test module"
        )
        core_file = result / "my_module.py"
        content = core_file.read_text(encoding="utf-8")
        assert "A test module" in content

    def test_copies_template_files(self, tmp_path: Path) -> None:
        """Template files that exist in the source should be copied."""
        result = scaffold_new_module("new_mod", target_path=tmp_path)
        # At least __init__.py should exist (it is in TEMPLATE_FILES and source)
        init_file = result / "__init__.py"
        assert init_file.exists()

    def test_raises_on_invalid_module_name_uppercase(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Invalid module name"):
            scaffold_new_module("BadName", target_path=tmp_path)

    def test_raises_on_invalid_module_name_starts_with_number(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(ValueError, match="Invalid module name"):
            scaffold_new_module("1module", target_path=tmp_path)

    def test_raises_on_invalid_module_name_hyphen(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Invalid module name"):
            scaffold_new_module("my-module", target_path=tmp_path)

    def test_raises_on_empty_module_name(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Invalid module name"):
            scaffold_new_module("", target_path=tmp_path)

    def test_raises_on_existing_directory(self, tmp_path: Path) -> None:
        """FileExistsError if the target already exists."""
        (tmp_path / "existing_mod").mkdir()
        with pytest.raises(FileExistsError):
            scaffold_new_module("existing_mod", target_path=tmp_path)

    def test_text_replacements_applied(self, tmp_path: Path) -> None:
        """Module name replacements should appear in generated files."""
        result = scaffold_new_module("data_pipeline", target_path=tmp_path)
        init_file = result / "__init__.py"
        if init_file.exists():
            content = init_file.read_text(encoding="utf-8")
            # The init file should have had "module_template" replaced
            # (only if the template itself contained that string)
            assert "module_template" not in content or "data_pipeline" in content

    def test_accepts_simple_valid_names(self, tmp_path: Path) -> None:
        """Various valid snake_case names should work."""
        for name in ["a", "abc", "my_module", "mod123", "a1b2c3"]:
            sub = tmp_path / name
            sub_parent = tmp_path / f"parent_{name}"
            sub_parent.mkdir()
            result = scaffold_new_module(name, target_path=sub_parent)
            assert result.exists()


# ---------------------------------------------------------------------------
# _copy_and_customize helper
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCopyAndCustomize:
    """Tests for the _copy_and_customize internal helper."""

    def test_performs_replacements(self, tmp_path: Path) -> None:
        src = tmp_path / "src.md"
        dst = tmp_path / "dst.md"
        src.write_text("Hello module_template world", encoding="utf-8")
        _copy_and_customize(
            src, dst, {"module_template": "my_mod"}, description="", author=""
        )
        content = dst.read_text(encoding="utf-8")
        assert "my_mod" in content
        assert "module_template" not in content

    def test_adds_description_to_readme(self, tmp_path: Path) -> None:
        src = tmp_path / "README.md"
        dst = tmp_path / "out_README.md"
        src.write_text("# Title\nSome content", encoding="utf-8")
        _copy_and_customize(
            src, dst, {}, description="My great description", author=""
        )
        # Rename dst so its .name is README.md (the function checks dst.name)
        # Actually the function checks dst.name — let's use a proper name
        dst2 = tmp_path / "sub"
        dst2.mkdir()
        readme_dst = dst2 / "README.md"
        _copy_and_customize(
            src, readme_dst, {}, description="My great description", author=""
        )
        content = readme_dst.read_text(encoding="utf-8")
        assert "My great description" in content

    def test_falls_back_to_copy_on_binary(self, tmp_path: Path) -> None:
        """If read_text fails, should fall back to shutil.copy2."""
        src = tmp_path / "binary.bin"
        dst = tmp_path / "out.bin"
        src.write_bytes(b"\x00\x01\x02\x03")
        # This should not raise — it falls back to copy
        _copy_and_customize(src, dst, {}, description="", author="")
        assert dst.exists()


# ---------------------------------------------------------------------------
# _create_core_module helper
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCreateCoreModule:
    """Tests for the _create_core_module internal helper."""

    def test_creates_file(self, tmp_path: Path) -> None:
        path = tmp_path / "my_module.py"
        _create_core_module(path, "my_module", "A description")
        assert path.exists()

    def test_file_contains_class(self, tmp_path: Path) -> None:
        path = tmp_path / "my_module.py"
        _create_core_module(path, "my_module", "A description")
        content = path.read_text(encoding="utf-8")
        assert "class MyModule" in content

    def test_class_name_from_snake_case(self, tmp_path: Path) -> None:
        path = tmp_path / "data_pipeline.py"
        _create_core_module(path, "data_pipeline", "")
        content = path.read_text(encoding="utf-8")
        assert "class DataPipeline" in content

    def test_contains_description(self, tmp_path: Path) -> None:
        path = tmp_path / "mod.py"
        _create_core_module(path, "mod", "Custom description here")
        content = path.read_text(encoding="utf-8")
        assert "Custom description here" in content

    def test_default_description_when_empty(self, tmp_path: Path) -> None:
        path = tmp_path / "mod.py"
        _create_core_module(path, "mod", "")
        content = path.read_text(encoding="utf-8")
        assert "Core implementation for this module." in content

    def test_contains_create_function(self, tmp_path: Path) -> None:
        path = tmp_path / "my_module.py"
        _create_core_module(path, "my_module", "")
        content = path.read_text(encoding="utf-8")
        assert "def create_my_module" in content

    def test_contains_process_method(self, tmp_path: Path) -> None:
        path = tmp_path / "my_module.py"
        _create_core_module(path, "my_module", "")
        content = path.read_text(encoding="utf-8")
        assert "def process" in content


# ---------------------------------------------------------------------------
# list_template_files
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestListTemplateFiles:
    """Tests for the list_template_files utility."""

    def test_returns_list(self) -> None:
        result = list_template_files()
        assert isinstance(result, list)

    def test_returns_non_empty(self) -> None:
        result = list_template_files()
        assert len(result) > 0

    def test_excludes_hidden_files(self) -> None:
        """Hidden files (starting with .) should not appear."""
        result = list_template_files()
        for name in result:
            assert not name.startswith(".")

    def test_contains_known_files(self) -> None:
        """Should contain at least scaffold.py and __init__.py."""
        result = list_template_files()
        assert "scaffold.py" in result
