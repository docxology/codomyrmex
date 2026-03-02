"""Data curation -- MinHash-based near-duplicate detection and deduplication."""
from .minhash import MinHash, LSHIndex, DataCurator

__all__ = ["MinHash", "LSHIndex", "DataCurator"]
