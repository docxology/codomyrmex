"""Unit tests for markdown parsing, link validation, and document structure checks.

Tests cover: find_markdown_files, extract_links, resolve_link, check_links
from check_doc_links.py, and check_structure/is_python_module from audit_structure.py.

Zero-mock policy: All tests use real filesystem via tmp_path fixtures.
"""

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# find_markdown_files
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFindMarkdownFiles:
    """Test markdown file discovery in documentation directories."""

    def test_finds_md_files_in_flat_directory(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import find_markdown_files

        (tmp_path / "guide.md").write_text("# Guide\n")
        (tmp_path / "notes.md").write_text("# Notes\n")
        (tmp_path / "data.json").write_text("{}")

        files = find_markdown_files(tmp_path)
        names = [f.name for f in files]
        assert "guide.md" in names
        assert "notes.md" in names
        assert "data.json" not in names

    def test_finds_md_files_recursively(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import find_markdown_files

        sub = tmp_path / "sub" / "deep"
        sub.mkdir(parents=True)
        (sub / "nested.md").write_text("# Nested\n")
        (tmp_path / "root.md").write_text("# Root\n")

        files = find_markdown_files(tmp_path)
        names = [f.name for f in files]
        assert "root.md" in names
        assert "nested.md" in names

    def test_skips_hidden_directories(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import find_markdown_files

        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "secret.md").write_text("# Secret\n")
        (tmp_path / "visible.md").write_text("# Visible\n")

        files = find_markdown_files(tmp_path)
        names = [f.name for f in files]
        assert "visible.md" in names
        assert "secret.md" not in names

    def test_empty_directory_returns_empty_list(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import find_markdown_files

        files = find_markdown_files(tmp_path)
        assert files == []

    def test_returns_sorted_paths(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import find_markdown_files

        (tmp_path / "zebra.md").write_text("# Z\n")
        (tmp_path / "alpha.md").write_text("# A\n")
        (tmp_path / "middle.md").write_text("# M\n")

        files = find_markdown_files(tmp_path)
        names = [f.name for f in files]
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# extract_links
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractLinks:
    """Test markdown link extraction from content."""

    def test_extracts_standard_link(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import extract_links

        content = "See [the guide](guide.md) for details.\n"
        dummy_path = tmp_path / "test.md"
        links = extract_links(content, dummy_path)
        assert len(links) == 1
        assert links[0][0] == "the guide"  # link text
        assert links[0][2] == "guide.md"  # link url

    def test_extracts_multiple_links(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import extract_links

        content = "[A](a.md) and [B](b.md)\n"
        links = extract_links(content, tmp_path / "test.md")
        assert len(links) == 2

    def test_captures_line_numbers(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import extract_links

        content = "Line 1\n[Link](target.md)\nLine 3\n"
        links = extract_links(content, tmp_path / "test.md")
        assert len(links) == 1
        assert links[0][1] == 2  # line number

    def test_extracts_external_links(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import extract_links

        content = "[GitHub](https://github.com)\n"
        links = extract_links(content, tmp_path / "test.md")
        assert len(links) == 1
        assert links[0][2] == "https://github.com"

    def test_no_links_returns_empty(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import extract_links

        content = "Plain text with no links.\n"
        links = extract_links(content, tmp_path / "test.md")
        assert links == []

    def test_extracts_relative_parent_links(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import extract_links

        content = "[Parent](../README.md)\n"
        links = extract_links(content, tmp_path / "test.md")
        assert len(links) == 1
        assert links[0][2] == "../README.md"


# ---------------------------------------------------------------------------
# resolve_link
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestResolveLink:
    """Test link resolution and existence checking."""

    def test_external_link_always_valid(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import resolve_link

        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        from_file = docs_root / "test.md"
        from_file.write_text("# Test\n")

        exists, resolved = resolve_link("https://example.com", from_file, docs_root)
        assert exists is True
        assert resolved == "external"

    def test_anchor_link_always_valid(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import resolve_link

        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        from_file = docs_root / "test.md"
        from_file.write_text("# Test\n")

        exists, resolved = resolve_link("#section-1", from_file, docs_root)
        assert exists is True
        assert resolved == "anchor"

    def test_existing_relative_link_resolves(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import resolve_link

        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        from_file = docs_root / "index.md"
        from_file.write_text("# Index\n")
        target = docs_root / "guide.md"
        target.write_text("# Guide\n")

        exists, _ = resolve_link("guide.md", from_file, docs_root)
        assert exists is True

    def test_broken_relative_link_detected(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import resolve_link

        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        from_file = docs_root / "index.md"
        from_file.write_text("# Index\n")

        exists, _ = resolve_link("nonexistent.md", from_file, docs_root)
        assert exists is False

    def test_mailto_link_treated_as_external(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import resolve_link

        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        from_file = docs_root / "test.md"
        from_file.write_text("# Test\n")

        exists, resolved = resolve_link("mailto:user@example.com", from_file, docs_root)
        assert exists is True
        assert resolved == "external"

    def test_link_with_anchor_stripped(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import resolve_link

        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        from_file = docs_root / "index.md"
        from_file.write_text("# Index\n")
        target = docs_root / "guide.md"
        target.write_text("# Guide\n")

        exists, _ = resolve_link("guide.md#section", from_file, docs_root)
        assert exists is True


# ---------------------------------------------------------------------------
# check_links (integration of the above)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCheckLinks:
    """Test the check_links function that validates all links in a docs tree."""

    def test_clean_docs_returns_no_issues(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import check_links

        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("# Index\n\nSee [guide](guide.md).\n")
        (docs / "guide.md").write_text("# Guide\n")

        issues = check_links(docs)
        assert len(issues) == 0

    def test_broken_link_reported(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import check_links

        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("# Index\n\nSee [missing](missing.md).\n")

        issues = check_links(docs)
        assert len(issues) >= 1
        file_issues = list(issues.values())[0]
        assert any(i["issue"] == "broken_link" for i in file_issues)

    def test_external_links_not_flagged(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import check_links

        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("[GitHub](https://github.com)\n")

        issues = check_links(docs)
        assert len(issues) == 0

    def test_empty_docs_dir_no_issues(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.check_doc_links import check_links

        docs = tmp_path / "docs"
        docs.mkdir()
        issues = check_links(docs)
        assert issues == {}


# ---------------------------------------------------------------------------
# audit_structure checks (is_python_module, check_structure)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAuditStructure:
    """Test documentation structure auditing."""

    def test_is_python_module_with_init(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import is_python_module

        mod = tmp_path / "my_pkg"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        assert is_python_module(mod) is True

    def test_is_python_module_without_init(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import is_python_module

        mod = tmp_path / "plain_dir"
        mod.mkdir()
        assert is_python_module(mod) is False

    def test_check_structure_finds_missing_trinity(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import check_structure

        mod = tmp_path / "my_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        # Missing: README.md, SPEC.md, AGENTS.md

        modules, errors = check_structure(tmp_path)
        assert len(modules) >= 1
        assert any("MISSING FILES" in e for e in errors)

    def test_check_structure_clean_module(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import check_structure

        mod = tmp_path / "good_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        (mod / "README.md").write_text("# Good\n")
        (mod / "SPEC.md").write_text("# Spec\n")
        agents_content = (
            "# Agents\n\n"
            "- **Parent**: [../AGENTS.md](../AGENTS.md)\n"
            "- **Self**: [AGENTS.md](AGENTS.md)\n"
            "See [Functional Spec](SPEC.md).\n"
        )
        (mod / "AGENTS.md").write_text(agents_content)

        modules, errors = check_structure(tmp_path)
        assert len(modules) >= 1
        # No missing file errors for good_mod
        mod_errors = [e for e in errors if "good_mod" in e and "MISSING" in e]
        assert len(mod_errors) == 0

    def test_check_structure_detects_bad_signposting(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import check_structure

        mod = tmp_path / "bad_agents"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        (mod / "README.md").write_text("# Bad\n")
        (mod / "SPEC.md").write_text("# Spec\n")
        # AGENTS.md without Parent/Self links
        (mod / "AGENTS.md").write_text("# Agents\n\nNo links here.\n")

        modules, errors = check_structure(tmp_path)
        signpost_errors = [e for e in errors if "BAD SIGNPOSTING" in e]
        assert len(signpost_errors) >= 1

    def test_check_structure_skips_pycache(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import check_structure

        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "__init__.py").write_text("")

        modules, errors = check_structure(tmp_path)
        cache_modules = [m for m in modules if "__pycache__" in str(m)]
        assert len(cache_modules) == 0

    def test_check_structure_skips_hidden_dirs(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import check_structure

        hidden = tmp_path / ".hidden_pkg"
        hidden.mkdir()
        (hidden / "__init__.py").write_text("")

        modules, errors = check_structure(tmp_path)
        hidden_modules = [m for m in modules if ".hidden" in str(m)]
        assert len(hidden_modules) == 0

    def test_is_python_module_accepts_string_path(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.audit_structure import is_python_module

        mod = tmp_path / "str_pkg"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        assert is_python_module(str(mod)) is True
