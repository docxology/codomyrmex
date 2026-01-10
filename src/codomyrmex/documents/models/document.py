"""Document model for Codomyrmex Documents module.

Defines core document types and formats.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DocumentType(Enum):
    """Types of documents."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    CODE = "code"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"


class DocumentFormat(Enum):
    """Document file formats."""
    TXT = "txt"
    MD = "md"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    PY = "py"
    JS = "js"


@dataclass
class DocumentMetadata:
    """Document metadata."""
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """Represents a document."""
    id: str
    content: str
    document_type: DocumentType
    format: DocumentFormat
    file_path: Optional[str] = None
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "document_type": self.document_type.value,
            "format": self.format.value,
            "file_path": self.file_path,
        }
