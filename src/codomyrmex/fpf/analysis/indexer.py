
"""Indexer for FPF specification search and relationship traversal.


logger = get_logger(__name__)
This module provides indexing and search capabilities for FPF patterns
and concepts.
"""

from typing import Any

from ..core.models import FPFIndex, FPFSpec, Pattern


class FPFIndexer:
    """Indexer for FPF patterns and concepts."""

    def __init__(self):
        """Initialize the indexer."""
        self.index: FPFIndex | None = None

    def build_index(self, spec: FPFSpec) -> FPFIndex:
        """Build a search index from the FPF specification.

        Args:
            spec: The FPFSpec object to index

        Returns:
            FPFIndex object containing all indexes
        """
        pattern_index: dict[str, Pattern] = {}
        concept_index: dict[str, list] = {}  # concept_name -> List[Concept]
        keyword_index: dict[str, list[str]] = {}  # keyword -> pattern_ids
        title_index: dict[str, list[str]] = {}  # word -> pattern_ids
        relationship_graph: dict[str, list[str]] = {}  # pattern_id -> related_ids

        # Build pattern index
        for pattern in spec.patterns:
            pattern_index[pattern.id] = pattern

            # Index keywords
            for keyword in pattern.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in keyword_index:
                    keyword_index[keyword_lower] = []
                if pattern.id not in keyword_index[keyword_lower]:
                    keyword_index[keyword_lower].append(pattern.id)

            # Index title words
            title_words = pattern.title.lower().split()
            for word in title_words:
                # Remove common words
                if word not in ["the", "a", "an", "and", "or", "of", "in", "on", "for"]:
                    if word not in title_index:
                        title_index[word] = []
                    if pattern.id not in title_index[word]:
                        title_index[word].append(pattern.id)

            # Build relationship graph
            relationship_graph[pattern.id] = []
            for _dep_type, deps in pattern.dependencies.items():
                for dep in deps:
                    if dep not in relationship_graph[pattern.id]:
                        relationship_graph[pattern.id].append(dep)
                    # Also add reverse relationship
                    if dep not in relationship_graph:
                        relationship_graph[dep] = []
                    if pattern.id not in relationship_graph[dep]:
                        relationship_graph[dep].append(pattern.id)

        # Build concept index
        for concept in spec.concepts:
            concept_lower = concept.name.lower()
            if concept_lower not in concept_index:
                concept_index[concept_lower] = []
            # Store Concept objects, not pattern IDs
            if concept not in concept_index[concept_lower]:
                concept_index[concept_lower].append(concept)

        self.index = FPFIndex(
            pattern_index=pattern_index,
            concept_index=concept_index,
            keyword_index=keyword_index,
            title_index=title_index,
            relationship_graph=relationship_graph,
        )

        return self.index

    def search_patterns(
        self, query: str, filters: dict[str, Any] | None = None
    ) -> list[Pattern]:
        """Search patterns using the built index.

        Args:
            query: Search query string
            filters: Optional filters (status, part, etc.)

        Returns:
            List of matching Pattern objects
        """
        if not self.index:
            return []

        return self.index.search_patterns(query, filters)

    def get_pattern_by_id(self, pattern_id: str) -> Pattern | None:
        """Get a pattern by its ID.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern object or None if not found
        """
        if not self.index:
            return None

        return self.index.get_pattern(pattern_id)

    def get_related_patterns(self, pattern_id: str, depth: int = 1) -> list[Pattern]:
        """Get patterns related to the given pattern.

        Args:
            pattern_id: Pattern identifier
            depth: Relationship traversal depth

        Returns:
            List of related Pattern objects
        """
        if not self.index:
            return []

        return self.index.get_related_patterns(pattern_id, depth)

