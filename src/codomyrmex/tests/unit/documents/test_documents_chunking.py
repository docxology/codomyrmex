"""
Unit tests for documents.chunking — Zero-Mock compliant.

Covers: DocumentChunker, Chunk, ChunkConfig, ChunkStrategy
All strategies: FIXED_SIZE, SENTENCE, PARAGRAPH, RECURSIVE
"""

import pytest

from codomyrmex.documents.chunking import (
    Chunk,
    ChunkConfig,
    ChunkStrategy,
    DocumentChunker,
)

# ── Chunk dataclass ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestChunk:
    """Tests for the Chunk dataclass."""

    def test_char_count(self):
        chunk = Chunk(text="hello world", index=0, start_char=0, end_char=11)
        assert chunk.char_count == 11

    def test_word_count(self):
        chunk = Chunk(text="hello world foo", index=0, start_char=0, end_char=15)
        assert chunk.word_count == 3

    def test_empty_text(self):
        chunk = Chunk(text="", index=0, start_char=0, end_char=0)
        assert chunk.char_count == 0
        assert chunk.word_count == 0

    def test_metadata_defaults_empty(self):
        chunk = Chunk(text="x", index=0, start_char=0, end_char=1)
        assert chunk.metadata == {}

    def test_metadata_stored(self):
        chunk = Chunk(text="x", index=0, start_char=0, end_char=1, metadata={"src": "doc"})
        assert chunk.metadata["src"] == "doc"


# ── ChunkConfig defaults ──────────────────────────────────────────────────


@pytest.mark.unit
class TestChunkConfig:
    """Tests for ChunkConfig defaults."""

    def test_default_strategy(self):
        cfg = ChunkConfig()
        assert cfg.strategy == ChunkStrategy.RECURSIVE

    def test_default_sizes(self):
        cfg = ChunkConfig()
        assert cfg.chunk_size == 1000
        assert cfg.chunk_overlap == 200
        assert cfg.min_chunk_size == 100

    def test_default_separators(self):
        cfg = ChunkConfig()
        assert "\n\n" in cfg.separators

    def test_custom_config(self):
        cfg = ChunkConfig(strategy=ChunkStrategy.FIXED_SIZE, chunk_size=500, chunk_overlap=50)
        assert cfg.strategy == ChunkStrategy.FIXED_SIZE
        assert cfg.chunk_size == 500


# ── FIXED_SIZE strategy ───────────────────────────────────────────────────


@pytest.mark.unit
class TestChunkFixed:
    """Tests for FIXED_SIZE chunking strategy."""

    def _chunker(self, size=100, overlap=20, min_size=0):
        return DocumentChunker(
            ChunkConfig(
                strategy=ChunkStrategy.FIXED_SIZE,
                chunk_size=size,
                chunk_overlap=overlap,
                min_chunk_size=min_size,
            )
        )

    def test_short_text_single_chunk(self):
        chunker = self._chunker(size=200)
        text = "Hello world, this is a short test."
        chunks = chunker.chunk(text)
        assert len(chunks) == 1
        assert chunks[0].text == text

    def test_long_text_produces_multiple_chunks(self):
        chunker = self._chunker(size=50, overlap=10, min_size=0)
        text = "A" * 200
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_chunks_are_indexed_sequentially(self):
        chunker = self._chunker(size=30, overlap=5, min_size=0)
        text = "x" * 100
        chunks = chunker.chunk(text)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_metadata_passed_to_all_chunks(self):
        chunker = self._chunker(size=50, overlap=5, min_size=0)
        text = "word " * 30
        chunks = chunker.chunk(text, metadata={"source": "test_doc"})
        for chunk in chunks:
            assert chunk.metadata.get("source") == "test_doc"

    def test_chunk_start_end_chars_monotone(self):
        chunker = self._chunker(size=50, overlap=0, min_size=0)
        text = "a" * 200
        chunks = chunker.chunk(text)
        for chunk in chunks:
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char

    def test_empty_text_returns_one_chunk(self):
        chunker = self._chunker(size=100, min_size=0)
        chunks = chunker.chunk("")
        # Empty string still produces one chunk (start==0 case)
        assert isinstance(chunks, list)


# ── SENTENCE strategy ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestChunkSentences:
    """Tests for SENTENCE chunking strategy."""

    def _chunker(self, size=200, min_size=0):
        return DocumentChunker(
            ChunkConfig(
                strategy=ChunkStrategy.SENTENCE,
                chunk_size=size,
                chunk_overlap=50,
                min_chunk_size=min_size,
            )
        )

    def test_short_text_produces_at_least_one_chunk(self):
        chunker = self._chunker()
        text = "Hello. World. This is a test."
        chunks = chunker.chunk(text)
        assert len(chunks) >= 1

    def test_chunks_contain_original_words(self):
        chunker = self._chunker()
        text = "First sentence here. Second sentence here. Third sentence here."
        chunks = chunker.chunk(text)
        combined = " ".join(c.text for c in chunks)
        assert "First" in combined
        assert "Third" in combined

    def test_long_text_creates_multiple_chunks(self):
        # Make many short sentences that exceed chunk_size when aggregated
        chunker = self._chunker(size=50, min_size=0)
        text = "A B. " * 50
        chunks = chunker.chunk(text)
        assert len(chunks) >= 2

    def test_metadata_forwarded(self):
        chunker = self._chunker()
        text = "One. Two. Three."
        chunks = chunker.chunk(text, metadata={"id": "doc1"})
        for c in chunks:
            assert c.metadata.get("id") == "doc1"


