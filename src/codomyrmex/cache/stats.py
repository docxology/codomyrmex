from dataclasses import dataclass















"""
Cache statistics data structures.
"""



@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        """Calculate miss rate."""
        if self.total_requests == 0:
            return 0.0
        return self.misses / self.total_requests

    @property
    def usage_percent(self) -> float:
        """Calculate cache usage percentage."""
        if self.max_size == 0:
            return 0.0
        return (self.size / self.max_size) * 100


