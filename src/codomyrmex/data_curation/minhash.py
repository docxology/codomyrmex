"""
MinHash-based near-duplicate detection and deduplication.

Implements MinHash (Broder 1997) with Locality-Sensitive Hashing (LSH)
for efficient corpus-scale deduplication. Pure Python + NumPy, no
external libraries.
"""

import hashlib
import re

import numpy as np


class MinHash:
    """
    MinHash approximation for Jaccard similarity of sets.

    MinHash (Broder 1997) estimates Jaccard similarity J(A,B) = |A n B|/|A u B|
    using random hash functions. With n_hashes functions:
    P[h(A) == h(B)] = J(A, B)

    This enables fast deduplication of text by shingling (n-grams) and
    comparing MinHash signatures rather than full document overlap.
    """

    def __init__(self, n_hashes: int = 128, shingle_size: int = 3):
        self.n_hashes = n_hashes
        self.shingle_size = shingle_size

        # Random hash parameters (universal hashing: h(x) = (a*x + b) mod p)
        rng = np.random.default_rng(42)
        self._a = rng.integers(1, 2**31, size=n_hashes)
        self._b = rng.integers(0, 2**31, size=n_hashes)
        self._p = 2**31 - 1  # Mersenne prime

    def _shingle(self, text: str) -> set[int]:
        """Convert text to a set of hashed k-shingles (character n-grams)."""
        text = re.sub(r"\s+", " ", text.lower().strip())
        shingles = set()
        for i in range(len(text) - self.shingle_size + 1):
            shingle = text[i : i + self.shingle_size]
            h = int(hashlib.md5(shingle.encode()).hexdigest(), 16) % self._p
            shingles.add(h)
        return shingles or {0}  # Prevent empty set

    def signature(self, text: str) -> np.ndarray:
        """
        Compute MinHash signature for text.

        For each hash function h_i, signature[i] = min_{s in shingles} h_i(s)

        Returns:
            (n_hashes,) array of minimum hash values
        """
        shingles = self._shingle(text)
        shingle_arr = np.array(list(shingles), dtype=np.int64)

        # Compute all hash values: (n_hashes, n_shingles)
        hash_values = (
            self._a[:, np.newaxis] * shingle_arr[np.newaxis, :] + self._b[:, np.newaxis]
        ) % self._p

        # MinHash: minimum over shingles for each hash function
        return hash_values.min(axis=1).astype(np.int64)

    def jaccard_estimate(self, sig_a: np.ndarray, sig_b: np.ndarray) -> float:
        """Estimate Jaccard similarity from two MinHash signatures."""
        return float(np.mean(sig_a == sig_b))

    def are_similar(self, text_a: str, text_b: str, threshold: float = 0.8) -> bool:
        """Check if two texts are near-duplicates."""
        sig_a = self.signature(text_a)
        sig_b = self.signature(text_b)
        return self.jaccard_estimate(sig_a, sig_b) >= threshold


class LSHIndex:
    """
    Locality-Sensitive Hashing for fast near-duplicate lookup.

    MinHash + LSH reduces near-duplicate search from O(n^2) to O(n):
    - Split n_hashes into b bands of r rows each
    - Documents in same bucket for ANY band are candidate pairs
    - P(same bucket) approx 1 - (1 - J^r)^b
    """

    def __init__(self, n_hashes: int = 128, n_bands: int = 16):
        self.n_hashes = n_hashes
        self.n_bands = n_bands
        self.rows_per_band = n_hashes // n_bands
        self.buckets: dict[tuple, list[str]] = {}  # bucket -> list of doc IDs
        self.signatures: dict[str, np.ndarray] = {}

    def add(self, doc_id: str, signature: np.ndarray) -> None:
        """Add document to LSH index."""
        self.signatures[doc_id] = signature

        for band_idx in range(self.n_bands):
            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band
            band_sig = tuple(signature[start:end].tolist())
            bucket_key = (band_idx, band_sig)

            if bucket_key not in self.buckets:
                self.buckets[bucket_key] = []
            self.buckets[bucket_key].append(doc_id)

    def query(self, signature: np.ndarray) -> set[str]:
        """Find all candidate near-duplicates for a query signature."""
        candidates = set()
        for band_idx in range(self.n_bands):
            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band
            band_sig = tuple(signature[start:end].tolist())
            bucket_key = (band_idx, band_sig)
            if bucket_key in self.buckets:
                candidates.update(self.buckets[bucket_key])
        return candidates


class DataCurator:
    """
    Full data curation pipeline using MinHash + LSH for deduplication.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.8,
        n_hashes: int = 128,
        n_bands: int = 16,
        shingle_size: int = 3,
    ):
        self.threshold = similarity_threshold
        self.minhash = MinHash(n_hashes=n_hashes, shingle_size=shingle_size)
        self.lsh = LSHIndex(n_hashes=n_hashes, n_bands=n_bands)

    def deduplicate(self, texts: list[str]) -> tuple[list[str], dict]:
        """
        Remove near-duplicate texts from corpus.

        Returns:
            unique_texts: Deduplicated texts
            stats: Deduplication statistics
        """
        unique_indices = []
        duplicate_pairs = []
        seen_ids = set()

        # Build index
        signatures = [self.minhash.signature(t) for t in texts]

        for i, (_text, sig) in enumerate(zip(texts, signatures, strict=False)):
            doc_id = str(i)
            candidates = self.lsh.query(sig)

            is_duplicate = False
            for cand_id in candidates:
                if cand_id in seen_ids:
                    cand_sig = signatures[int(cand_id)]
                    sim = self.minhash.jaccard_estimate(sig, cand_sig)
                    if sim >= self.threshold:
                        duplicate_pairs.append((i, int(cand_id), sim))
                        is_duplicate = True
                        break

            if not is_duplicate:
                unique_indices.append(i)
                seen_ids.add(doc_id)

            self.lsh.add(doc_id, sig)

        unique_texts = [texts[i] for i in unique_indices]
        stats = {
            "total_documents": len(texts),
            "unique_documents": len(unique_texts),
            "duplicates_removed": len(texts) - len(unique_texts),
            "duplicate_pairs_found": len(duplicate_pairs),
            "deduplication_ratio": len(unique_texts) / len(texts) if texts else 1.0,
        }
        return unique_texts, stats
