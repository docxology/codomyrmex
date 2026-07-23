import sys
from pathlib import Path

import pytest

# The module under test
from src.manuscript_variables import inject_via_infrastructure


def test_inject_via_infrastructure_not_implemented(monkeypatch):
    """Test that inject_via_infrastructure raises NotImplementedError when infrastructure is not available."""
    manuscript_dir = Path("/tmp/manuscript")
    output_dir = Path("/tmp/output")
    variables = {"KEY": "VALUE"}

    # Ensure infrastructure is not available in sys.modules, forcing ImportError
    monkeypatch.setitem(sys.modules, "infrastructure", None)
    monkeypatch.setitem(sys.modules, "infrastructure.rendering", None)

    with pytest.raises(
        NotImplementedError, match="infrastructure rendering not available"
    ):
        inject_via_infrastructure(manuscript_dir, output_dir, variables)


class DummyPdfRenderer:
    def __init__(self):
        self.called_with = None

    def inject_manuscript_variables(self, manuscript_dir, output_dir, variables):
        self.called_with = {
            "manuscript_dir": manuscript_dir,
            "output_dir": output_dir,
            "variables": variables,
        }


class DummyRendering:
    def __init__(self):
        self.pdf_combined_renderer = DummyPdfRenderer()


class DummyInfrastructure:
    def __init__(self):
        self.rendering = DummyRendering()


def test_inject_via_infrastructure_success(monkeypatch):
    """Test that inject_via_infrastructure correctly delegates to infrastructure when available."""
    manuscript_dir = Path("/tmp/manuscript")
    output_dir = Path("/tmp/output")
    variables = {"KEY": "VALUE"}

    # Setup dummy infrastructure module without using unittest.mock
    dummy_infrastructure = DummyInfrastructure()
    dummy_rendering = dummy_infrastructure.rendering
    dummy_pdf_renderer = dummy_rendering.pdf_combined_renderer

    monkeypatch.setitem(sys.modules, "infrastructure", dummy_infrastructure)
    monkeypatch.setitem(sys.modules, "infrastructure.rendering", dummy_rendering)

    # Call the function
    inject_via_infrastructure(manuscript_dir, output_dir, variables)

    # Verify it was called correctly by inspecting the dummy object
    assert dummy_pdf_renderer.called_with == {
        "manuscript_dir": manuscript_dir,
        "output_dir": output_dir,
        "variables": variables,
    }