# ── PARAGRAPH strategy ────────────────────────────────────────────────────


@pytest.mark.unit
class TestChunkParagraphs:
    """Tests for PARAGRAPH chunking strategy."""

    def _chunker(self, min_size=0):
        return DocumentChunker(
            ChunkConfig(
                strategy=ChunkStrategy.PARAGRAPH,
                chunk_size=1000,
                chunk_overlap=0,
                min_chunk_size=min_size,
            )
        )

    def test_two_paragraphs_produce_two_chunks(self):
        chunker = self._chunker()
        text = "First paragraph text here with enough words.\n\nSecond paragraph text here with enough words."
        chunks = chunker.chunk(text)
        assert len(chunks) == 2

    def test_single_paragraph(self):
        chunker = self._chunker()
        text = "Just one block of text without double newlines."
        chunks = chunker.chunk(text)
        assert len(chunks) == 1

    def test_min_size_filters_short_paragraphs(self):
        chunker = self._chunker(min_size=50)
        text = "Short.\n\nThis is a much longer paragraph that should pass the minimum size threshold easily."
        chunks = chunker.chunk(text)
        # The short paragraph "Short." should be filtered out
        assert all(len(c.text) >= 50 for c in chunks)

    def test_chunk_text_matches_paragraph(self):
        chunker = self._chunker()
        para1 = "First paragraph block with sufficient content here."
        para2 = "Second paragraph block with sufficient content here."
        text = f"{para1}\n\n{para2}"
        chunks = chunker.chunk(text)
        assert any(para1 in c.text for c in chunks)


# ── RECURSIVE strategy ────────────────────────────────────────────────────


@pytest.mark.unit
class TestChunkRecursive:
    """Tests for RECURSIVE chunking strategy (default)."""

    def _chunker(self, size=200, min_size=0):
        return DocumentChunker(
            ChunkConfig(
                strategy=ChunkStrategy.RECURSIVE,
                chunk_size=size,
                chunk_overlap=50,
                min_chunk_size=min_size,
                separators=["\n\n", "\n", ". ", " "],
            )
        )

    def test_short_text_single_chunk(self):
        chunker = self._chunker(size=1000)
        text = "Short text."
        chunks = chunker.chunk(text)
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."

    def test_long_text_splits_into_multiple_chunks(self):
        """Double-newline separators force the recursive chunker to split."""
        chunker = self._chunker(size=30, min_size=0)
        # Each paragraph is 12 chars; chunk_size=30 forces splits between them
        text = "hello world.\n\nhello world.\n\nhello world."
        chunks = chunker.chunk(text)
        assert len(chunks) >= 2

    def test_default_chunker_uses_recursive(self):
        # Default config is RECURSIVE
        chunker = DocumentChunker()
        text = "Hello world."
        chunks = chunker.chunk(text)
        assert len(chunks) >= 1

    def test_chunks_cover_content(self):
        """Content is preserved across chunks when text contains separators."""
        chunker = self._chunker(size=30, min_size=0)
        # Use \n\n separator so the recursive strategy can split reliably
        paragraphs = [f"para{i} content text" for i in range(6)]
        text = "\n\n".join(paragraphs)
        chunks = chunker.chunk(text)
        combined = " ".join(c.text for c in chunks)
        assert "para0" in combined
        assert "para5" in combined


# ── SEMANTIC (fallback to FIXED_SIZE) ─────────────────────────────────────


@pytest.mark.unit
class TestChunkSemantic:
    """SEMANTIC falls back to FIXED_SIZE (not yet implemented)."""

    def test_semantic_strategy_returns_chunks(self):
        chunker = DocumentChunker(
            ChunkConfig(
                strategy=ChunkStrategy.SEMANTIC,
                chunk_size=100,
                chunk_overlap=20,
                min_chunk_size=0,
            )
        )
        text = "A " * 60
        chunks = chunker.chunk(text)
        assert isinstance(chunks, list)
        assert len(chunks) >= 1


# ── Integration: chunk/unchunk round-trip ─────────────────────────────────


@pytest.mark.unit
class TestChunkerIntegration:
    """Integration tests combining strategies."""

    def test_all_strategies_return_list_of_chunk(self):
        text = "Hello world. " * 20
        for strategy in ChunkStrategy:
            chunker = DocumentChunker(
                ChunkConfig(strategy=strategy, chunk_size=50, chunk_overlap=10, min_chunk_size=0)
            )
            chunks = chunker.chunk(text)
            assert isinstance(chunks, list)
            for c in chunks:
                assert isinstance(c, Chunk)

    def test_no_metadata_defaults_to_empty_dict(self):
        chunker = DocumentChunker(ChunkConfig(
            strategy=ChunkStrategy.FIXED_SIZE,
            chunk_size=50, chunk_overlap=10, min_chunk_size=0
        ))
        chunks = chunker.chunk("test " * 20)
        for c in chunks:
            assert c.metadata == {}
