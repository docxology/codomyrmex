"""Unit tests for RASP documentation compliance auditing.

Tests cover: ModuleAudit, audit_rasp, audit_documentation, is_package,
generate_report, and the RASP file completeness checks.

Zero-mock policy: All tests use real filesystem via tmp_path fixtures.
"""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestModuleAuditRaspFiles:
    """Test ModuleAudit RASP file detection (README.md, AGENTS.md, SPEC.md, PAI.md)."""

    def _make_module(self, tmp_path: Path, files: list[str] | None = None) -> Path:
        """Create a fake Python module directory with optional RASP files."""
        mod = tmp_path / "src" / "codomyrmex" / "test_module"
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text('"""Test module."""\n')
        for fname in (files or []):
            (mod / fname).write_text(
                f"# {fname.replace('.md', '')}\n\nThis file has real content "
                f"that is well above the fifty character minimum threshold.\n"
            )
        return mod

    def test_all_rasp_files_present_no_missing(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, ["README.md", "AGENTS.md", "SPEC.md", "PAI.md"])
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert audit.missing_docs == []

    def test_missing_pai_md_detected(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, ["README.md", "AGENTS.md", "SPEC.md"])
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert "PAI.md" in audit.missing_docs

    def test_missing_all_rasp_files(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, [])
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert set(audit.missing_docs) == {"README.md", "AGENTS.md", "SPEC.md", "PAI.md"}

    def test_placeholder_content_detected(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, ["AGENTS.md", "SPEC.md", "PAI.md"])
        # Create README.md with placeholder text
        (mod / "README.md").write_text("# New Module\nPlaceholder")
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert "README.md" in audit.placeholder_docs

    def test_short_content_detected_as_placeholder(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, ["AGENTS.md", "SPEC.md", "PAI.md"])
        # Content below 50 chars is treated as placeholder
        (mod / "README.md").write_text("# Short")
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert "README.md" in audit.placeholder_docs

    def test_py_typed_marker_detected(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, [])
        (mod / "py.typed").write_text("")
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert audit.has_py_typed is True

    def test_py_typed_marker_absent(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, [])
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert audit.has_py_typed is False

    def test_init_docstring_detected(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, [])
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert audit.init_has_docstring is True

    def test_init_without_docstring(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, [])
        (mod / "__init__.py").write_text("import os\n")
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        assert audit.init_has_docstring is False

    def test_files_count_tracks_python_files(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit

        src_root = tmp_path / "src" / "codomyrmex"
        mod = self._make_module(tmp_path, [])
        (mod / "helpers.py").write_text("pass\n")
        (mod / "utils.py").write_text("pass\n")
        audit = ModuleAudit(mod, src_root)
        audit.audit()
        # __init__.py + helpers.py + utils.py = 3
        assert audit.files_count == 3


@pytest.mark.unit
class TestIsPackage:
    """Test the is_package helper function."""

    def test_directory_with_init_is_package(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import is_package

        pkg = tmp_path / "my_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        assert is_package(pkg) is True

    def test_directory_without_init_is_not_package(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import is_package

        pkg = tmp_path / "my_dir"
        pkg.mkdir()
        assert is_package(pkg) is False

    def test_file_path_is_not_package(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import is_package

        f = tmp_path / "file.txt"
        f.write_text("not a package")
        assert is_package(f) is False


@pytest.mark.unit
class TestAuditRasp:
    """Test the audit_rasp function for RASP compliance checking."""

    def _make_compliant_module(self, base: Path, name: str) -> Path:
        """Create a fully RASP-compliant module."""
        mod = base / name
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text(f'"""Module {name}."""\n')
        for doc in ["README.md", "AGENTS.md", "SPEC.md", "PAI.md"]:
            (mod / doc).write_text(
                f"# {doc.replace('.md', '')} for {name}\n\n"
                f"This is substantive content for the {name} module.\n"
            )
        return mod

    def test_all_compliant_returns_zero(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import audit_rasp

        base = tmp_path / "base"
        self._make_compliant_module(base, "alpha")
        self._make_compliant_module(base, "beta")
        result = audit_rasp(base)
        assert result == 0

    def test_missing_files_returns_one(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import audit_rasp

        base = tmp_path / "base"
        mod = base / "incomplete"
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text('"""Incomplete."""\n')
        (mod / "README.md").write_text("# README\n\nSome content here.\n")
        # Missing: AGENTS.md, SPEC.md, PAI.md
        result = audit_rasp(base)
        assert result == 1

    def test_non_package_dirs_ignored(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import audit_rasp

        base = tmp_path / "base"
        # Directory without __init__.py should be ignored
        plain_dir = base / "not_a_package"
        plain_dir.mkdir(parents=True)
        (plain_dir / "README.md").write_text("# Not a package\n")
        # No __init__.py means no audit
        result = audit_rasp(base)
        assert result == 0

    def test_pycache_dirs_skipped(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import audit_rasp

        base = tmp_path / "base"
        cache = base / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "__init__.py").write_text("")
        result = audit_rasp(base)
        assert result == 0


@pytest.mark.unit
class TestGenerateReport:
    """Test the generate_report function for audit report creation."""

    def test_report_file_created(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit, generate_report

        src_root = tmp_path / "src"
        mod = src_root / "my_mod"
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text('"""My mod."""\n')

        audit = ModuleAudit(mod, src_root)
        audit.audit()

        report_file = tmp_path / "report.md"
        generate_report([audit], report_file)
        assert report_file.exists()

    def test_report_contains_summary_header(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit, generate_report

        src_root = tmp_path / "src"
        mod = src_root / "mod_a"
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text('"""Mod A."""\n')

        audit = ModuleAudit(mod, src_root)
        audit.audit()

        report_file = tmp_path / "report.md"
        generate_report([audit], report_file)
        content = report_file.read_text()
        assert "# Documentation Audit Report" in content
        assert "## Summary" in content

    def test_report_counts_perfect_modules(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import ModuleAudit, generate_report

        src_root = tmp_path / "src"
        mod = src_root / "perfect"
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text('"""Perfect module."""\n')
        (mod / "py.typed").write_text("")
        for doc in ["README.md", "AGENTS.md", "SPEC.md", "PAI.md"]:
            (mod / doc).write_text(
                f"# {doc}\n\nThis is real content for the module documentation "
                f"and is well above fifty characters.\n"
            )

        audit = ModuleAudit(mod, src_root)
        audit.audit()

        report_file = tmp_path / "report.md"
        generate_report([audit], report_file)
        content = report_file.read_text()
        assert "Perfect Compliance" in content
        assert "1 / 1" in content


@pytest.mark.unit
class TestAuditDocumentation:
    """Test the audit_documentation entry point."""

    def test_nonexistent_dir_handled_gracefully(self, tmp_path: Path, capsys):
        from codomyrmex.documentation.quality.audit import audit_documentation

        fake_dir = tmp_path / "does_not_exist"
        report_file = tmp_path / "report.md"
        audit_documentation(fake_dir, report_file)
        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_empty_dir_reports_no_modules(self, tmp_path: Path, capsys):
        from codomyrmex.documentation.quality.audit import audit_documentation

        report_file = tmp_path / "report.md"
        audit_documentation(tmp_path, report_file)
        captured = capsys.readouterr()
        assert "No modules found" in captured.out

    def test_full_audit_creates_report(self, tmp_path: Path):
        from codomyrmex.documentation.quality.audit import audit_documentation

        mod = tmp_path / "my_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Module."""\n')
        (mod / "README.md").write_text(
            "# My Module\n\nThis is the my_mod module with substantive documentation.\n"
        )

        report_file = tmp_path / "report.md"
        audit_documentation(tmp_path, report_file)
        assert report_file.exists()
        content = report_file.read_text()
        assert "Documentation Audit Report" in content
