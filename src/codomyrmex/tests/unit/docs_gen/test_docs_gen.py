"""Tests for Sprint 38: Documentation Site Generator.

Covers APIDocExtractor, SearchIndex, and SiteGenerator.
"""

import pytest

from codomyrmex.docs_gen.api_doc_extractor import APIDocExtractor
from codomyrmex.docs_gen.search_index import SearchIndex
from codomyrmex.docs_gen.site_generator import SiteGenerator


SAMPLE_SOURCE = '''
"""Sample module docstring."""

__all__ = ["Greeter"]

class Greeter:
    """A greeting class."""

    def hello(self, name: str) -> str:
        """Say hello to someone."""
        return f"Hello, {name}"

def standalone(x: int) -> int:
    """A standalone function."""
    return x + 1
'''


# ─── APIDocExtractor ──────────────────────────────────────────────────

class TestAPIDocExtractor:
    """Test suite for APIDocExtractor."""

    def test_extract_module_docstring(self):
        """Test functionality: extract module docstring."""
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SAMPLE_SOURCE, "sample")
        assert doc.docstring == "Sample module docstring."

    def test_extract_class(self):
        """Test functionality: extract class."""
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SAMPLE_SOURCE, "sample")
        assert len(doc.classes) == 1
        assert doc.classes[0].name == "Greeter"

    def test_extract_methods(self):
        """Test functionality: extract methods."""
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SAMPLE_SOURCE, "sample")
        methods = doc.classes[0].methods
        assert any(m.name == "hello" for m in methods)

    def test_extract_function(self):
        """Test functionality: extract function."""
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SAMPLE_SOURCE, "sample")
        assert len(doc.functions) >= 1
        assert doc.functions[0].name == "standalone"

    def test_extract_exports(self):
        """Test functionality: extract exports."""
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SAMPLE_SOURCE, "sample")
        assert "Greeter" in doc.exports

    def test_to_markdown(self):
        """Test functionality: to markdown."""
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SAMPLE_SOURCE, "sample")
        md = ext.to_markdown(doc)
        assert "# `sample`" in md
        assert "Greeter" in md


# ─── SearchIndex ──────────────────────────────────────────────────────

class TestSearchIndex:
    """Test suite for SearchIndex."""

    def test_add_and_search(self):
        """Test functionality: add and search."""
        idx = SearchIndex()
        idx.add("doc1", title="Agent API", content="The agent processes tasks")
        results = idx.search("agent")
        assert len(results) >= 1
        assert results[0].doc_id == "doc1"

    def test_title_boosted(self):
        """Test functionality: title boosted."""
        idx = SearchIndex()
        idx.add("a", title="Agent Guide", content="some content")
        idx.add("b", title="Other", content="agent mentioned here")
        results = idx.search("agent")
        assert results[0].doc_id == "a"  # Title match ranked higher

    def test_no_results(self):
        """Test functionality: no results."""
        idx = SearchIndex()
        idx.add("a", title="test", content="test content")
        assert len(idx.search("nonexistent")) == 0

    def test_remove(self):
        """Test functionality: remove."""
        idx = SearchIndex()
        idx.add("a", title="doc", content="hello world")
        idx.remove("a")
        assert idx.doc_count == 0


# ─── SiteGenerator ──────────────────────────────────────────────────

class TestSiteGenerator:
    """Test suite for SiteGenerator."""

    def test_add_module(self):
        """Test functionality: add module."""
        gen = SiteGenerator()
        doc = gen.add_module_source(SAMPLE_SOURCE, "sample")
        assert gen.module_count == 1
        assert "sample" in doc.name

    def test_generate_pages(self):
        """Test functionality: generate pages."""
        gen = SiteGenerator()
        gen.add_module_source(SAMPLE_SOURCE, "sample")
        pages = gen.generate_pages()
        assert "api/sample.md" in pages

    def test_mkdocs_yaml(self):
        """Test functionality: mkdocs yaml."""
        gen = SiteGenerator(title="Test Docs")
        gen.add_module_source(SAMPLE_SOURCE, "sample")
        yaml = gen.to_mkdocs_yaml()
        assert "site_name: Test Docs" in yaml
        assert "sample" in yaml

    def test_search_integrated(self):
        """Test functionality: search integrated."""
        gen = SiteGenerator()
        gen.add_module_source(SAMPLE_SOURCE, "sample")
        results = gen.search_index.search("greeter")
        assert len(results) >= 1
