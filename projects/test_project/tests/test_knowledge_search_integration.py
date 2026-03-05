"""Integration tests for knowledge_search.py — search + scrape + formal_verification."""

import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSearchImports:
    """Verify codomyrmex.search imports used in knowledge_search."""

    def test_import_create_index(self):
        """create_index is importable and callable."""
        from codomyrmex.search import create_index

        assert callable(create_index)

    def test_import_quick_search(self):
        """quick_search is importable and callable."""
        from codomyrmex.search import quick_search

        assert callable(quick_search)

    def test_import_document(self):
        """Document model is importable and constructable."""
        from codomyrmex.search import Document

        doc = Document(id="test", content="hello world")
        assert doc is not None
        assert doc.id == "test"
        assert doc.content == "hello world"

    def test_import_fuzzy_matcher(self):
        """FuzzyMatcher is importable and constructable."""
        from codomyrmex.search import FuzzyMatcher

        matcher = FuzzyMatcher()
        assert matcher is not None

    def test_import_query_parser(self):
        """QueryParser is importable and constructable."""
        from codomyrmex.search import QueryParser

        parser = QueryParser()
        assert parser is not None

    def test_import_search_result(self):
        """SearchResult is importable."""
        from codomyrmex.search import SearchResult

        assert SearchResult is not None

    def test_import_in_memory_index(self):
        """InMemoryIndex is importable and constructable."""
        from codomyrmex.search import InMemoryIndex

        index = InMemoryIndex()
        assert index is not None


class TestScrapeImports:
    """Verify codomyrmex.scrape imports used in knowledge_search."""

    def test_import_scraper(self):
        """Scraper class is importable."""
        from codomyrmex.scrape import Scraper

        assert Scraper is not None

    def test_import_scrape_options(self):
        """ScrapeOptions is importable and constructable."""
        from codomyrmex.scrape import ScrapeOptions

        opts = ScrapeOptions()
        assert opts is not None

    def test_import_scrape_format(self):
        """ScrapeFormat enum is importable with expected values."""
        from codomyrmex.scrape import ScrapeFormat

        assert ScrapeFormat is not None
        assert ScrapeFormat.MARKDOWN is not None

    def test_import_scrape_error(self):
        """ScrapeError exception is importable."""
        from codomyrmex.scrape import ScrapeError

        assert issubclass(ScrapeError, Exception)


class TestFormalVerificationImports:
    """Verify codomyrmex.formal_verification imports used in knowledge_search."""

    def test_import_constraint_solver(self):
        """ConstraintSolver is importable."""
        from codomyrmex.formal_verification import ConstraintSolver

        assert ConstraintSolver is not None

    def test_import_solver_status(self):
        """SolverStatus is importable and has expected values."""
        from codomyrmex.formal_verification import SolverStatus

        assert SolverStatus is not None
        values = [s.value for s in SolverStatus]
        assert len(values) > 0

    def test_import_solver_error(self):
        """SolverError is importable."""
        from codomyrmex.formal_verification import SolverError

        assert issubclass(SolverError, Exception)


class TestKnowledgeSearchModule:
    """Functional tests for KnowledgeSearch class."""

    def test_has_search_modules_flag(self):
        """HAS_SEARCH_MODULES flag is True in knowledge_search.py."""
        from src.knowledge_search import HAS_SEARCH_MODULES

        assert HAS_SEARCH_MODULES is True

    def test_knowledge_search_instantiation(self):
        """KnowledgeSearch can be instantiated without errors."""
        from src.knowledge_search import KnowledgeSearch

        ks = KnowledgeSearch()
        assert ks is not None
        assert ks.index is not None
        assert ks.fuzzy is not None
        assert ks.parser is not None

    def test_build_index_returns_index(self):
        """build_index() with documents returns a SearchIndex."""
        from src.knowledge_search import KnowledgeSearch

        ks = KnowledgeSearch()
        docs = [
            {"id": "1", "content": "Python is great for data science"},
            {"id": "2", "content": "JavaScript runs in the browser"},
            {"id": "3", "content": "Rust provides memory safety"},
        ]
        index = ks.build_index(docs)
        assert index is not None

    def test_full_text_search_returns_list(self):
        """full_text_search() returns a list of results."""
        from src.knowledge_search import KnowledgeSearch

        ks = KnowledgeSearch()
        docs = [
            {"id": "1", "content": "Python is great for data science"},
            {"id": "2", "content": "JavaScript runs in the browser"},
        ]
        results = ks.full_text_search("Python", docs)
        assert isinstance(results, list)

    def test_fuzzy_match_returns_list(self):
        """fuzzy_match() returns a list of strings."""
        from src.knowledge_search import KnowledgeSearch

        ks = KnowledgeSearch()
        candidates = ["python", "javascript", "typescript", "kotlin"]
        matches = ks.fuzzy_match("pythn", candidates)
        assert isinstance(matches, list)

    def test_scraper_info_returns_dict(self):
        """scraper_info() returns a dict with expected keys."""
        from src.knowledge_search import KnowledgeSearch

        ks = KnowledgeSearch()
        info = ks.scraper_info()
        assert isinstance(info, dict)
        assert "scraper_class" in info
        assert "available_formats" in info
        assert isinstance(info["available_formats"], list)
        assert len(info["available_formats"]) > 0

    def test_verify_constraints_returns_dict(self):
        """verify_constraints() returns a dict with status key."""
        from src.knowledge_search import KnowledgeSearch

        ks = KnowledgeSearch()
        result = ks.verify_constraints([], timeout_ms=100)
        assert isinstance(result, dict)
        assert "status" in result
        assert "solver_available" in result
