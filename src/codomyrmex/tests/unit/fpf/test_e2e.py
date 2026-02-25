"""End-to-end tests for FPF CLI commands and workflows."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from codomyrmex.fpf import FPFClient


@pytest.mark.integration
def test_e2e_search_workflow():
    """Test end-to-end workflow: search."""
    spec_path = Path(__file__).resolve().parents[3] / "fpf" / "FPF-Spec.md"
    if not spec_path.exists():
        pytest.skip("FPF-Spec.md not found")

    client = FPFClient()
    client.load_from_file(str(spec_path))

    results = client.search("holon")
    assert isinstance(results, list)

    # Test with filters
    results = client.search("pattern", filters={"status": "Stable"})
    assert isinstance(results, list)


@pytest.mark.integration
def test_e2e_export_workflow():
    """Test end-to-end workflow: export."""
    spec_path = Path(__file__).resolve().parents[3] / "fpf" / "FPF-Spec.md"
    if not spec_path.exists():
        pytest.skip("FPF-Spec.md not found")

    client = FPFClient()
    client.load_from_file(str(spec_path))

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "export.json"
        client.export_json(str(output_path))

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert "patterns" in data


@pytest.mark.integration
def test_e2e_context_building_workflow():
    """Test end-to-end workflow: context building."""
    spec_path = Path(__file__).resolve().parents[3] / "fpf" / "FPF-Spec.md"
    if not spec_path.exists():
        pytest.skip("FPF-Spec.md not found")

    client = FPFClient()
    client.load_from_file(str(spec_path))

    # Build context for a pattern
    if client.spec.patterns:
        pattern_id = client.spec.patterns[0].id
        context = client.build_context(pattern_id=pattern_id)
        assert isinstance(context, str)
        assert pattern_id in context

    # Build minimal context
    context = client.build_context(filters={"part": "A"})
    assert isinstance(context, str)

    # Build full context
    context = client.build_context()
    assert isinstance(context, str)


@pytest.mark.integration
def test_e2e_full_pipeline():
    """Test complete end-to-end pipeline."""
    spec_path = Path(__file__).resolve().parents[3] / "fpf" / "FPF-Spec.md"
    if not spec_path.exists():
        pytest.skip("FPF-Spec.md not found")

    # Load
    client = FPFClient()
    client.load_from_file(str(spec_path))

    # Search
    results = client.search("system")
    assert len(results) >= 0

    # Get pattern
    if results:
        pattern = client.get_pattern(results[0].id)
        assert pattern is not None

    # Export
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "pipeline_export.json"
        client.export_json(str(output_path))
        assert output_path.exists()

    # Build context
    context = client.build_context()
    assert isinstance(context, str)



