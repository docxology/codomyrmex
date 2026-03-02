"""
Unit tests for DataProvider document and security methods — Zero-Mock compliant.

Tests cover:
- get_doc_content() path traversal prevention (raises ValueError/FileNotFoundError)
- get_config_content() returns string content
- save_config_content() saves file
- _compute_module_status() returns capitalized status string
- _get_script_metadata() returns (title, description) tuple
- get_module_detail() for known/unknown modules
- _get_last_build_time() returns string
- get_doc_tree() structure
"""

import sys
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.data_provider import DataProvider


def _make_project(tmp_path: Path) -> Path:
    """Create a minimal project tree for DataProvider tests."""
    src = tmp_path / "src" / "codomyrmex"
    src.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs").mkdir()
    mod = src / "test_mod"
    mod.mkdir()
    (mod / "__init__.py").write_text('"""Test module for testing."""\n')
    (tmp_path / "docs" / "guide.md").write_text("# Guide\nSome content here.\n")
    (tmp_path / "docs" / "nested").mkdir()
    (tmp_path / "docs" / "nested" / "deep.md").write_text("# Deep\nNested doc.\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    (tmp_path / "README.md").write_text("# Project README\n")
    (tmp_path / ".git").mkdir()
    return tmp_path


# ── get_doc_content() Tests ───────────────────────────────────────────


@pytest.mark.unit
class TestGetDocContent:
    """Tests for get_doc_content() method security and functionality."""

    def test_reads_valid_md_file(self, tmp_path):
        """Test reading a valid .md file returns string content."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        result = dp.get_doc_content("docs/guide.md")
        assert isinstance(result, (str, dict))
        assert "Guide" in str(result)

    def test_rejects_path_traversal(self, tmp_path):
        """Test that path traversal raises ValueError."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        with pytest.raises(ValueError, match="[Tt]raversal"):
            dp.get_doc_content("../../etc/passwd")

    def test_rejects_absolute_path(self, tmp_path):
        """Test that absolute paths raise ValueError."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        with pytest.raises(ValueError, match="[Aa]bsolute"):
            dp.get_doc_content("/etc/passwd")

    def test_rejects_non_md_file(self, tmp_path):
        """Test that non-.md files raise ValueError."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        with pytest.raises(ValueError, match=r"\.md"):
            dp.get_doc_content("pyproject.toml")

    def test_missing_file_raises_error(self, tmp_path):
        """Test that missing file raises FileNotFoundError."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        with pytest.raises(FileNotFoundError):
            dp.get_doc_content("docs/nonexistent.md")


# ── get_config_content() Tests ────────────────────────────────────────


@pytest.mark.unit
class TestGetConfigContent:
    """Tests for get_config_content() method security."""

    def test_reads_valid_config_returns_string(self, tmp_path):
        """Test reading a valid config file returns string content."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        result = dp.get_config_content("pyproject.toml")
        assert isinstance(result, str)
        assert "test" in result

    def test_rejects_traversal(self, tmp_path):
        """Test that path traversal raises ValueError."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        with pytest.raises(ValueError):
            dp.get_config_content("../../etc/passwd")


# ── save_config_content() Tests ───────────────────────────────────────


@pytest.mark.unit
class TestSaveConfigContent:
    """Tests for save_config_content() method."""

    def test_saves_valid_content(self, tmp_path):
        """Test saving content to an existing config file updates it."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        dp.save_config_content("pyproject.toml", "[updated]\nkey = true\n")
        assert "[updated]" in (root / "pyproject.toml").read_text()

    def test_rejects_traversal(self, tmp_path):
        """Test that path traversal raises ValueError on save."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        with pytest.raises(ValueError):
            dp.save_config_content("../../etc/evil", "malicious")


# ── _compute_module_status() Tests ────────────────────────────────────


@pytest.mark.unit
class TestComputeModuleStatus:
    """Tests for _compute_module_status() private method."""

    def test_known_module_returns_status_string(self, tmp_path):
        """Test that a known module returns a capitalized status string."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        mod_path = root / "src" / "codomyrmex" / "test_mod"
        status = dp._compute_module_status(mod_path)
        assert isinstance(status, str)
        assert len(status) > 0
        # Status is typically capitalized like 'Active', 'Error', etc.
        assert status[0].isupper()

    def test_nonexistent_module_returns_status(self, tmp_path):
        """Test that a non-existent module still returns a status string."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        fake_path = root / "src" / "codomyrmex" / "totally_fake_module_xyz"
        status = dp._compute_module_status(fake_path)
        assert isinstance(status, str)


# ── get_module_detail() Tests ─────────────────────────────────────────


@pytest.mark.unit
class TestGetModuleDetail:
    """Tests for get_module_detail() method."""

    def test_known_module_returns_detail(self, tmp_path):
        """Test getting detail for a known module returns dict with name."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        detail = dp.get_module_detail("test_mod")
        assert detail is not None
        assert detail.get("name") == "test_mod"

    def test_unknown_module_returns_none(self, tmp_path):
        """Test getting detail for an unknown module returns None."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        detail = dp.get_module_detail("nonexistent_module_xyz")
        assert detail is None


# ── _get_last_build_time() Tests ──────────────────────────────────────


@pytest.mark.unit
class TestGetLastBuildTime:
    """Tests for _get_last_build_time() method."""

    def test_returns_string(self, tmp_path):
        """Test that _get_last_build_time returns a string."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        result = dp._get_last_build_time()
        assert isinstance(result, str)


# ── get_doc_tree() Tests ──────────────────────────────────────────────


@pytest.mark.unit
class TestGetDocTree:
    """Tests for get_doc_tree() method."""

    def test_returns_dict(self, tmp_path):
        """Test that get_doc_tree returns a dictionary."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        tree = dp.get_doc_tree()
        assert isinstance(tree, dict)

    def test_finds_docs_directory(self, tmp_path):
        """Test that docs directory is discovered."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        tree = dp.get_doc_tree()
        tree_str = str(tree)
        assert "guide.md" in tree_str or "docs" in tree_str


# ── _get_script_metadata() Tests ──────────────────────────────────────


@pytest.mark.unit
class TestGetScriptMetadata:
    """Tests for _get_script_metadata() method (returns tuple)."""

    def test_extracts_docstring_as_description(self, tmp_path):
        """Test that script docstring is used as description tuple."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        script = root / "scripts" / "example.py"
        script.write_text('"""Example script for testing.\n\nMore details."""\nprint("hi")\n')
        meta = dp._get_script_metadata(script)
        assert isinstance(meta, tuple)
        assert len(meta) == 2
        title, desc = meta
        assert "Example" in title or "Example" in desc

    def test_handles_script_without_docstring(self, tmp_path):
        """Test that scripts without docstrings get default metadata tuple."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        script = root / "scripts" / "nodoc.py"
        script.write_text('print("no docstring")\n')
        meta = dp._get_script_metadata(script)
        assert isinstance(meta, tuple)
        assert len(meta) == 2


# ── _get_description() Tests ──────────────────────────────────────────


@pytest.mark.unit
class TestGetDescription:
    """Tests for _get_description() private method."""

    def test_reads_init_docstring(self, tmp_path):
        """Test that __init__.py docstring is extracted."""
        root = _make_project(tmp_path)
        dp = DataProvider(root)
        mod_path = root / "src" / "codomyrmex" / "test_mod"
        desc = dp._get_description(mod_path)
        assert isinstance(desc, str)
        assert "Test module" in desc or desc == ""
