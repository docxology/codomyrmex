"""Knowledge Search — demonstrates codomyrmex search, scrape, and formal_verification.

Integrates with:
- codomyrmex.search for full-text TF-IDF indexing and fuzzy matching
- codomyrmex.scrape for web content extraction and format handling
- codomyrmex.formal_verification for constraint-based verification (Z3)
- codomyrmex.logging_monitoring for structured logging

Example:
    >>> ks = KnowledgeSearch()
    >>> docs = [{"id": "1", "content": "Python async patterns"}, ...]
    >>> results = ks.full_text_search("async", docs)
    >>> matches = ks.fuzzy_match("pythn", ["python", "kotlin", "java"])
    >>> print(matches)
"""

from typing import Any

from codomyrmex.formal_verification import ConstraintSolver
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.scrape import ScrapeFormat, ScrapeOptions, Scraper
from codomyrmex.search import (
    Document,
    FuzzyMatcher,
    InMemoryIndex,
    QueryParser,
    SearchIndex,
    SearchResult,
    create_index,
    quick_search,
)

HAS_SEARCH_MODULES = True  # Exported for integration tests

logger = get_logger(__name__)


class KnowledgeSearch:
    """Demonstrates search + scrape + formal_verification integration.

    Provides document indexing, fuzzy matching, scraping utilities,
    and constraint verification using real codomyrmex modules.

    Attributes:
        index: InMemoryIndex for full-text search.
        fuzzy: FuzzyMatcher for approximate string matching.
        parser: QueryParser for structured query parsing.

    Example:
        >>> ks = KnowledgeSearch()
        >>> ks.build_index([{"id": "doc1", "content": "Codomyrmex modules"}])
        >>> results = ks.full_text_search("modules")
        >>> print(len(results))
    """

    def __init__(self) -> None:
        """Initialize KnowledgeSearch with empty index."""
        self.index: InMemoryIndex = InMemoryIndex()
        self.fuzzy = FuzzyMatcher()
        self.parser = QueryParser()
        logger.info("KnowledgeSearch initialized")

    def build_index(self, documents: list[dict[str, Any]]) -> SearchIndex:
        """Build a full-text search index from documents.

        Converts raw dicts to Document objects and indexes them using
        InMemoryIndex (create_index creates the backend, .index() adds docs).

        Args:
            documents: List of dicts with 'id' and 'content' keys.
                       Optional 'metadata' key supported.

        Returns:
            InMemoryIndex populated with the documents.
        """
        self.index = create_index("memory")
        for i, d in enumerate(documents):
            doc = Document(
                id=str(d.get("id", i)),
                content=str(d.get("content", "")),
                metadata=d.get("metadata", {}),
            )
            self.index.index(doc)
        logger.info(f"Built index with {len(documents)} documents")
        return self.index

    def full_text_search(
        self,
        query: str,
        documents: list[dict[str, Any]] | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Perform full-text search using codomyrmex.search.

        If documents are provided, builds a fresh index first then searches.
        Uses quick_search for one-shot convenience on content strings.

        Args:
            query: Search query string.
            documents: Optional list of document dicts to index first.
            top_k: Maximum results to return.

        Returns:
            List of SearchResult objects sorted by relevance score.
        """
        if documents:
            self.build_index(documents)
            # quick_search takes plain content strings for one-shot searches
            content_strings = [str(d.get("content", "")) for d in documents]
            results = quick_search(content_strings, query, k=top_k)
        else:
            results = self.index.search(query=query, top_k=top_k)

        logger.debug(f"Full-text search '{query}' returned {len(results)} results")
        return results

    def fuzzy_match(
        self, query: str, candidates: list[str], threshold: float = 0.6
    ) -> list[str]:
        """Find fuzzy matches for query within candidates.

        Uses FuzzyMatcher.similarity_ratio to filter candidates above
        the similarity threshold, then find_best_match as fallback.

        Args:
            query: Query string to match.
            candidates: List of candidate strings.
            threshold: Minimum similarity threshold (0.0–1.0).

        Returns:
            List of matching candidate strings above threshold.
        """
        matches = [
            c for c in candidates if self.fuzzy.similarity_ratio(query, c) >= threshold
        ]
        if not matches:
            best = self.fuzzy.find_best_match(query, candidates, threshold)
            matches = [best] if best is not None else []
        logger.debug(f"Fuzzy match '{query}' found {len(matches)} matches")
        return matches

    def parse_query(self, query_string: str) -> dict[str, Any]:
        """Parse a structured query string.

        Args:
            query_string: Query with optional field:value syntax.

        Returns:
            Parsed query representation as dict.
        """
        parsed = self.parser.parse(query_string)
        return {"raw": query_string, "parsed": parsed}

    def scraper_info(self) -> dict[str, Any]:
        """Return info about available scrape formats.

        Shows what ScrapeFormat values are available without
        making any network calls.

        Returns:
            Dictionary with available formats and scraper config.
        """
        formats = [fmt.value for fmt in ScrapeFormat]
        return {
            "scraper_class": Scraper.__name__,
            "options_class": ScrapeOptions.__name__,
            "available_formats": formats,
            "default_format": ScrapeFormat.MARKDOWN.value,
        }

    def verify_constraints(
        self,
        assertions: list[str],
        timeout_ms: int = 5000,
    ) -> dict[str, Any]:
        """Verify a set of logical constraints using formal_verification.

        Uses codomyrmex.formal_verification.ConstraintSolver (Z3 backend)
        to check satisfiability of assertions. Requires z3-solver installed.

        Args:
            assertions: List of Z3 constraint strings to verify.
            timeout_ms: Solver timeout in milliseconds.

        Returns:
            Dictionary with:
            - status: 'satisfiable', 'unsatisfiable', or 'unknown'
            - model: variable assignments if satisfiable
            - solver_available: bool
        """
        result: dict[str, Any] = {
            "assertions": assertions,
            "status": "unknown",
            "model": None,
            "solver_available": False,
        }

        try:
            solver = ConstraintSolver()
            result["solver_available"] = True

            for assertion in assertions:
                solver.add_item(assertion)

            solve_result = solver.solve(timeout_ms=timeout_ms)
            result["status"] = solve_result.status.value
            result["model"] = solve_result.model

        except Exception as e:
            logger.warning(f"Constraint verification failed: {e}")
            result["error"] = str(e)

        return result
