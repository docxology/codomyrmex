"""Tests for FPF exporter."""

import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from codomyrmex.fpf import FPFExporter, FPFSpec, Pattern, Relationship, PatternStatus, Concept, ConceptType


@pytest.mark.unit
def test_exporter_initialization():
    """Test exporter initialization."""
    exporter = FPFExporter()
    assert exporter is not None


@pytest.mark.unit
def test_export_json():
    """Test JSON export."""
    exporter = FPFExporter()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                content="Test content",
            )
        ]
    )
    
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.json"
        exporter.export_json(spec, output_path)
        assert output_path.exists()
        
        data = json.loads(output_path.read_text())
        assert "patterns" in data
        assert len(data["patterns"]) == 1


@pytest.mark.unit
def test_export_patterns_json():
    """Test patterns-only export."""
    exporter = FPFExporter()
    patterns = [
        Pattern(
            id="A.1",
            title="Pattern 1",
            status=PatternStatus.STABLE,
            content="",
        ),
        Pattern(
            id="A.2",
            title="Pattern 2",
            status=PatternStatus.DRAFT,
            content="",
        ),
    ]
    
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "patterns.json"
        exporter.export_patterns_json(patterns, output_path)
        assert output_path.exists()
        
        data = json.loads(output_path.read_text())
        assert "patterns" in data
        assert len(data["patterns"]) == 2


@pytest.mark.unit
def test_export_concepts_json():
    """Test concepts-only export."""
    exporter = FPFExporter()
    concepts = [
        Concept(
            name="U.Holon",
            definition="A holon is...",
            pattern_id="A.1",
            type=ConceptType.U_TYPE,
        )
    ]
    
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "concepts.json"
        exporter.export_concepts_json(concepts, output_path)
        assert output_path.exists()
        
        data = json.loads(output_path.read_text())
        assert "concepts" in data
        assert len(data["concepts"]) == 1


@pytest.mark.unit
def test_export_for_context():
    """Test context-optimized export."""
    exporter = FPFExporter()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Test Pattern",
                status=PatternStatus.STABLE,
                keywords=["test"],
                content="Test content",
                part="A",
            )
        ]
    )
    
    context_data = exporter.export_for_context(spec, filters={"part": "A"})
    assert "summary" in context_data
    assert "patterns" in context_data
    assert context_data["summary"]["total_patterns"] == 1


@pytest.mark.unit
def test_export_for_context_with_filters():
    """Test context export with filters."""
    exporter = FPFExporter()
    spec = FPFSpec(
        patterns=[
            Pattern(
                id="A.1",
                title="Stable Pattern",
                status=PatternStatus.STABLE,
                content="",
                part="A",
            ),
            Pattern(
                id="B.1",
                title="Draft Pattern",
                status=PatternStatus.DRAFT,
                content="",
                part="B",
            ),
        ]
    )
    
    context_data = exporter.export_for_context(spec, filters={"status": "Stable"})
    assert len(context_data["patterns"]) == 1
    assert context_data["patterns"][0]["status"] == "Stable"


