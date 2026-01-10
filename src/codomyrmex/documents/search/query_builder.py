from typing import List, Optional

from codomyrmex.logging_monitoring import get_logger
























"""Query builder for document search."""

logger = get_logger(__name__)
class QueryBuilder:
    """Builder for constructing search queries."""
    
    def __init__(self):

        self.terms: List[str] = []
        self.filters: dict = {}
        self.sort_by: Optional[str] = None
    
    def add_term(self, term: str) -> "QueryBuilder":
        """Add a search term."""
        self.terms.append(term)
        return self
    
    def add_filter(self, field: str, value: str) -> "QueryBuilder":
        """Add a filter."""
        self.filters[field] = value
        return self
    
    def set_sort(self, field: str) -> "QueryBuilder":
        """Set sort field."""
        self.sort_by = field
        return self
    
    def build(self) -> str:
        """Build query string."""
        query = " ".join(self.terms)
        return query


def build_query(terms: List[str], filters: dict = None, sort_by: str = None) -> str:
    """
    Build a search query.
    
    Args:
        terms: List of search terms
        filters: Optional filters dictionary
        sort_by: Optional sort field
    
    Returns:
        Query string
    """
    builder = QueryBuilder()
    for term in terms:
        builder.add_term(term)
    if filters:
        for field, value in filters.items():
            builder.add_filter(field, value)
    if sort_by:
        builder.set_sort(sort_by)
    return builder.build()

