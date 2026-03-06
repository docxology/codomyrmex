"""Text splitting strategies for RAG chunking."""

import re
from abc import ABC, abstractmethod

from .models import Chunk, Document


class TextSplitter(ABC):
    """Base class for text splitting strategies."""

    @abstractmethod
    def split(self, document: Document) -> list[Chunk]:
        """Split document into chunks."""


class RecursiveTextSplitter(TextSplitter):
    """
    Split text recursively by separators.

    Tries larger separators first, falls back to smaller.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text."""
        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            return [
                text[i : i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
            ]

        parts = text.split(separator)
        chunks = []
        current_chunk = ""

        for part in parts:
            test_chunk = current_chunk + separator + part if current_chunk else part

            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                if len(part) > self.chunk_size:
                    sub_chunks = self._split_text(part, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def split(self, document: Document) -> list[Chunk]:
        """Split document into chunks."""
        text_chunks = self._split_text(document.content, self.separators)

        chunks = []
        char_pos = 0

        for i, text in enumerate(text_chunks):
            start = document.content.find(text, char_pos)
            if start == -1:
                start = char_pos
            end = start + len(text)

            chunks.append(
                Chunk(
                    id=f"{document.id}_chunk_{i}",
                    content=text,
                    document_id=document.id,
                    sequence=i,
                    start_char=start,
                    end_char=end,
                    metadata=document.metadata.copy(),
                )
            )

            char_pos = max(char_pos, end - self.chunk_overlap)

        return chunks


class SentenceSplitter(TextSplitter):
    """Split text by sentences."""

    SENTENCE_ENDINGS = re.compile(r"(?<=[.!?])\s+")

    def __init__(
        self,
        sentences_per_chunk: int = 5,
        overlap_sentences: int = 1,
    ):
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences

    def split(self, document: Document) -> list[Chunk]:
        """Split document by sentences."""
        sentences = self.SENTENCE_ENDINGS.split(document.content)

        chunks = []
        i = 0
        chunk_num = 0

        while i < len(sentences):
            chunk_sentences = sentences[i : i + self.sentences_per_chunk]
            content = " ".join(chunk_sentences)

            start = document.content.find(chunk_sentences[0])
            end = start + len(content) if start >= 0 else 0

            chunks.append(
                Chunk(
                    id=f"{document.id}_chunk_{chunk_num}",
                    content=content,
                    document_id=document.id,
                    sequence=chunk_num,
                    start_char=max(0, start),
                    end_char=end,
                    metadata=document.metadata.copy(),
                )
            )

            i += self.sentences_per_chunk - self.overlap_sentences
            chunk_num += 1

        return chunks
