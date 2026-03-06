"""RAG data models: Document, Chunk, RetrievalResult, GenerationContext."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


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
        """Length."""
        return len(self.content)


@dataclass
class RetrievalResult:
    """Result of a retrieval query."""

    chunk: Chunk
    score: float
    document: Document | None = None

    @property
    def content(self) -> str:
        """Content."""
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
        return len(self.retrieved)
