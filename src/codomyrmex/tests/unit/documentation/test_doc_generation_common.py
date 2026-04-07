"""Tests for doc_generation_common (purpose inference and signpost helpers)."""

from pathlib import Path

import pytest

from codomyrmex.documentation.doc_generation_common import (
    EXCLUDED_DOC_PREFIXES,
    describe_inventory_item,
    describe_inventory_item_for_directory,
    extract_init_docstring_first_line,
    extract_skill_md_purpose,
    humanize_slug,
    infer_mission_control_purpose,
    infer_purpose_for_directory,
    nearest_python_package,
    path_matches_excluded_prefix,
)


@pytest.mark.unit
class TestInferPurposeForDirectory:
    def test_surface_src(self, tmp_path: Path) -> None:
        d = tmp_path / "src"
        d.mkdir()
        assert "source code" in infer_purpose_for_directory(d, tmp_path).lower()

    def test_docs_modules_mirror(self, tmp_path: Path) -> None:
        d = tmp_path / "docs" / "modules" / "cache"
        d.mkdir(parents=True)
        p = infer_purpose_for_directory(d, tmp_path)
        assert "cache" in p
        assert "codomyrmex" in p

    def test_codomyrmex_package_and_subdir(self, tmp_path: Path) -> None:
        pkg = tmp_path / "src" / "codomyrmex" / "mytestpkg"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text('"""Hello world pkg."""', encoding="utf-8")
        sub = pkg / "rules"
        sub.mkdir()
        p = infer_purpose_for_directory(sub, tmp_path)
        assert "Hello world pkg." in p
        assert "rules" in p

        p_pkg = infer_purpose_for_directory(pkg, tmp_path)
        assert p_pkg == "Hello world pkg."

    def test_tests_segment(self, tmp_path: Path) -> None:
        d = tmp_path / "src" / "codomyrmex" / "tests" / "unit" / "foo"
        d.mkdir(parents=True)
        assert "test" in infer_purpose_for_directory(d, tmp_path).lower()


@pytest.mark.unit
class TestExtractAndPackageHelpers:
    def test_extract_init_first_line(self, tmp_path: Path) -> None:
        d = tmp_path / "p"
        d.mkdir()
        (d / "__init__.py").write_text(
            '"""First line.\n\nMore text."""', encoding="utf-8"
        )
        assert extract_init_docstring_first_line(d) == "First line."

    def test_nearest_python_package(self, tmp_path: Path) -> None:
        stop = tmp_path / "root" / "codomyrmex"
        pkg = stop / "pkg"
        sub = pkg / "nested"
        sub.mkdir(parents=True)
        (pkg / "__init__.py").touch()
        assert nearest_python_package(sub, stop) == pkg.resolve()
        assert nearest_python_package(pkg, stop) == pkg.resolve()


@pytest.mark.unit
class TestExcludedPrefixesAndInventory:
    def test_path_matches_excluded_prefix(self) -> None:
        assert path_matches_excluded_prefix(
            Path("src/codomyrmex/agents/open_gauss/skills/foo"),
            EXCLUDED_DOC_PREFIXES,
        )
        assert not path_matches_excluded_prefix(
            Path("src/codomyrmex/validation"),
            EXCLUDED_DOC_PREFIXES,
        )

    def test_describe_inventory_item(self) -> None:
        assert "Python" in describe_inventory_item("x.py")
        assert "Directory" in describe_inventory_item("pkg/")


@pytest.mark.unit
class TestSkillAndMissionControlHelpers:
    def test_humanize_slug(self) -> None:
        assert "Llm" in humanize_slug("llm-architect") or "Llm" in humanize_slug(
            "llm_architect"
        )

    def test_extract_skill_md_purpose(self, tmp_path: Path) -> None:
        skill = tmp_path / "SKILL.md"
        skill.write_text(
            "---\nname: X\ndescription: >\n  One line summary here\n---\n\n# X\n",
            encoding="utf-8",
        )
        assert "One line summary here" in extract_skill_md_purpose(tmp_path)

    def test_infer_mission_control_route_handler(self, tmp_path: Path) -> None:
        base = (
            tmp_path
            / "src"
            / "codomyrmex"
            / "agents"
            / "mission_control"
            / "app"
            / "api"
            / "ping"
        )
        base.mkdir(parents=True)
        (base / "route.ts").write_text("export async function GET() {}", encoding="utf-8")
        rel = base.relative_to(tmp_path)
        p = infer_mission_control_purpose(base, rel)
        assert "Mission Control" in p
        assert "route" in p.lower() or "handler" in p.lower()

    def test_describe_inventory_mission_control(self, tmp_path: Path) -> None:
        app = (
            tmp_path
            / "src"
            / "codomyrmex"
            / "agents"
            / "mission_control"
            / "app"
        )
        app.mkdir(parents=True)
        d = describe_inventory_item_for_directory(app, tmp_path, "route.ts")
        assert "Route Handler" in d or "route" in d.lower()

    def test_infer_purpose_upstream_skill_folder(self, tmp_path: Path) -> None:
        d = (
            tmp_path
            / "src"
            / "codomyrmex"
            / "skills"
            / "skills"
            / "upstream"
            / "ai"
            / "custom_leaf"
        )
        d.mkdir(parents=True)
        out = infer_purpose_for_directory(d, tmp_path)
        assert "Upstream skill mirror" in out
        assert "custom_leaf" in out

    def test_fallback_subtree_wording(self, tmp_path: Path) -> None:
        d = tmp_path / "src" / "orphan" / "nested"
        d.mkdir(parents=True)
        out = infer_purpose_for_directory(d, tmp_path)
        assert "Repository subtree" in out
        assert "src" in out
