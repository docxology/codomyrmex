# Data Curation -- Technical Specification

## Architecture

### MinHash

- **Shingling**: Character n-grams (default k=3) hashed via MD5, modulo Mersenne prime
- **Universal hashing**: h(x) = (a*x + b) mod p with random a, b and p = 2^31 - 1
- **Signature**: For each of n_hashes functions, store the minimum hash value across all shingles
- **Similarity**: Jaccard estimate = fraction of matching positions between two signatures

### LSH Index

- **Banding**: Split n_hashes into n_bands bands of rows_per_band rows each
- **Bucketing**: Each band's sub-signature is a bucket key; collisions indicate candidates
- **Candidate probability**: P(candidate) = 1 - (1 - J^r)^b

### DataCurator

- **Pipeline**: Compute all signatures -> iterate documents -> query LSH for candidates -> check threshold -> emit unique
- **Ordering**: First occurrence wins; later duplicates are removed

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_hashes` | 128 | Number of hash functions in MinHash signature |
| `shingle_size` | 3 | Character n-gram size |
| `n_bands` | 16 | Number of LSH bands |
| `similarity_threshold` | 0.8 | Jaccard similarity cutoff for deduplication |

## Limitations

- Character-level shingling only (no word-level or sentence-level)
- No incremental index updates after deduplication pass
- MD5 used for shingling hash (not cryptographic -- speed is the goal)
- Single-threaded processing
