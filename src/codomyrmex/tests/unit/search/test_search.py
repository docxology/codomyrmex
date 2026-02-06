"""Tests for search module."""

from datetime import datetime

import pytest

try:
    from codomyrmex.search import (
        Document,
        FuzzyMatcher,
        InMemoryIndex,
        QueryParser,
        SearchIndex,
        SearchResult,
        SimpleTokenizer,
        Tokenizer,
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
    def test_create_document(self):
        doc = Document(id="doc-1", content="Hello world")
        assert doc.id == "doc-1"
        assert doc.content == "Hello world"

    def test_document_defaults(self):
        doc = Document(id="doc-2", content="test")
        assert doc.metadata == {}
        assert isinstance(doc.indexed_at, datetime)

    def test_document_with_metadata(self):
        doc = Document(id="doc-3", content="test", metadata={"source": "web"})
        assert doc.metadata["source"] == "web"


@pytest.mark.unit
class TestSearchResult:
    def test_create_result(self):
        doc = Document(id="doc-1", content="test")
        result = SearchResult(document=doc, score=0.95)
        assert result.score == 0.95
        assert result.highlights == []


@pytest.mark.unit
class TestSimpleTokenizer:
    def test_create_tokenizer(self):
        tokenizer = SimpleTokenizer()
        assert tokenizer is not None

    def test_tokenizer_lowercase(self):
        tokenizer = SimpleTokenizer(lowercase=True)
        assert tokenizer is not None

    def test_tokenizer_min_length(self):
        tokenizer = SimpleTokenizer(min_length=3)
        assert tokenizer is not None


@pytest.mark.unit
class TestInMemoryIndex:
    def test_create_index(self):
        index = InMemoryIndex()
        assert index is not None

    def test_create_with_tokenizer(self):
        tokenizer = SimpleTokenizer()
        index = InMemoryIndex(tokenizer=tokenizer)
        assert index is not None


@pytest.mark.unit
class TestFuzzyMatcher:
    def test_class_exists(self):
        assert FuzzyMatcher is not None


@pytest.mark.unit
class TestQueryParser:
    def test_create_parser(self):
        parser = QueryParser()
        assert parser is not None


@pytest.mark.unit
class TestCreateIndex:
    def test_default_creates_memory_index(self):
        index = create_index()
        assert isinstance(index, InMemoryIndex)

    def test_memory_backend(self):
        index = create_index(backend="memory")
        assert index is not None


@pytest.mark.unit
class TestQuickSearch:
    def test_returns_results(self):
        docs = ["Hello world", "Python programming", "Search engine"]
        results = quick_search(docs, "hello")
        assert isinstance(results, list)

    def test_top_k(self):
        docs = ["doc one", "doc two", "doc three", "doc four"]
        results = quick_search(docs, "doc", k=2)
        assert len(results) <= 2
