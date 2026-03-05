"""Data curation -- MinHash-based near-duplicate detection and deduplication."""

from .minhash import DataCurator, LSHIndex, MinHash

__all__ = ["DataCurator", "LSHIndex", "MinHash"]
