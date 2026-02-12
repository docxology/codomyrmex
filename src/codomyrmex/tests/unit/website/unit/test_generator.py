"""
Unit tests for the WebsiteGenerator class — Zero-Mock compliant.

Tests use real Jinja2 templates and a real DataProvider against
temporary project structures. No unittest.mock is used.
"""

import shutil
from pathlib import Path

import pytest

from codomyrmex.website.generator import WebsiteGenerator


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def minimal_project(tmp_path):
    """Create a minimal project tree that DataProvider can scan."""
    src = tmp_path / "src" / "codomyrmex"
    src.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def simple_template_dir(tmp_path):
    """Create a tiny Jinja2 template set for fast test generation."""
    tpl = tmp_path / "tpl"
    tpl.mkdir()
    # base.html — minimal layout
    (tpl / "base.html").write_text(
        "<!DOCTYPE html><html><body>{% block content %}{% endblock %}</body></html>"
    )
    # index.html — inherits base
    (tpl / "index.html").write_text(
        '{% extends "base.html" %}{% block content %}'
        "<h1>{{ system.status }}</h1>"
        "{% endblock %}"
    )
    return tpl


# ── Init Tests ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestWebsiteGeneratorInit:
    """Tests for WebsiteGenerator initialization."""

    def test_init_with_output_dir(self, tmp_path):
        """Test initialization with just output_dir."""
        output_dir = tmp_path / "output"
        gen = WebsiteGenerator(output_dir=str(output_dir))

        assert gen.output_dir == output_dir
        assert gen.data_provider is not None

    def test_init_with_root_dir(self, tmp_path):
        """Test initialization with explicit root_dir."""
        output_dir = tmp_path / "output"
        root = tmp_path / "root"
        root.mkdir()

        gen = WebsiteGenerator(output_dir=str(output_dir), root_dir=str(root))

        assert gen.output_dir == output_dir
        assert gen.root_dir == root

    def test_init_creates_data_provider(self, tmp_path):
        """Test that DataProvider is created during init."""
        gen = WebsiteGenerator(output_dir=str(tmp_path / "output"))
        assert gen.data_provider is not None


# ── Generate Tests ──────────────────────────────────────────────────


@pytest.mark.unit
class TestWebsiteGeneratorGenerate:
    """Tests for the generate() method using real templates."""

    def test_generate_creates_output_directory(self, minimal_project):
        """Test that generate creates the output directory."""
        output_dir = minimal_project / "website_output"
        gen = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(minimal_project),
        )
        gen.generate()

        assert output_dir.exists()
        assert (output_dir / "index.html").exists()

    def test_generate_clears_existing_output(self, minimal_project):
        """Test that generate clears existing output directory."""
        output_dir = minimal_project / "website_output"
        output_dir.mkdir()
        (output_dir / "old_file.txt").write_text("old content")

        gen = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(minimal_project),
        )
        gen.generate()

        assert not (output_dir / "old_file.txt").exists()
        assert (output_dir / "index.html").exists()

    def test_generate_produces_all_pages(self, minimal_project):
        """Test that all 10 pages are generated."""
        output_dir = minimal_project / "website_output"
        gen = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(minimal_project),
        )
        gen.generate()

        expected_pages = [
            "index.html", "health.html", "modules.html", "scripts.html",
            "chat.html", "agents.html", "config.html", "docs.html",
            "pipelines.html", "awareness.html",
        ]
        for page in expected_pages:
            assert (output_dir / page).exists(), f"Missing page: {page}"


# ── _render_page Tests ──────────────────────────────────────────────


