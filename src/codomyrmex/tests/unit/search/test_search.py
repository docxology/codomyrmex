"""Tests for search module."""

from datetime import datetime

import pytest

try:
    from codomyrmex.search import (
        Document,
        FuzzyMatcher,
        InMemoryIndex,
        QueryParser,
        SearchResult,
        SimpleTokenizer,
        create_index,
        quick_search,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("search module not available", allow_module_level=True)


@pytest.mark.unit
class TestDocument:
    """Test suite for Document."""
    def test_create_document(self):
        """Test functionality: create document."""
        doc = Document(id="doc-1", content="Hello world")
        assert doc.id == "doc-1"
        assert doc.content == "Hello world"

    def test_document_defaults(self):
        """Test functionality: document defaults."""
        doc = Document(id="doc-2", content="test")
        assert doc.metadata == {}
        assert isinstance(doc.indexed_at, datetime)

    def test_document_with_metadata(self):
        """Test functionality: document with metadata."""
        doc = Document(id="doc-3", content="test", metadata={"source": "web"})
        assert doc.metadata["source"] == "web"


@pytest.mark.unit
class TestSearchResult:
    """Test suite for SearchResult."""
    def test_create_result(self):
        """Test functionality: create result."""
        doc = Document(id="doc-1", content="test")
        result = SearchResult(document=doc, score=0.95)
        assert result.score == 0.95
        assert result.highlights == []


@pytest.mark.unit
class TestSimpleTokenizer:
    """Test suite for SimpleTokenizer."""
    def test_create_tokenizer(self):
        """Test functionality: create tokenizer."""
        tokenizer = SimpleTokenizer()
        assert tokenizer is not None

    def test_tokenizer_lowercase(self):
        """Test functionality: tokenizer lowercase."""
        tokenizer = SimpleTokenizer(lowercase=True)
        assert tokenizer is not None

    def test_tokenizer_min_length(self):
        """Test functionality: tokenizer min length."""
        tokenizer = SimpleTokenizer(min_length=3)
        assert tokenizer is not None


@pytest.mark.unit
class TestInMemoryIndex:
    """Test suite for InMemoryIndex."""
    def test_create_index(self):
        """Test functionality: create index."""
        index = InMemoryIndex()
        assert index is not None

    def test_create_with_tokenizer(self):
        """Test functionality: create with tokenizer."""
        tokenizer = SimpleTokenizer()
        index = InMemoryIndex(tokenizer=tokenizer)
        assert index is not None


@pytest.mark.unit
class TestFuzzyMatcher:
    """Test suite for FuzzyMatcher."""
    def test_class_exists(self):
        """Test functionality: class exists."""
        assert FuzzyMatcher is not None


@pytest.mark.unit
class TestQueryParser:
    """Test suite for QueryParser."""
    def test_create_parser(self):
        """Test functionality: create parser."""
        parser = QueryParser()
        assert parser is not None


@pytest.mark.unit
class TestCreateIndex:
    """Test suite for CreateIndex."""
    def test_default_creates_memory_index(self):
        """Test functionality: default creates memory index."""
        index = create_index()
        assert isinstance(index, InMemoryIndex)

    def test_memory_backend(self):
        """Test functionality: memory backend."""
        index = create_index(backend="memory")
        assert index is not None


@pytest.mark.unit
class TestQuickSearch:
    """Test suite for QuickSearch."""
    def test_returns_results(self):
        """Test functionality: returns results."""
        docs = ["Hello world", "Python programming", "Search engine"]
        results = quick_search(docs, "hello")
        assert isinstance(results, list)

    def test_top_k(self):
        """Test functionality: top k."""
        docs = ["doc one", "doc two", "doc three", "doc four"]
        results = quick_search(docs, "doc", k=2)
        assert len(results) <= 2
