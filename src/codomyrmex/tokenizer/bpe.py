"""Byte-Pair Encoding tokenizer — from-scratch implementation.

Based on the original Sennrich et al. 2016 algorithm. Trains by iteratively
merging the most frequent adjacent byte pair in the corpus until the target
vocabulary size is reached.
"""

import json
from collections import defaultdict
from pathlib import Path


class BPETokenizer:
    """Byte-Pair Encoding tokenizer trained from scratch.

    Based on the original Sennrich et al. 2016 algorithm.
    Trains by iteratively merging the most frequent byte pair in the corpus.

    Attributes:
        vocab_size: Target vocabulary size (upper bound).
        merges: Ordered list of merge rules learned during training.
        vocab: Mapping from token string to integer ID.
        id_to_token: Reverse mapping from integer ID to token string.
    """

    SPECIAL_TOKENS = {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3}

    def __init__(self, vocab_size: int = 1000) -> None:
        self.vocab_size = vocab_size
        self.merges: list[tuple[str, str]] = []  # ordered merge rules
        self.vocab: dict[str, int] = {}  # token -> id
        self.id_to_token: dict[int, str] = {}  # id -> token
        self._trained = False

    def train(self, texts: list[str], vocab_size: int | None = None) -> None:
        """Train BPE on a corpus of texts.

        Algorithm:
        1. Start with character vocabulary (UTF-8 bytes + special tokens)
        2. Count frequency of all adjacent pairs in corpus
        3. Merge most frequent pair into a new token
        4. Repeat until vocab_size reached

        Args:
            texts: List of training strings.
            vocab_size: Target vocabulary size (overrides __init__ value).
        """
        if vocab_size:
            self.vocab_size = vocab_size

        # Initialize with special tokens + character vocab
        self.vocab = dict(self.SPECIAL_TOKENS)

        # Tokenize corpus to word-level with end-of-word marker.
        # Each word becomes a space-separated character sequence with </w> at end.
        # e.g. "hello" -> "h e l l o </w>"
        word_freqs = self._get_word_frequencies(texts)

        # Add all initial characters to vocab
        chars: set[str] = set()
        for word in word_freqs:
            for token in word.split(" "):
                chars.add(token)
        for char in sorted(chars):
            if char not in self.vocab:
                self.vocab[char] = len(self.vocab)

        # BPE merge loop — word_splits stores each word as a list of tokens
        word_splits = {word: word.split(" ") for word in word_freqs}

        while len(self.vocab) < self.vocab_size:
            # Count pair frequencies
            pair_freqs = self._get_pair_frequencies(word_splits, word_freqs)
            if not pair_freqs:
                break

            # Find best pair
            best_pair = max(pair_freqs, key=pair_freqs.get)  # type: ignore

            # Merge best pair everywhere
            word_splits = self._merge_pair(best_pair, word_splits)
            self.merges.append(best_pair)

            # Add merged token to vocab
            new_token = "".join(best_pair)
            if new_token not in self.vocab:
                self.vocab[new_token] = len(self.vocab)

        # Build reverse mapping
        self.id_to_token = {v: k for k, v in self.vocab.items()}
        self._trained = True

    def encode(self, text: str) -> list[int]:
        """Encode text to token IDs using learned BPE merges.

        Args:
            text: Input string to tokenize.

        Returns:
            List of integer token IDs.

        Raises:
            RuntimeError: If tokenizer has not been trained.
        """
        if not self._trained:
            raise RuntimeError("Tokenizer must be trained before encoding")

        tokens: list[int] = []
        # Split on whitespace, apply BPE to each word
        words = text.split()
        for word in words:
            # Each word becomes characters + end-of-word marker
            chars = [*list(word), "</w>"]
            word_pieces = self._apply_merges(chars)
            for piece in word_pieces:
                token_id = self.vocab.get(piece, self.vocab.get("<UNK>", 1))
                tokens.append(token_id)

        return tokens

    def decode(self, token_ids: list[int]) -> str:
        """Decode token IDs back to text.

        Args:
            token_ids: List of integer token IDs.

        Returns:
            Reconstructed text string.

        Raises:
            RuntimeError: If tokenizer has not been trained.
        """
        if not self._trained:
            raise RuntimeError("Tokenizer must be trained before decoding")

        tokens = [self.id_to_token.get(tid, "<UNK>") for tid in token_ids]
        # Join and remove end-of-word markers, replacing with spaces
        text = "".join(tokens).replace("</w>", " ").rstrip()
        return text

    def _get_word_frequencies(self, texts: list[str]) -> dict[str, int]:
        """Count word frequencies in corpus, marking end-of-word.

        Each word is represented as a space-separated character string with
        '</w>' appended.  e.g. "hello" -> "h e l l o </w>".

        Args:
            texts: Corpus of training strings.

        Returns:
            Dict mapping word representations to their frequency counts.
        """
        freqs: dict[str, int] = defaultdict(int)
        for text in texts:
            for word in text.split():
                # Represent word as character sequence with end marker
                word_repr = " ".join(list(word)) + " </w>"
                freqs[word_repr] += 1
        return dict(freqs)

    def _get_pair_frequencies(
        self,
        word_splits: dict[str, list[str]],
        word_freqs: dict[str, int],
    ) -> dict[tuple[str, str], int]:
        """Count frequency of all adjacent token pairs.

        Args:
            word_splits: Current tokenization of each word.
            word_freqs: Frequency of each word in corpus.

        Returns:
            Dict mapping (token_a, token_b) pairs to their total frequency.
        """
        pair_freqs: dict[tuple[str, str], int] = defaultdict(int)
        for word, splits in word_splits.items():
            freq = word_freqs.get(word, 1)
            for i in range(len(splits) - 1):
                pair_freqs[(splits[i], splits[i + 1])] += freq
        return dict(pair_freqs)

    def _merge_pair(
        self,
        pair: tuple[str, str],
        word_splits: dict[str, list[str]],
    ) -> dict[str, list[str]]:
        """Merge all occurrences of a pair in word splits.

        Args:
            pair: The (left, right) token pair to merge.
            word_splits: Current tokenization of each word.

        Returns:
            Updated word_splits with the pair merged into a single token.
        """
        new_splits: dict[str, list[str]] = {}
        merged = "".join(pair)
        for word, splits in word_splits.items():
            new_word: list[str] = []
            i = 0
            while i < len(splits):
                if (
                    i < len(splits) - 1
                    and splits[i] == pair[0]
                    and splits[i + 1] == pair[1]
                ):
                    new_word.append(merged)
                    i += 2
                else:
                    new_word.append(splits[i])
                    i += 1
            new_splits[word] = new_word
        return new_splits

    def _apply_merges(self, chars: list[str]) -> list[str]:
        """Apply learned merge rules to a character sequence.

        Merges are applied greedily in the order they were learned (most
        frequent pairs first). This is the standard BPE application algorithm.

        Args:
            chars: List of character tokens (including '</w>' marker).

        Returns:
            List of merged tokens after all applicable rules are applied.
        """
        word = list(chars)
        for merge in self.merges:
            i = 0
            new_word: list[str] = []
            while i < len(word):
                if (
                    i < len(word) - 1
                    and word[i] == merge[0]
                    and word[i + 1] == merge[1]
                ):
                    new_word.append(merge[0] + merge[1])
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            word = new_word
        return word

    def save(self, path: str | Path) -> None:
        """Save tokenizer to JSON file.

        Persists vocab, merges, and vocab_size so the tokenizer can be
        reconstructed without retraining.

        Args:
            path: File path to write the JSON to.
        """
        path = Path(path)
        data = {
            "vocab_size": self.vocab_size,
            "vocab": self.vocab,
            "merges": self.merges,
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    @classmethod
    def load(cls, path: str | Path) -> "BPETokenizer":
        """Load tokenizer from JSON file.

        Args:
            path: File path to read the JSON from.

        Returns:
            Reconstructed BPETokenizer instance ready for encode/decode.
        """
        path = Path(path)
        data = json.loads(path.read_text())
        tok = cls(vocab_size=data["vocab_size"])
        tok.vocab = data["vocab"]
        tok.merges = [tuple(m) for m in data["merges"]]
        tok.id_to_token = {int(v): k for k, v in tok.vocab.items()}
        tok._trained = True
        return tok

    @property
    def vocab_size_actual(self) -> int:
        """Return the actual number of tokens in the vocabulary."""
        return len(self.vocab)
