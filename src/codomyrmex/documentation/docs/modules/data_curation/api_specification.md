# Data Curation — API Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview

The `data_curation` module provides MinHash-based near-duplicate detection and deduplication for text corpora. Uses Locality-Sensitive Hashing (LSH) for sub-quadratic similarity search. Pure Python + NumPy implementation with no external NLP dependencies.

## 2. Public Exports

```python
from codomyrmex.data_curation import DataCurator, LSHIndex, MinHash
```

## 3. Classes

### 3.1 `MinHash`

MinHash signature generator for estimating Jaccard similarity between text documents.

#### Constructor

```python
MinHash(n_hashes: int = 128, shingle_size: int = 3)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `n_hashes` | `int` | `128` | Number of hash functions (signature dimensionality) |
| `shingle_size` | `int` | `3` | Character n-gram size for shingling |

#### Methods

| Method | Signature | Description |
| :--- | :--- | :--- |
| `signature` | `(text: str) → np.ndarray` | Compute `(n_hashes,)` MinHash signature for text |
| `jaccard_estimate` | `(sig_a, sig_b) → float` | Estimate Jaccard similarity from two signatures |
| `are_similar` | `(text_a, text_b, threshold=0.8) → bool` | Check if two texts are near-duplicates |

**Internals**: Uses universal hashing `h(x) = (a*x + b) mod p` with Mersenne prime `p = 2^31 - 1`. Shingling converts text to character n-grams hashed via MD5 (non-cryptographic, chosen for speed).

### 3.2 `LSHIndex`

Locality-Sensitive Hashing index for approximate nearest-neighbour candidate generation.

#### Constructor

```python
LSHIndex(n_hashes: int = 128, n_bands: int = 16)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `n_hashes` | `int` | `128` | Must match MinHash's `n_hashes` |
| `n_bands` | `int` | `16` | Number of bands (higher = more candidates, lower precision) |

Derived: `rows_per_band = n_hashes // n_bands` (default: 8 rows per band).

#### Methods

| Method | Signature | Description |
| :--- | :--- | :--- |
| `add` | `(doc_id: str, signature: np.ndarray) → None` | Index a document by its MinHash signature |
| `query` | `(signature: np.ndarray) → set[str]` | Find all candidate near-duplicate document IDs |

**Candidate probability**: `P(candidate) ≈ 1 - (1 - J^r)^b` where `J` is true Jaccard, `r` = rows per band, `b` = number of bands.

### 3.3 `DataCurator`

End-to-end deduplication pipeline combining MinHash and LSH.

#### Constructor

```python
DataCurator(
    similarity_threshold: float = 0.8,
    n_hashes: int = 128,
    n_bands: int = 16,
    shingle_size: int = 3,
)
```

#### Methods

| Method | Signature | Description |
| :--- | :--- | :--- |
| `deduplicate` | `(texts: list[str]) → tuple[list[str], dict]` | Remove near-duplicates, return unique texts + statistics |

**Return value** of `deduplicate`:

```python
(
    unique_texts: list[str],  # Deduplicated texts (first occurrence wins)
    stats: {
        "total_documents": int,
        "unique_documents": int,
        "duplicates_removed": int,
        "duplicate_pairs_found": int,
        "deduplication_ratio": float,  # unique / total
    }
)
```

## 4. MCP Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `data_curation_deduplicate` | `texts: list`, `threshold: float = 0.8` | Deduplicate text list via MinHash + LSH |
| `data_curation_similarity` | `text_a: str`, `text_b: str` | Estimate Jaccard similarity between two texts |

### Return Formats

**`data_curation_deduplicate`**:

```python
{"unique_texts": list[str], "stats": dict}
```

**`data_curation_similarity`**:

```python
{"similarity": float, "are_similar": bool}  # are_similar uses 0.8 threshold
```

## 5. Usage Examples

### Corpus Deduplication

```python
from codomyrmex.data_curation import DataCurator

corpus = [
    "The quick brown fox jumps over the lazy dog",
    "The quick brown fox leaps over the lazy dog",  # near-duplicate
    "Completely different text about machine learning",
]

curator = DataCurator(similarity_threshold=0.8)
unique_texts, stats = curator.deduplicate(corpus)

print(f"Kept {stats['unique_documents']}/{stats['total_documents']} documents")
# Kept 2/3 documents
```

### Pairwise Similarity

```python
from codomyrmex.data_curation import MinHash

mh = MinHash()
sig_a = mh.signature("The quick brown fox jumps over the lazy dog")
sig_b = mh.signature("The quick brown fox leaps over the lazy dog")

similarity = mh.jaccard_estimate(sig_a, sig_b)
print(f"Similarity: {similarity:.2f}")  # ~0.85
```

### Building a Custom Index

```python
from codomyrmex.data_curation import MinHash, LSHIndex

mh = MinHash(n_hashes=128)
lsh = LSHIndex(n_hashes=128, n_bands=16)

# Index documents
for doc_id, text in documents.items():
    sig = mh.signature(text)
    lsh.add(doc_id, sig)

# Query for near-duplicates
query_sig = mh.signature("new document text")
candidates = lsh.query(query_sig)
```

## 6. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
