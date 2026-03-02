# Tokenizer Module — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Algorithm: Byte-Pair Encoding (BPE)

### Reference

Sennrich, R., Haddow, B., & Birch, A. (2016). "Neural Machine Translation of Rare Words with Subword Units." ACL 2016.

### Training Algorithm

**Input**: Corpus of text strings, target `vocab_size`

**Output**: Ordered list of merge rules, token vocabulary

```
1. Initialize vocab = SPECIAL_TOKENS + {all unique characters in corpus}
2. Represent each word as space-separated characters + "</w>" end marker
3. WHILE |vocab| < vocab_size:
   a. Count frequency of all adjacent (token_a, token_b) pairs
      weighted by word frequency
   b. IF no pairs found: BREAK
   c. best_pair = argmax(pair_frequencies)
   d. Merge best_pair everywhere in corpus
   e. Add joined token to vocab
   f. Record merge rule
4. Build reverse mapping (id -> token)
```

**Complexity**: O(V * N) where V = target vocab size, N = corpus size in tokens.

### Encoding Algorithm

**Input**: Text string, learned merge rules

**Output**: List of integer token IDs

```
1. Split text on whitespace into words
2. FOR each word:
   a. Split into characters + "</w>"
   b. FOR each merge rule (in training order):
      - Scan left-to-right, merge matching adjacent pairs
   c. Map resulting tokens to IDs via vocab
3. Return concatenated ID list
```

### Decoding Algorithm

**Input**: List of integer token IDs

**Output**: Reconstructed text string

```
1. Map each ID to its token string
2. Concatenate all tokens
3. Replace "</w>" with space
4. Strip trailing whitespace
```

## Special Tokens

| Token | ID | Purpose |
|---|---|---|
| `<PAD>` | 0 | Padding for batch alignment |
| `<UNK>` | 1 | Unknown/out-of-vocabulary token |
| `<BOS>` | 2 | Beginning of sequence |
| `<EOS>` | 3 | End of sequence |

The `Vocabulary` class additionally includes:

| Token | ID | Purpose |
|---|---|---|
| `<MASK>` | 4 | Masked token for MLM-style tasks |

## Serialization Format

Tokenizers are saved as JSON with the following schema:

```json
{
  "vocab_size": 1000,
  "vocab": {
    "<PAD>": 0,
    "<UNK>": 1,
    "a": 4,
    "th": 30,
    "the": 45
  },
  "merges": [
    ["t", "h"],
    ["th", "e"],
    ["i", "n"]
  ]
}
```

## Interface Contracts

### BPETokenizer

```python
class BPETokenizer:
    SPECIAL_TOKENS: dict[str, int]

    def __init__(self, vocab_size: int = 1000) -> None: ...
    def train(self, texts: list[str], vocab_size: int | None = None) -> None: ...
    def encode(self, text: str) -> list[int]: ...
    def decode(self, token_ids: list[int]) -> str: ...
    def save(self, path: str | Path) -> None: ...
    @classmethod
    def load(cls, path: str | Path) -> "BPETokenizer": ...
    @property
    def vocab_size_actual(self) -> int: ...
```

### Vocabulary

```python
class Vocabulary:
    SPECIAL: dict[str, int]

    def __init__(self) -> None: ...
    def add(self, token: str) -> int: ...
    def __len__(self) -> int: ...
    def token_to_id(self, token: str) -> int: ...
    def id_to_token_str(self, idx: int) -> str: ...
```

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| Python stdlib | >= 3.10 | `json`, `collections.defaultdict`, `pathlib.Path` |
| `codomyrmex.model_context_protocol` | Internal | `@mcp_tool` decorator for auto-discovery |

No external packages required.

## Limitations

- **No regex-based pre-tokenization**: Unlike GPT-2/GPT-4 tokenizers, this implementation splits only on whitespace. It does not handle contractions, punctuation grouping, or number splitting.
- **No byte-level fallback**: Operates on Unicode characters, not raw UTF-8 bytes. Characters not seen during training map to `<UNK>`.
- **Single-threaded training**: No parallel pair counting. Suitable for small to medium corpora.
- **Greedy merge application**: Encoding applies merges left-to-right in training order. This is standard BPE but may not produce the globally optimal segmentation.

## Navigation

- **Parent**: [codomyrmex](../SPEC.md)
- **Related**: [llm](../llm/SPEC.md), [prompt_engineering](../prompt_engineering/SPEC.md)
