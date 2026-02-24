"""Query builder for document search."""


from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class QueryBuilder:
    """Builder for constructing search queries."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self.terms: list[str] = []
        self.filters: dict = {}
        self.sort_by: str | None = None

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

    def to_dict(self) -> dict:
        """Serialize query builder state to a dictionary."""
        return {
            "terms": self.terms,
            "filters": self.filters,
            "sort_by": self.sort_by,
        }


def build_query(terms: list[str], filters: dict = None, sort_by: str = None) -> str:
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
