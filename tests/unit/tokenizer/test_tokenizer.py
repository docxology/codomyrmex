"""Unit tests for the BPE tokenizer module.

Tests training, encoding, decoding, save/load, vocabulary, and MCP tools.
All tests use real BPE training on a small corpus — no mocks.
"""

import pytest

from codomyrmex.tokenizer import BPETokenizer, Vocabulary

CORPUS = [
    "the quick brown fox jumps over the lazy dog",
    "hello world this is a test sentence",
    "the cat sat on the mat",
    "machine learning and natural language processing",
    "byte pair encoding is a tokenization algorithm",
    "the the the the the fox fox fox",
]


class TestBPETraining:
    """Tests for BPE training algorithm."""

    @pytest.mark.unit
    def test_train_produces_vocab(self):
        tok = BPETokenizer(vocab_size=100)
        tok.train(CORPUS)
        assert tok._trained is True
        assert len(tok.vocab) >= 4  # at minimum special tokens
        assert len(tok.vocab) <= 100

    @pytest.mark.unit
    def test_vocab_contains_special_tokens(self):
        tok = BPETokenizer(vocab_size=50)
        tok.train(CORPUS)
        assert "<PAD>" in tok.vocab
        assert "<UNK>" in tok.vocab
        assert "<BOS>" in tok.vocab
        assert "<EOS>" in tok.vocab

    @pytest.mark.unit
    def test_merges_not_empty(self):
        tok = BPETokenizer(vocab_size=100)
        tok.train(CORPUS)
        assert len(tok.merges) > 0

    @pytest.mark.unit
    def test_frequent_pair_gets_merged(self):
        """Frequent character pairs should appear as merge rules."""
        tok = BPETokenizer(vocab_size=200)
        tok.train(CORPUS)
        # At least some merges should have happened
        merged_tokens = ["".join(m) for m in tok.merges]
        assert len(merged_tokens) > 0

    @pytest.mark.unit
    def test_vocab_size_override(self):
        """Passing vocab_size to train() overrides __init__ value."""
        tok = BPETokenizer(vocab_size=50)
        tok.train(CORPUS, vocab_size=80)
        assert tok.vocab_size == 80
        assert tok.vocab_size_actual <= 80

    @pytest.mark.unit
    def test_id_to_token_mapping_consistent(self):
        """id_to_token should be exact inverse of vocab."""
        tok = BPETokenizer(vocab_size=100)
        tok.train(CORPUS)
        for token, tid in tok.vocab.items():
            assert tok.id_to_token[tid] == token

    @pytest.mark.unit
    def test_train_empty_corpus(self):
        """Training on empty corpus should still produce special tokens."""
        tok = BPETokenizer(vocab_size=50)
        tok.train([])
        assert tok._trained is True
        assert "<PAD>" in tok.vocab
        assert len(tok.merges) == 0

    @pytest.mark.unit
    def test_train_single_word(self):
        """Training on a single word should work."""
        tok = BPETokenizer(vocab_size=50)
        tok.train(["hello"])
        assert tok._trained is True
        assert len(tok.vocab) > 4  # special + characters


class TestBPEEncoding:
    """Tests for BPE encoding and decoding."""

    @pytest.fixture(autouse=True)
    def trained_tokenizer(self):
        self.tok = BPETokenizer(vocab_size=200)
        self.tok.train(CORPUS)

    @pytest.mark.unit
    def test_encode_returns_list_of_ints(self):
        ids = self.tok.encode("hello world")
        assert isinstance(ids, list)
        assert all(isinstance(i, int) for i in ids)

    @pytest.mark.unit
    def test_encode_nonempty(self):
        ids = self.tok.encode("the quick fox")
        assert len(ids) > 0

    @pytest.mark.unit
    def test_decode_produces_string(self):
        ids = self.tok.encode("hello world")
        text = self.tok.decode(ids)
        assert isinstance(text, str)
        assert len(text) > 0

    @pytest.mark.unit
    def test_roundtrip_known_word(self):
        """Words seen in training should round-trip cleanly."""
        original = "the"
        ids = self.tok.encode(original)
        decoded = self.tok.decode(ids)
        # Decoded should contain the original word
        assert "the" in decoded.strip()

    @pytest.mark.unit
    def test_encode_decode_corpus_words(self):
        """All words in training corpus should encode and decode reasonably."""
        test_words = ["hello", "world", "machine", "learning"]
        for word in test_words:
            ids = self.tok.encode(word)
            assert len(ids) > 0
            decoded = self.tok.decode(ids)
            assert len(decoded.strip()) > 0

    @pytest.mark.unit
    def test_encode_untrained_raises(self):
        """Encoding with untrained tokenizer should raise RuntimeError."""
        tok = BPETokenizer(vocab_size=100)
        with pytest.raises(RuntimeError, match="trained"):
            tok.encode("hello")

    @pytest.mark.unit
    def test_decode_untrained_raises(self):
        """Decoding with untrained tokenizer should raise RuntimeError."""
        tok = BPETokenizer(vocab_size=100)
        with pytest.raises(RuntimeError, match="trained"):
            tok.decode([1, 2, 3])

    @pytest.mark.unit
    def test_encode_multiword(self):
        """Multi-word input should produce more tokens than single word."""
        ids_single = self.tok.encode("the")
        ids_multi = self.tok.encode("the quick brown fox")
        assert len(ids_multi) > len(ids_single)

    @pytest.mark.unit
    def test_unknown_chars_get_unk_id(self):
        """Characters not in training vocab should map to UNK."""
        # Use characters very unlikely to appear in the English training corpus
        ids = self.tok.encode("\u4e16\u754c")  # Chinese characters
        unk_id = self.tok.vocab["<UNK>"]
        # At least some tokens should be UNK
        assert unk_id in ids


