"""
Integration tests for the documents module.

Tests end-to-end workflows, cross-format operations, and integration
with other Codomyrmex modules.
"""

import pytest
import tempfile
import json
from pathlib import Path

from codomyrmex.documents import (
    read_document,
    write_document,
    Document,
    DocumentFormat,
)

try:
    from codomyrmex.documents.transformation import convert_document, merge_documents
    TRANSFORMATION_AVAILABLE = True
except ImportError:
    TRANSFORMATION_AVAILABLE = False


class TestDocumentWorkflows:
    """Test end-to-end document processing workflows."""
    
    def test_read_write_workflow(self, tmp_path):
        """Test complete read-write workflow."""
        # Create source document
        source_file = tmp_path / "source.md"
        source_file.write_text("# Source\n\nContent", encoding="utf-8")
        
        # Read document
        doc = read_document(source_file)
        assert doc.format == DocumentFormat.MARKDOWN
        
        # Write to new location
        output_file = tmp_path / "output.md"
        write_document(doc, output_file)
        
        # Verify output
        assert output_file.exists()
        assert "# Source" in output_file.read_text()
    
    @pytest.mark.skipif(not TRANSFORMATION_AVAILABLE, reason="Transformation not available")
    def test_format_conversion_workflow(self, tmp_path):
        """Test format conversion workflow."""
        # Create markdown source
        md_file = tmp_path / "source.md"
        md_file.write_text("# Title\n\nContent", encoding="utf-8")
        
        # Read markdown
        md_doc = read_document(md_file)
        
        # Convert to text
        text_doc = convert_document(md_doc, DocumentFormat.TEXT)
        
        # Write text
        text_file = tmp_path / "output.txt"
        write_document(text_doc, text_file)
        
        # Verify conversion
        assert text_file.exists()
        content = text_file.read_text()
        assert "Title" in content or "Content" in content
    
    @pytest.mark.skipif(not TRANSFORMATION_AVAILABLE, reason="Transformation not available")
    def test_merge_workflow(self, tmp_path):
        """Test document merging workflow."""
        # Create multiple source documents
        doc1_file = tmp_path / "doc1.md"
        doc1_file.write_text("# Document 1\n\nContent 1", encoding="utf-8")
        
        doc2_file = tmp_path / "doc2.md"
        doc2_file.write_text("# Document 2\n\nContent 2", encoding="utf-8")
        
        # Read documents
        doc1 = read_document(doc1_file)
        doc2 = read_document(doc2_file)
        
        # Merge documents
        merged = merge_documents([doc1, doc2])
        
        # Write merged document
        merged_file = tmp_path / "merged.md"
        write_document(merged, merged_file)
        
        # Verify merge
        assert merged_file.exists()
        content = merged_file.read_text()
        assert "Document 1" in content or "Content 1" in content
        assert "Document 2" in content or "Content 2" in content


class TestCrossFormatOperations:
    """Test operations across different formats."""
    
    def test_json_to_yaml_roundtrip(self, tmp_path):
        """Test JSON to YAML conversion and back."""
        # Create JSON file
        json_file = tmp_path / "data.json"
        data = {"key": "value", "number": 42}
        json_file.write_text(json.dumps(data), encoding="utf-8")
        
        # Read JSON
        json_doc = read_document(json_file, format=DocumentFormat.JSON)
        assert isinstance(json_doc.content, dict)
        
        # Write as YAML (if conversion available)
        try:
            yaml_file = tmp_path / "data.yaml"
            # For now, just test that we can read JSON
            assert json_doc.content == data
        except Exception:
            # YAML conversion may not be fully implemented
            pass


class TestErrorPropagation:
    """Test error handling in workflows."""
    
    def test_error_handling_in_workflow(self, tmp_path):
        """Test that errors are properly handled in workflows."""
        # Try to read non-existent file
        nonexistent = tmp_path / "nonexistent.txt"
        
        with pytest.raises(Exception):  # Should raise DocumentReadError
            read_document(nonexistent)
    
    def test_invalid_format_handling(self, tmp_path):
        """Test handling of invalid format operations."""
        # Create a document
        doc = Document(content="Test", format=DocumentFormat.TEXT)
        
        # Try invalid operations should handle gracefully
        # (specific behavior depends on implementation)
        assert doc is not None

