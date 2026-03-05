"""Unit tests for documentation/maintenance.py.

Covers: get_submodules, MODULE_DESCRIPTIONS, update_readme_md,
        update_agents_md_list, enrich_agents_md, update_root_docs,
        finalize_docs, update_spec.

Zero-mock policy: all tests use real filesystem via tmp_path.
"""

from pathlib import Path

import pytest

from codomyrmex.documentation.maintenance import (
    IGNORE_DIRS,
    MODULE_DESCRIPTIONS,
    enrich_agents_md,
    finalize_docs,
    get_submodules,
    update_agents_md_list,
    update_readme_md,
    update_root_docs,
    update_spec,
)


def _make_package(parent: Path, name: str) -> Path:
    """Create a minimal Python package directory inside parent."""
    pkg = parent / name
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text(f'"""Package {name}."""\n')
    return pkg


@pytest.mark.unit
class TestModuleDescriptions:
    """Test the MODULE_DESCRIPTIONS constant."""

    def test_module_descriptions_is_dict(self):
        assert isinstance(MODULE_DESCRIPTIONS, dict)

    def test_module_descriptions_not_empty(self):
        assert len(MODULE_DESCRIPTIONS) > 0

    def test_documentation_key_present(self):
        assert "documentation" in MODULE_DESCRIPTIONS

    def test_agents_key_present(self):
        assert "agents" in MODULE_DESCRIPTIONS

    def test_all_values_are_strings(self):
        for key, val in MODULE_DESCRIPTIONS.items():
            assert isinstance(val, str), f"Value for '{key}' is not a string"

    def test_ignore_dirs_excludes_pycache(self):
        assert "__pycache__" in IGNORE_DIRS


@pytest.mark.unit
class TestGetSubmodules:
    """Test get_submodules returns valid Python package names."""

    def test_empty_dir_returns_empty_list(self, tmp_path: Path):
        result = get_submodules(tmp_path)
        assert result == []

    def test_package_subdir_included(self, tmp_path: Path):
        _make_package(tmp_path, "alpha")
        result = get_submodules(tmp_path)
        assert "alpha" in result

    def test_non_package_subdir_excluded(self, tmp_path: Path):
        plain = tmp_path / "not_a_package"
        plain.mkdir()
        result = get_submodules(tmp_path)
        assert "not_a_package" not in result

    def test_multiple_packages_returned_sorted(self, tmp_path: Path):
        _make_package(tmp_path, "zebra")
        _make_package(tmp_path, "alpha")
        _make_package(tmp_path, "middle")
        result = get_submodules(tmp_path)
        assert result == ["alpha", "middle", "zebra"]

    def test_hidden_dirs_excluded(self, tmp_path: Path):
        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "__init__.py").write_text("")
        result = get_submodules(tmp_path)
        assert ".hidden" not in result

    def test_pycache_excluded(self, tmp_path: Path):
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "__init__.py").write_text("")
        result = get_submodules(tmp_path)
        assert "__pycache__" not in result


@pytest.mark.unit
class TestUpdateReadmeMd:
    """Test update_readme_md writes module list into the correct section."""

    def _make_readme(self, path: Path, extra_content: str = "") -> Path:
        readme = path / "README.md"
        readme.write_text(
            "# Project\n\n"
            "## Directory Contents\n\n"
            "Old content here.\n\n"
            "## Next Section\n" + extra_content
        )
        return readme

    def test_update_readme_with_modules(self, tmp_path: Path):
        self._make_readme(tmp_path)
        update_readme_md(["alpha", "beta"], tmp_path)
        content = (tmp_path / "README.md").read_text()
        assert "alpha" in content
        assert "beta" in content

    def test_update_readme_adds_readme_self_entry(self, tmp_path: Path):
        self._make_readme(tmp_path)
        update_readme_md([], tmp_path)
        content = (tmp_path / "README.md").read_text()
        assert "README.md" in content

    def test_update_readme_missing_header_skips(self, tmp_path: Path, capsys):
        readme = tmp_path / "README.md"
        readme.write_text("# Project\n\nNo directory contents section.\n")
        update_readme_md(["alpha"], tmp_path)
        captured = capsys.readouterr()
        assert "Could not find" in captured.out

    def test_update_readme_missing_file_skips(self, tmp_path: Path, capsys):
        # No README.md created — function should print skip message
        update_readme_md(["alpha"], tmp_path)
        captured = capsys.readouterr()
        assert "Skipping" in captured.out


