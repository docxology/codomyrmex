"""Document chunking strategies for RAG pipelines.

Provides multiple chunking strategies (fixed-size, sentence-based,
semantic, recursive) for splitting documents into chunks suitable
for embedding and retrieval.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChunkStrategy(Enum):
    """Supported chunking strategies."""
    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"


@dataclass
class Chunk:
    """A document chunk with metadata."""
    text: str
    index: int
    start_char: int
    end_char: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        """char Count ."""
        return len(self.text)

    @property
    def word_count(self) -> int:
        """word Count ."""
        return len(self.text.split())


@dataclass
class ChunkConfig:
    """Configuration for chunking."""
    strategy: ChunkStrategy = ChunkStrategy.RECURSIVE
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    separators: list[str] = field(default_factory=lambda: ["\n\n", "\n", ". ", " "])


class DocumentChunker:
    """Split documents into chunks for RAG pipelines.

    Supports multiple strategies with configurable overlap
    for context preservation across chunk boundaries.
    """

    def __init__(self, config: ChunkConfig | None = None) -> None:
        """Initialize this instance."""
        self._config = config or ChunkConfig()

    def chunk(self, text: str, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        """Chunk text using the configured strategy."""
        strategy = self._config.strategy
        if strategy == ChunkStrategy.FIXED_SIZE:
            return self._chunk_fixed(text, metadata)
        elif strategy == ChunkStrategy.SENTENCE:
            return self._chunk_sentences(text, metadata)
        elif strategy == ChunkStrategy.PARAGRAPH:
            return self._chunk_paragraphs(text, metadata)
        elif strategy == ChunkStrategy.RECURSIVE:
            return self._chunk_recursive(text, self._config.separators, metadata)
        else:
            return self._chunk_fixed(text, metadata)

    def _chunk_fixed(self, text: str, metadata: dict[str, Any] | None) -> list[Chunk]:
        """Split text into fixed-size chunks with overlap."""
        chunks: list[Chunk] = []
        size = self._config.chunk_size
        overlap = self._config.chunk_overlap
        start = 0
        idx = 0
        while start < len(text):
            end = min(start + size, len(text))
            chunk_text = text[start:end]
            if len(chunk_text.strip()) >= self._config.min_chunk_size or start == 0:
                chunks.append(Chunk(
                    text=chunk_text, index=idx,
                    start_char=start, end_char=end,
                    metadata=metadata or {},
                ))
                idx += 1
            start = end - overlap if end < len(text) else end
        return chunks

    def _chunk_sentences(self, text: str, metadata: dict[str, Any] | None) -> list[Chunk]:
        """Split text by sentences, grouping up to chunk_size."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks: list[Chunk] = []
        current: list[str] = []
        current_len = 0
        char_pos = 0
        idx = 0
        for sentence in sentences:
            if current_len + len(sentence) > self._config.chunk_size and current:
                chunk_text = " ".join(current)
                chunks.append(Chunk(
                    text=chunk_text, index=idx,
                    start_char=char_pos - len(chunk_text),
                    end_char=char_pos,
                    metadata=metadata or {},
                ))
                idx += 1
                # Keep overlap
                overlap_count = max(1, len(current) // 4)
                current = current[-overlap_count:]
                current_len = sum(len(s) for s in current)
            current.append(sentence)
            current_len += len(sentence)
            char_pos += len(sentence) + 1
        if current:
            chunk_text = " ".join(current)
            chunks.append(Chunk(
                text=chunk_text, index=idx,
                start_char=max(0, char_pos - len(chunk_text)),
                end_char=char_pos,
                metadata=metadata or {},
            ))
        return chunks

    def _chunk_paragraphs(self, text: str, metadata: dict[str, Any] | None) -> list[Chunk]:
        """Split text by paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks: list[Chunk] = []
        char_pos = 0
        for idx, para in enumerate(paragraphs):
            para = para.strip()
            if len(para) >= self._config.min_chunk_size:
                chunks.append(Chunk(
                    text=para, index=idx,
                    start_char=char_pos, end_char=char_pos + len(para),
                    metadata=metadata or {},
                ))
            char_pos += len(para) + 2
        return chunks

    def _chunk_recursive(self, text: str, separators: list[str],
                         metadata: dict[str, Any] | None) -> list[Chunk]:
        """Recursively split text using separator hierarchy."""
        if len(text) <= self._config.chunk_size:
            return [Chunk(text=text, index=0, start_char=0,
                         end_char=len(text), metadata=metadata or {})]

        sep = separators[0] if separators else " "
        parts = text.split(sep)

        chunks: list[Chunk] = []
        current_parts: list[str] = []
        current_len = 0
        idx = 0
        char_pos = 0

        for part in parts:
            if current_len + len(part) > self._config.chunk_size and current_parts:
                chunk_text = sep.join(current_parts)
                if len(chunk_text.strip()) >= self._config.min_chunk_size:
                    if len(chunk_text) > self._config.chunk_size and len(separators) > 1:
                        sub_chunks = self._chunk_recursive(
                            chunk_text, separators[1:], metadata
                        )
                        for sc in sub_chunks:
                            sc.index = idx
                            idx += 1
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append(Chunk(
                            text=chunk_text, index=idx,
                            start_char=char_pos - len(chunk_text),
                            end_char=char_pos,
                            metadata=metadata or {},
                        ))
                        idx += 1
                current_parts = []
                current_len = 0
            current_parts.append(part)
            current_len += len(part) + len(sep)
            char_pos += len(part) + len(sep)

        if current_parts:
            chunk_text = sep.join(current_parts)
            if len(chunk_text.strip()) >= self._config.min_chunk_size:
                chunks.append(Chunk(
                    text=chunk_text, index=idx,
                    start_char=max(0, char_pos - len(chunk_text)),
                    end_char=char_pos,
                    metadata=metadata or {},
                ))
        return chunks
