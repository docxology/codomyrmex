"""Integration tests for FPF module using real FPF-Spec.md."""

import pytest
from pathlib import Path

from codomyrmex.fpf import FPFClient, FPFParser, FPFExtractor, FPFIndexer


@pytest.fixture
def fpf_spec_path():
    """Get path to FPF-Spec.md file."""
    spec_path = Path(__file__).parent.parent / "FPF-Spec.md"
    if not spec_path.exists():
        pytest.skip("FPF-Spec.md not found")
    return spec_path


def test_integration_parse_real_spec(fpf_spec_path):
    """Test parsing real FPF-Spec.md file."""
    parser = FPFParser()
    content = fpf_spec_path.read_text(encoding="utf-8")
    spec = parser.parse_spec(content, source_path=str(fpf_spec_path))
    
    assert spec is not None
    assert len(spec.patterns) > 0
    # Should have patterns from multiple parts
    parts = {p.part for p in spec.patterns if p.part}
    assert len(parts) > 0


def test_integration_extract_concepts(fpf_spec_path):
    """Test concept extraction from real spec."""
    parser = FPFParser()
    extractor = FPFExtractor()
    
    content = fpf_spec_path.read_text(encoding="utf-8")
    spec = parser.parse_spec(content)
    concepts = extractor.extract_concepts(spec)
    
    assert len(concepts) > 0
    # Should have U.Types
    u_types = [c for c in concepts if c.type == "U.Type"]
    assert len(u_types) > 0


def test_integration_extract_relationships(fpf_spec_path):
    """Test relationship extraction from real spec."""
    parser = FPFParser()
    extractor = FPFExtractor()
    
    content = fpf_spec_path.read_text(encoding="utf-8")
    spec = parser.parse_spec(content)
    relationships = extractor.extract_relationships(spec)
    
    assert len(relationships) > 0
    # Should have various relationship types
    rel_types = {r.type for r in relationships}
    assert len(rel_types) > 0


def test_integration_build_index(fpf_spec_path):
    """Test index building from real spec."""
    parser = FPFParser()
    extractor = FPFExtractor()
    indexer = FPFIndexer()
    
    content = fpf_spec_path.read_text(encoding="utf-8")
    spec = parser.parse_spec(content)
    spec.concepts = extractor.extract_concepts(spec)
    spec.relationships = extractor.extract_relationships(spec)
    
    index = indexer.build_index(spec)
    
    assert index is not None
    assert len(index.pattern_index) > 0


def test_integration_search_patterns(fpf_spec_path):
    """Test pattern search on real spec."""
    client = FPFClient()
    client.load_from_file(str(fpf_spec_path))
    
    # Search for common terms
    results = client.search("holon")
    assert len(results) > 0
    
    results = client.search("pattern")
    assert len(results) > 0


def test_integration_get_pattern(fpf_spec_path):
    """Test getting specific pattern from real spec."""
    client = FPFClient()
    client.load_from_file(str(fpf_spec_path))
    
    # Try to get a known pattern (A.1 should exist)
    try:
        pattern = client.get_pattern("A.1")
        assert pattern is not None
        assert pattern.id == "A.1"
    except ValueError:
        # Pattern might not exist, try another
        patterns = client.spec.patterns
        if patterns:
            pattern = client.get_pattern(patterns[0].id)
            assert pattern is not None


def test_integration_export_json(fpf_spec_path):
    """Test JSON export of real spec."""
    import json
    from tempfile import TemporaryDirectory
    
    client = FPFClient()
    client.load_from_file(str(fpf_spec_path))
    
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "export.json"
        client.export_json(str(output_path))
        
        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert "patterns" in data
        assert len(data["patterns"]) > 0


def test_integration_full_pipeline(fpf_spec_path):
    """Test full pipeline: parse → extract → index → search."""
    parser = FPFParser()
    extractor = FPFExtractor()
    indexer = FPFIndexer()
    
    content = fpf_spec_path.read_text(encoding="utf-8")
    spec = parser.parse_spec(content)
    spec.concepts = extractor.extract_concepts(spec)
    spec.relationships = extractor.extract_relationships(spec)
    index = indexer.build_index(spec)
    
    # Search should work
    results = index.search_patterns("system")
    assert isinstance(results, list)
    
    # Get pattern should work
    if spec.patterns:
        pattern = index.get_pattern(spec.patterns[0].id)
        assert pattern is not None