@pytest.mark.unit
class TestWebsiteGeneratorRenderPage:
    """Tests for _render_page() with real Jinja2 templates."""

    def test_render_page_creates_html_file(self, tmp_path, simple_template_dir):
        """Test that _render_page creates the correct HTML file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        gen = WebsiteGenerator(output_dir=str(output_dir))
        # Override templates dir to use our simple templates
        gen.templates_dir = simple_template_dir
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        gen.env = Environment(
            loader=FileSystemLoader(simple_template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

        gen._render_page("index.html", {"system": {"status": "Operational"}})

        result = (output_dir / "index.html").read_text()
        assert "<h1>Operational</h1>" in result

    def test_render_page_passes_context_correctly(self, tmp_path, simple_template_dir):
        """Test that context variables appear in rendered output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        gen = WebsiteGenerator(output_dir=str(output_dir))
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        gen.env = Environment(
            loader=FileSystemLoader(simple_template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

        gen._render_page("index.html", {"system": {"status": "Degraded"}})

        result = (output_dir / "index.html").read_text()
        assert "Degraded" in result


# ── _copy_assets Tests ──────────────────────────────────────────────


@pytest.mark.unit
class TestWebsiteGeneratorCopyAssets:
    """Tests for _copy_assets() with real file structures."""

    def test_copy_assets_copies_directory(self, tmp_path):
        """Test that _copy_assets copies the assets directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create real assets directory
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "css").mkdir()
        (assets_dir / "css" / "style.css").write_text("body { color: red; }")
        (assets_dir / "js").mkdir()
        (assets_dir / "js" / "app.js").write_text("console.log('hello');")

        gen = WebsiteGenerator(output_dir=str(output_dir))
        gen.assets_dir = assets_dir

        gen._copy_assets()

        assert (output_dir / "assets" / "css" / "style.css").exists()
        assert (output_dir / "assets" / "js" / "app.js").exists()
        assert (output_dir / "assets" / "css" / "style.css").read_text() == "body { color: red; }"

    def test_copy_assets_handles_missing_assets_dir(self, tmp_path):
        """Test that _copy_assets handles missing assets directory gracefully."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        gen = WebsiteGenerator(output_dir=str(output_dir))
        gen.assets_dir = tmp_path / "nonexistent_assets"

        # Should not raise an exception
        gen._copy_assets()

        assert not (output_dir / "assets").exists()


# ── Integration Tests ───────────────────────────────────────────────


@pytest.mark.unit
class TestWebsiteGeneratorIntegration:
    """Full generation workflow with real templates and DataProvider."""

    def test_full_generation_workflow(self, minimal_project):
        """Test the complete website generation with real project."""
        output_dir = minimal_project / "website_output"

        gen = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(minimal_project),
        )
        gen.generate()

        assert output_dir.exists()
        assert (output_dir / "index.html").exists()
        assert (output_dir / "scripts.html").exists()
        assert (output_dir / "assets").exists()

        # Verify generated HTML has content
        index_html = (output_dir / "index.html").read_text()
        assert len(index_html) > 100
        assert "<html" in index_html.lower()

    def test_regeneration_is_idempotent(self, minimal_project):
        """Test that running generate twice produces same output."""
        output_dir = minimal_project / "website_output"
        gen = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(minimal_project),
        )

        gen.generate()
        first_index = (output_dir / "index.html").read_text()

        gen.generate()
        second_index = (output_dir / "index.html").read_text()

        assert first_index == second_index


# ── Error Handling Tests ────────────────────────────────────────────


@pytest.mark.unit
class TestGeneratorErrorHandling:
    """Tests for template rendering error isolation."""

    def test_broken_template_is_skipped(self, tmp_path, minimal_project):
        """Test that a template with errors is skipped without crashing."""
        output_dir = tmp_path / "output"
        gen = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(minimal_project),
        )

        # Inject a broken template (undefined variable reference)
        broken = gen.templates_dir / "_broken_test.html"
        broken.write_text("{{ undefined_var.method() }}")

        # Monkey-patch the pages list to include the broken template
        import codomyrmex.website.generator as gen_mod
        original_generate = gen.generate

        def patched_generate():
            """Generate with an extra broken page in the list."""
            import shutil as _shutil

            if gen.output_dir.exists():
                _shutil.rmtree(gen.output_dir)
            gen.output_dir.mkdir(parents=True)

            context = {
                "system": gen.data_provider.get_system_summary(),
                "modules": gen.data_provider.get_modules(),
                "agents": gen.data_provider.get_actual_agents(),
                "scripts": gen.data_provider.get_available_scripts(),
                "config_files": gen.data_provider.get_config_files(),
                "doc_tree": gen.data_provider.get_doc_tree(),
                "pipelines": gen.data_provider.get_pipeline_status(),
                "health": gen.data_provider.get_health_status(),
                "awareness": gen.data_provider.get_pai_awareness_data(),
            }

            pages = ["index.html", "_broken_test.html", "health.html"]
            for page in pages:
                try:
                    gen._render_page(page, context)
                except Exception:
                    pass  # graceful skip

            gen._copy_assets()

        patched_generate()

        # Broken template should NOT exist in output
        assert not (output_dir / "_broken_test.html").exists()
        # Other pages should still be rendered
        assert (output_dir / "index.html").exists()
        assert (output_dir / "health.html").exists()

        # Clean up injected template
        broken.unlink()

    def test_missing_template_is_skipped(self, minimal_project):
        """Test that a non-existent template name is skipped gracefully."""
        output_dir = minimal_project / "output_missing"
        gen = WebsiteGenerator(
            output_dir=str(output_dir),
            root_dir=str(minimal_project),
        )

        # _render_page should raise TemplateNotFound for missing template
        from jinja2 import TemplateNotFound
        with pytest.raises(TemplateNotFound):
            gen._render_page("nonexistent_page.html", {"system": {}})

        # But generate() should catch it and continue
        gen.generate()
        # index.html and other real templates should still exist
        assert (output_dir / "index.html").exists()
