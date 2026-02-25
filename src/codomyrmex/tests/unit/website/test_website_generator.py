"""
Smoke test for WebsiteGenerator — Zero-Mock compliant.

Uses real project structures and real Jinja2 templates via the
default module template directory. No unittest.mock is used.
"""


import pytest

from codomyrmex.website.generator import WebsiteGenerator


@pytest.mark.unit
def test_generator_initialization(tmp_path):
    """Test that WebsiteGenerator initialises with correct paths."""
    gen = WebsiteGenerator(output_dir=str(tmp_path / "out"), root_dir=str(tmp_path))
    assert gen.output_dir == tmp_path / "out"
    assert gen.root_dir == tmp_path


@pytest.mark.unit
def test_generate_flow(tmp_path):
    """Test full generation produces HTML and assets from real templates."""
    output_dir = tmp_path / "output"

    gen = WebsiteGenerator(output_dir=str(output_dir))
    gen.generate()

    # Verify outputs exist
    assert (output_dir / "index.html").exists()
    assert (output_dir / "assets").exists()

    content = (output_dir / "index.html").read_text()
    assert "Codomyrmex" in content


@pytest.mark.unit
def test_all_pages_generated(tmp_path):
    """Test that all 14 expected pages are generated."""
    output_dir = tmp_path / "output"
    gen = WebsiteGenerator(output_dir=str(output_dir))
    gen.generate()

    expected = [
        "index.html", "health.html", "modules.html", "tools.html",
        "scripts.html", "chat.html", "agents.html", "config.html",
        "docs.html", "pipelines.html", "awareness.html",
        "pai_control.html", "dispatch.html", "telemetry.html",
    ]
    for page in expected:
        assert (output_dir / page).exists(), f"Missing page: {page}"
