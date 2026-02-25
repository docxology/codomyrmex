"""
LLM RAG Module

Retrieval-Augmented Generation pipeline with document processing.
"""

__version__ = "0.1.0"

import hashlib
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar('T')


class DocumentType(Enum):
    """Supported document types."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    CODE = "code"


@dataclass
class Document:
    """A document for RAG processing."""
    id: str
    content: str
    doc_type: DocumentType = DocumentType.TEXT
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def content_hash(self) -> str:
        """Get hash of content."""
        return hashlib.md5(self.content.encode()).hexdigest()

    @classmethod
    def from_text(cls, text: str, doc_id: str | None = None, **metadata) -> "Document":
        """Create document from plain text."""
        return cls(
            id=doc_id or hashlib.md5(text.encode()).hexdigest()[:12],
            content=text,
            doc_type=DocumentType.TEXT,
            metadata=metadata,
        )

    @classmethod
    def from_file(cls, path: str, encoding: str = "utf-8") -> "Document":
        """Load document from file."""
        file_path = Path(path)
        content = file_path.read_text(encoding=encoding)

        # Detect type from extension
        ext = file_path.suffix.lower()
        doc_type = {
            ".md": DocumentType.MARKDOWN,
            ".html": DocumentType.HTML,
            ".htm": DocumentType.HTML,
            ".py": DocumentType.CODE,
            ".js": DocumentType.CODE,
            ".ts": DocumentType.CODE,
        }.get(ext, DocumentType.TEXT)

        return cls(
            id=file_path.stem,
            content=content,
            doc_type=doc_type,
            source=str(file_path),
            metadata={"filename": file_path.name},
        )


@dataclass
class Chunk:
    """A chunk of a document."""
    id: str
    content: str
    document_id: str
    sequence: int
    start_char: int
    end_char: int
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None

    @property
    def length(self) -> int:
        """Execute Length operations natively."""
        return len(self.content)


@dataclass
class RetrievalResult:
    """Result of a retrieval query."""
    chunk: Chunk
    score: float
    document: Document | None = None

    @property
    def content(self) -> str:
        """Execute Content operations natively."""
        return self.chunk.content


@dataclass
class GenerationContext:
    """Context for generation with retrieved content."""
    query: str
    retrieved: list[RetrievalResult]
    formatted_context: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def num_sources(self) -> int:
        """Execute Num Sources operations natively."""
        return len(self.retrieved)


class TextSplitter(ABC):
    """Base class for text splitting strategies."""

    @abstractmethod
    def split(self, document: Document) -> list[Chunk]:
        """Split document into chunks."""
        pass


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
        """Execute   Init   operations natively."""
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
            # Character-level split
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]

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
                    # Recursively split with next separator
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
            # Find actual position in document
            start = document.content.find(text, char_pos)
            if start == -1:
                start = char_pos
            end = start + len(text)

            chunks.append(Chunk(
                id=f"{document.id}_chunk_{i}",
                content=text,
                document_id=document.id,
                sequence=i,
                start_char=start,
                end_char=end,
                metadata=document.metadata.copy(),
            ))

            char_pos = max(char_pos, end - self.chunk_overlap)

        return chunks


class SentenceSplitter(TextSplitter):
    """Split text by sentences."""

    SENTENCE_ENDINGS = re.compile(r'(?<=[.!?])\s+')

    def __init__(
        self,
        sentences_per_chunk: int = 5,
        overlap_sentences: int = 1,
    ):
        """Execute   Init   operations natively."""
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences

    def split(self, document: Document) -> list[Chunk]:
        """Split document by sentences."""
        sentences = self.SENTENCE_ENDINGS.split(document.content)

        chunks = []
        i = 0
        chunk_num = 0

        while i < len(sentences):
            chunk_sentences = sentences[i:i + self.sentences_per_chunk]
            content = " ".join(chunk_sentences)

            # Find position
            start = document.content.find(chunk_sentences[0])
            end = start + len(content) if start >= 0 else 0

            chunks.append(Chunk(
                id=f"{document.id}_chunk_{chunk_num}",
                content=content,
                document_id=document.id,
                sequence=chunk_num,
                start_char=max(0, start),
                end_char=end,
                metadata=document.metadata.copy(),
            ))

            i += self.sentences_per_chunk - self.overlap_sentences
            chunk_num += 1

        return chunks


class VectorStore(ABC):
    """Base class for vector storage."""

    @abstractmethod
    def add(self, chunks: list[Chunk]) -> None:
        """Add chunks with embeddings."""
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        k: int = 5,
    ) -> list[RetrievalResult]:
        """Search for similar chunks."""
        pass

    @abstractmethod
    def delete(self, document_id: str) -> int:
        """Delete chunks by document ID."""
        pass


class InMemoryVectorStore(VectorStore):
    """Simple in-memory vector store."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        """Add chunks with embeddings."""
        for chunk in chunks:
            if chunk.embedding is not None:
                self._chunks.append(chunk)

    def search(
        self,
        query_embedding: list[float],
        k: int = 5,
    ) -> list[RetrievalResult]:
        """Search for similar chunks using cosine similarity."""
        results = []

        for chunk in self._chunks:
            if chunk.embedding is None:
                continue

            # Cosine similarity
            dot = sum(a * b for a, b in zip(query_embedding, chunk.embedding))
            mag1 = sum(x * x for x in query_embedding) ** 0.5
            mag2 = sum(x * x for x in chunk.embedding) ** 0.5

            if mag1 > 0 and mag2 > 0:
                score = dot / (mag1 * mag2)
                results.append(RetrievalResult(chunk=chunk, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

    def delete(self, document_id: str) -> int:
        """Delete chunks by document ID."""
        original = len(self._chunks)
        self._chunks = [c for c in self._chunks if c.document_id != document_id]
        return original - len(self._chunks)

    @property
    def count(self) -> int:
        """Execute Count operations natively."""
        return len(self._chunks)


class ContextFormatter:
    """Format retrieved results into context for LLM."""

    def __init__(
        self,
        template: str = "Source {i}:\n{content}\n",
        max_context_length: int = 4000,
        include_metadata: bool = False,
    ):
        """Execute   Init   operations natively."""
        self.template = template
        self.max_context_length = max_context_length
        self.include_metadata = include_metadata

    def format(self, results: list[RetrievalResult]) -> str:
        """Format results into context string."""
        parts = []
        total_length = 0

        for i, result in enumerate(results, 1):
            content = result.content
            if self.include_metadata and result.chunk.metadata:
                content = f"[{result.chunk.metadata}]\n{content}"

            part = self.template.format(i=i, content=content, score=result.score)

            if total_length + len(part) > self.max_context_length:
                # Truncate to fit
                remaining = self.max_context_length - total_length
                if remaining > 100:
                    parts.append(part[:remaining] + "...")
                break

            parts.append(part)
            total_length += len(part)

        return "\n".join(parts)


class RAGPipeline:
    """
    Complete RAG pipeline.

    Usage:
        # Setup
        pipeline = RAGPipeline(
            embedding_fn=lambda texts: [embed(t) for t in texts],
            vector_store=InMemoryVectorStore(),
        )

        # Index documents
        doc = Document.from_text("Your long document here...")
        pipeline.index_document(doc)

        # Query
        results = pipeline.retrieve("What is the main topic?", k=3)
        context = pipeline.build_context("What is the main topic?", k=3)

        # Generate (with your LLM)
        response = llm.complete(f"Context:\n{context.formatted_context}\n\nQuestion: {context.query}")
    """

    def __init__(
        self,
        embedding_fn: Callable[[list[str]], list[list[float]]],
        vector_store: VectorStore | None = None,
        text_splitter: TextSplitter | None = None,
        context_formatter: ContextFormatter | None = None,
    ):
        """Execute   Init   operations natively."""
        self.embedding_fn = embedding_fn
        self.vector_store = vector_store or InMemoryVectorStore()
        self.text_splitter = text_splitter or RecursiveTextSplitter()
        self.context_formatter = context_formatter or ContextFormatter()
        self._documents: dict[str, Document] = {}

    def index_document(self, document: Document) -> int:
        """
        Index a document for retrieval.

        Returns number of chunks indexed.
        """
        # Store document
        self._documents[document.id] = document

        # Split into chunks
        chunks = self.text_splitter.split(document)

        # Generate embeddings
        texts = [c.content for c in chunks]
        embeddings = self.embedding_fn(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        # Add to store
        self.vector_store.add(chunks)

        return len(chunks)

    def index_documents(self, documents: list[Document]) -> int:
        """Index multiple documents."""
        total = 0
        for doc in documents:
            total += self.index_document(doc)
        return total

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of retrieval results with scores
        """
        # Embed query
        query_embedding = self.embedding_fn([query])[0]

        # Search
        results = self.vector_store.search(query_embedding, k=k)

        # Attach documents
        for result in results:
            doc_id = result.chunk.document_id
            if doc_id in self._documents:
                result.document = self._documents[doc_id]

        return results

    def build_context(
        self,
        query: str,
        k: int = 5,
    ) -> GenerationContext:
        """
        Build generation context from retrieval.

        Args:
            query: The query
            k: Number of chunks to retrieve

        Returns:
            GenerationContext with formatted content
        """
        results = self.retrieve(query, k=k)
        formatted = self.context_formatter.format(results)

        return GenerationContext(
            query=query,
            retrieved=results,
            formatted_context=formatted,
            metadata={
                "num_chunks": len(results),
                "avg_score": sum(r.score for r in results) / len(results) if results else 0,
            },
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks."""
        if document_id in self._documents:
            del self._documents[document_id]
            self.vector_store.delete(document_id)
            return True
        return False

    @property
    def document_count(self) -> int:
        """Get number of indexed documents."""
        return len(self._documents)


# Prompt templates for RAG
RAG_PROMPT_TEMPLATE = """Use the following context to answer the question. If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {query}

Answer:"""


def create_rag_prompt(context: GenerationContext) -> str:
    """Create a RAG prompt from generation context."""
    return RAG_PROMPT_TEMPLATE.format(
        context=context.formatted_context,
        query=context.query,
    )


__all__ = [
    # Enums
    "DocumentType",
    # Data classes
    "Document",
    "Chunk",
    "RetrievalResult",
    "GenerationContext",
    # Splitters
    "TextSplitter",
    "RecursiveTextSplitter",
    "SentenceSplitter",
    # Vector stores
    "VectorStore",
    "InMemoryVectorStore",
    # Core
    "ContextFormatter",
    "RAGPipeline",
    # Templates
    "RAG_PROMPT_TEMPLATE",
    "create_rag_prompt",
]