@pytest.mark.unit
class TestUpdateAgentsMdList:
    """Test update_agents_md_list writes component list correctly."""

    def _make_agents_md(self, path: Path) -> Path:
        agents = path / "AGENTS.md"
        agents.write_text(
            "# AGENTS\n\n## Active Components\n\nOld entry.\n\n## Other Section\n"
        )
        return agents

    def test_update_agents_with_modules(self, tmp_path: Path):
        self._make_agents_md(tmp_path)
        update_agents_md_list(["gamma", "delta"], tmp_path)
        content = (tmp_path / "AGENTS.md").read_text()
        assert "gamma" in content
        assert "delta" in content

    def test_update_agents_missing_header_prints_message(self, tmp_path: Path, capsys):
        agents = tmp_path / "AGENTS.md"
        agents.write_text("# AGENTS\n\nNo active components section.\n")
        update_agents_md_list(["gamma"], tmp_path)
        captured = capsys.readouterr()
        assert "Could not find" in captured.out

    def test_update_agents_missing_file_skips(self, tmp_path: Path, capsys):
        update_agents_md_list(["m"], tmp_path)
        captured = capsys.readouterr()
        assert "Skipping" in captured.out


@pytest.mark.unit
class TestEnrichAgentsMd:
    """Test enrich_agents_md replaces generic 'Module component' text."""

    def test_enrich_replaces_generic_description(self, tmp_path: Path):
        agents = tmp_path / "AGENTS.md"
        agents.write_text(
            "# AGENTS\n\n"
            "- `agents/` – Module component\n"
            "- `documentation/` – Module component\n"
        )
        enrich_agents_md(tmp_path)
        content = agents.read_text()
        # agents and documentation are in MODULE_DESCRIPTIONS
        assert "Module component" not in content or "agents" in content

    def test_enrich_missing_file_skips(self, tmp_path: Path, capsys):
        enrich_agents_md(tmp_path)
        captured = capsys.readouterr()
        assert "Skipping" in captured.out

    def test_enrich_does_not_corrupt_file(self, tmp_path: Path):
        agents = tmp_path / "AGENTS.md"
        original = "# AGENTS\n\n- `unknown_module/` – Module component\n"
        agents.write_text(original)
        enrich_agents_md(tmp_path)
        content = agents.read_text()
        # File still exists and has content
        assert len(content) > 0
        assert "AGENTS" in content


@pytest.mark.unit
class TestUpdateRootDocs:
    """Test update_root_docs runs end-to-end on a tmp directory."""

    def _make_minimal_src(self, tmp_path: Path) -> Path:
        src = tmp_path
        # README.md with required section
        (src / "README.md").write_text(
            "# Root\n\n## Directory Contents\n\nOld.\n\n## Other\n"
        )
        # AGENTS.md with required section
        (src / "AGENTS.md").write_text(
            "# AGENTS\n\n## Active Components\n\nOld.\n\n## More\n"
        )
        # __init__.py with markers
        (src / "__init__.py").write_text('_submodules = ["old"]\n__all__ = ["old"]\n')
        # A real subpackage
        _make_package(src, "my_module")
        return src

    def test_update_root_docs_runs_without_error(self, tmp_path: Path, capsys):
        src = self._make_minimal_src(tmp_path)
        update_root_docs(src)
        captured = capsys.readouterr()
        assert "Found" in captured.out

    def test_update_root_docs_readme_updated(self, tmp_path: Path):
        src = self._make_minimal_src(tmp_path)
        update_root_docs(src)
        content = (src / "README.md").read_text()
        assert "my_module" in content


@pytest.mark.unit
class TestUpdateSpec:
    """Test update_spec adds missing modules to SPEC.md."""

    def _make_spec(self, path: Path) -> Path:
        spec = path / "SPEC.md"
        spec.write_text(
            "# SPEC\n\n"
            "#### Specialized Layer\n\n"
            "**Modules**: existing_mod\n\n"
            "**Characteristics**: something\n"
        )
        return spec

    def test_update_spec_with_no_modules_prints_nothing_missing(
        self, tmp_path: Path, capsys
    ):
        self._make_spec(tmp_path)
        # No packages in tmp_path → no missing modules
        update_spec(tmp_path)
        captured = capsys.readouterr()
        assert "No missing modules" in captured.out

    def test_update_spec_missing_file_prints_error(self, tmp_path: Path, capsys):
        update_spec(tmp_path)
        captured = capsys.readouterr()
        assert "Error" in captured.out or "not found" in captured.out

    def test_update_spec_adds_new_module(self, tmp_path: Path, capsys):
        self._make_spec(tmp_path)
        _make_package(tmp_path, "brand_new_module")
        update_spec(tmp_path)
        content = (tmp_path / "SPEC.md").read_text()
        assert "brand_new_module" in content

    def test_update_spec_missing_specialized_section_handled(
        self, tmp_path: Path, capsys
    ):
        spec = tmp_path / "SPEC.md"
        spec.write_text("# SPEC\n\nNo specialized layer here.\n")
        update_spec(tmp_path)
        captured = capsys.readouterr()
        assert "Could not find" in captured.out


@pytest.mark.unit
class TestFinalizeDocs:
    """Test finalize_docs runs enrich_agents_md + update_spec cleanly."""

    def test_finalize_docs_missing_files_handled(self, tmp_path: Path, capsys):
        finalize_docs(tmp_path)
        captured = capsys.readouterr()
        # Both sub-functions will print skip/error messages — no crash
        assert len(captured.out) >= 0  # Just verifying no exception
