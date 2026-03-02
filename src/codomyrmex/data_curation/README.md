# Data Curation

MinHash-based near-duplicate detection and corpus deduplication.

## Overview

The data_curation module provides efficient text deduplication using MinHash signatures with Locality-Sensitive Hashing (LSH). It estimates Jaccard similarity between documents without computing full set intersections, reducing O(n^2) comparisons to near-linear time.

## Quick Start

```python
from codomyrmex.data_curation import DataCurator

curator = DataCurator(similarity_threshold=0.8)
texts = [
    "The quick brown fox jumps over the lazy dog",
    "The quick brown fox leaps over the lazy dog",  # near-duplicate
    "Machine learning is a subset of artificial intelligence",
]
unique_texts, stats = curator.deduplicate(texts)

print(stats)
# {'total_documents': 3, 'unique_documents': 2, 'duplicates_removed': 1, ...}
```

### Similarity Estimation

```python
from codomyrmex.data_curation import MinHash

mh = MinHash(n_hashes=128, shingle_size=3)
sig_a = mh.signature("hello world this is a test")
sig_b = mh.signature("hello world this is a test")
print(mh.jaccard_estimate(sig_a, sig_b))  # 1.0
```

### LSH Index for Fast Lookup

```python
from codomyrmex.data_curation import MinHash, LSHIndex

mh = MinHash()
index = LSHIndex()
index.add("doc1", mh.signature("first document text"))
index.add("doc2", mh.signature("second document text"))

candidates = index.query(mh.signature("first document text"))
# Returns {"doc1"} as a candidate match
```

## Algorithm Details

- **Shingling**: Text is converted to character n-grams (default k=3), each hashed via MD5
- **MinHash**: Universal hashing h(x) = (ax + b) mod p with Mersenne prime p = 2^31 - 1
- **LSH**: Signature split into b bands of r rows; documents sharing any band bucket are candidates
- **Threshold tuning**: P(candidate) = 1 - (1 - J^r)^b where J is true Jaccard similarity

## Dependencies

- `numpy` (core dependency)
- `hashlib` (stdlib)