class TestBPESaveLoad:
    """Tests for tokenizer serialization."""

    @pytest.mark.unit
    def test_save_and_load(self, tmp_path):
        tok = BPETokenizer(vocab_size=100)
        tok.train(CORPUS)

        path = tmp_path / "tokenizer.json"
        tok.save(path)

        loaded = BPETokenizer.load(path)
        assert loaded._trained is True
        assert loaded.vocab_size == tok.vocab_size
        assert len(loaded.merges) == len(tok.merges)

        # Encoding should produce same results
        ids1 = tok.encode("hello world")
        ids2 = loaded.encode("hello world")
        assert ids1 == ids2

    @pytest.mark.unit
    def test_save_creates_file(self, tmp_path):
        tok = BPETokenizer(vocab_size=50)
        tok.train(CORPUS)

        path = tmp_path / "tok.json"
        assert not path.exists()
        tok.save(path)
        assert path.exists()
        assert path.stat().st_size > 0

    @pytest.mark.unit
    def test_load_preserves_merges(self, tmp_path):
        tok = BPETokenizer(vocab_size=100)
        tok.train(CORPUS)

        path = tmp_path / "tok.json"
        tok.save(path)
        loaded = BPETokenizer.load(path)

        for i, merge in enumerate(tok.merges):
            assert loaded.merges[i] == merge


class TestVocabulary:
    """Tests for the Vocabulary class."""

    @pytest.mark.unit
    def test_initial_special_tokens(self):
        vocab = Vocabulary()
        assert len(vocab) == 5  # PAD, UNK, BOS, EOS, MASK
        assert vocab.token_to_id("<PAD>") == 0
        assert vocab.token_to_id("<UNK>") == 1
        assert vocab.token_to_id("<BOS>") == 2
        assert vocab.token_to_id("<EOS>") == 3
        assert vocab.token_to_id("<MASK>") == 4

    @pytest.mark.unit
    def test_add_token(self):
        vocab = Vocabulary()
        idx = vocab.add("hello")
        assert idx == 5  # first non-special token
        assert vocab.token_to_id("hello") == 5
        assert vocab.id_to_token_str(5) == "hello"

    @pytest.mark.unit
    def test_add_duplicate_returns_same_id(self):
        vocab = Vocabulary()
        idx1 = vocab.add("hello")
        idx2 = vocab.add("hello")
        assert idx1 == idx2
        assert len(vocab) == 6  # 5 special + 1

    @pytest.mark.unit
    def test_unknown_token_returns_unk(self):
        vocab = Vocabulary()
        assert vocab.token_to_id("nonexistent") == 1  # UNK

    @pytest.mark.unit
    def test_unknown_id_returns_unk_string(self):
        vocab = Vocabulary()
        assert vocab.id_to_token_str(9999) == "<UNK>"

    @pytest.mark.unit
    def test_len_grows(self):
        vocab = Vocabulary()
        initial = len(vocab)
        vocab.add("a")
        vocab.add("b")
        vocab.add("c")
        assert len(vocab) == initial + 3


class TestMCPTools:
    """Tests for MCP tool wrappers."""

    @pytest.mark.unit
    def test_train_encode_decode_mcp(self):
        from codomyrmex.tokenizer.mcp_tools import (
            tokenizer_decode,
            tokenizer_encode,
            tokenizer_train,
        )

        # Train
        result = tokenizer_train(CORPUS, vocab_size=200)
        assert result["status"] == "success"
        assert result["vocab_size"] > 0
        assert result["num_merges"] > 0
        assert isinstance(result["sample_vocab"], list)

        # Encode
        enc = tokenizer_encode("hello world")
        assert enc["status"] == "success"
        assert len(enc["token_ids"]) > 0
        assert enc["num_tokens"] == len(enc["token_ids"])

        # Decode
        dec = tokenizer_decode(enc["token_ids"])
        assert dec["status"] == "success"
        assert len(dec["text"]) > 0

    @pytest.mark.unit
    def test_encode_before_train_returns_error(self):
        """Encoding with untrained module-level tokenizer should return error."""
        import codomyrmex.tokenizer.mcp_tools as mcp_mod

        # Reset global state
        mcp_mod._tokenizer = None

        result = mcp_mod.tokenizer_encode("hello")
        assert result["status"] == "error"
        assert "tokenizer_train" in result["message"]
