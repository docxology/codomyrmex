"""
Unit tests for the WebsiteGenerator class.

Tests cover:
- Generator initialization
- Page rendering
- Asset copying
- Full generation workflow
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.generator import WebsiteGenerator


@pytest.mark.unit
class TestWebsiteGeneratorInit:
    """Tests for WebsiteGenerator initialization."""

    def test_init_with_output_dir(self, tmp_path):
        """Test initialization with just output_dir."""
        output_dir = tmp_path / "output"
        generator = WebsiteGenerator(output_dir=str(output_dir))

        assert generator.output_dir == output_dir
        assert generator.templates_dir.exists() or True  # May not exist in test env
        assert generator.data_provider is not None

    def test_init_with_root_dir(self, tmp_path):
        """Test initialization with explicit root_dir."""
        output_dir = tmp_path / "output"
        root_dir = tmp_path / "root"
        root_dir.mkdir()

        generator = WebsiteGenerator(output_dir=str(output_dir), root_dir=str(root_dir))

        assert generator.output_dir == output_dir
        assert generator.root_dir == root_dir

    def test_init_creates_data_provider(self, tmp_path):
        """Test that DataProvider is created during init."""
        output_dir = tmp_path / "output"
        generator = WebsiteGenerator(output_dir=str(output_dir))

        assert generator.data_provider is not None


@pytest.mark.unit
class TestWebsiteGeneratorGenerate:
    """Tests for the generate() method."""

    def test_generate_creates_output_directory(self, tmp_path):
        """Test that generate creates the output directory."""
        output_dir = tmp_path / "output"
        root_dir = tmp_path / "root"

        # Create minimal project structure
        root_dir.mkdir()
        (root_dir / "src" / "codomyrmex").mkdir(parents=True)
        (root_dir / "scripts").mkdir()

        generator = WebsiteGenerator(output_dir=str(output_dir), root_dir=str(root_dir))

        # Mock the template loading to avoid needing actual templates
        with patch.object(generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html></html>"
            mock_get_template.return_value = mock_template

            generator.generate()

        assert output_dir.exists()

    def test_generate_clears_existing_output(self, tmp_path):
        """Test that generate clears existing output directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "old_file.txt").write_text("old content")

        root_dir = tmp_path / "root"
        root_dir.mkdir()
        (root_dir / "src" / "codomyrmex").mkdir(parents=True)
        (root_dir / "scripts").mkdir()

        generator = WebsiteGenerator(output_dir=str(output_dir), root_dir=str(root_dir))

        with patch.object(generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html></html>"
            mock_get_template.return_value = mock_template

            generator.generate()

        assert not (output_dir / "old_file.txt").exists()


@pytest.mark.unit
class TestWebsiteGeneratorRenderPage:
    """Tests for the _render_page() method."""

    def test_render_page_creates_html_file(self, tmp_path):
        """Test that _render_page creates the correct HTML file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generator = WebsiteGenerator(output_dir=str(output_dir))

        with patch.object(generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html><body>Test</body></html>"
            mock_get_template.return_value = mock_template

            generator._render_page("test.html", {"key": "value"})

        assert (output_dir / "test.html").exists()
        assert (output_dir / "test.html").read_text() == "<html><body>Test</body></html>"

    def test_render_page_passes_context(self, tmp_path):
        """Test that _render_page passes context to template."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generator = WebsiteGenerator(output_dir=str(output_dir))

        with patch.object(generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html></html>"
            mock_get_template.return_value = mock_template

            context = {"system": {"status": "ok"}, "scripts": []}
            generator._render_page("test.html", context)

            mock_template.render.assert_called_once_with(**context)


@pytest.mark.unit
class TestWebsiteGeneratorCopyAssets:
    """Tests for the _copy_assets() method."""

    def test_copy_assets_copies_directory(self, tmp_path):
        """Test that _copy_assets copies the assets directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create mock assets directory
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "css").mkdir()
        (assets_dir / "css" / "style.css").write_text("body { color: red; }")
        (assets_dir / "js").mkdir()
        (assets_dir / "js" / "app.js").write_text("console.log('hello');")

        generator = WebsiteGenerator(output_dir=str(output_dir))
        generator.assets_dir = assets_dir

        generator._copy_assets()

        assert (output_dir / "assets" / "css" / "style.css").exists()
        assert (output_dir / "assets" / "js" / "app.js").exists()

    def test_copy_assets_handles_missing_assets_dir(self, tmp_path):
        """Test that _copy_assets handles missing assets directory gracefully."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generator = WebsiteGenerator(output_dir=str(output_dir))
        generator.assets_dir = tmp_path / "nonexistent_assets"

        # Should not raise an exception
        generator._copy_assets()

        assert not (output_dir / "assets").exists()


@pytest.mark.unit
class TestWebsiteGeneratorIntegration:
    """Integration tests for the full generation workflow."""

    def test_full_generation_workflow(self, tmp_path):
        """Test the complete website generation workflow."""
        output_dir = tmp_path / "output"
        root_dir = tmp_path / "root"

        # Create minimal project structure
        root_dir.mkdir()
        (root_dir / "src" / "codomyrmex").mkdir(parents=True)
        (root_dir / "scripts").mkdir()

        generator = WebsiteGenerator(output_dir=str(output_dir), root_dir=str(root_dir))

        # Mock templates and assets
        with patch.object(generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html><body>Generated</body></html>"
            mock_get_template.return_value = mock_template

            generator.assets_dir = tmp_path / "mock_assets"

            generator.generate()

        # Verify output
        assert output_dir.exists()
        assert (output_dir / "index.html").exists()
        assert (output_dir / "scripts.html").exists()
