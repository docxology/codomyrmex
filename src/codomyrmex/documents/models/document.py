"""Document model for Codomyrmex Documents module.

Defines core document types and formats.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DocumentType(Enum):
    """Types of documents."""
    TEXT = "text"
    MARKUP = "markup"
    STRUCTURED = "structured"
    BINARY = "binary"
    CODE = "code"


class DocumentFormat(Enum):
    """Document file formats."""
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    PDF = "pdf"
    RTF = "rtf"
    DOCX = "docx"
    XLSX = "xlsx"
    PY = "py"
    JS = "js"


# Mapping from format to document type
_FORMAT_TYPE_MAP = {
    DocumentFormat.MARKDOWN: DocumentType.MARKUP,
    DocumentFormat.HTML: DocumentType.MARKUP,
    DocumentFormat.XML: DocumentType.MARKUP,
    DocumentFormat.RTF: DocumentType.MARKUP,
    DocumentFormat.TEXT: DocumentType.TEXT,
    DocumentFormat.JSON: DocumentType.STRUCTURED,
    DocumentFormat.YAML: DocumentType.STRUCTURED,
    DocumentFormat.CSV: DocumentType.STRUCTURED,
    DocumentFormat.XLSX: DocumentType.STRUCTURED,
    DocumentFormat.PDF: DocumentType.BINARY,
    DocumentFormat.DOCX: DocumentType.BINARY,
    DocumentFormat.PY: DocumentType.CODE,
    DocumentFormat.JS: DocumentType.CODE,
}


@dataclass
class Document:
    """Represents a document."""
    content: Any
    format: DocumentFormat
    file_path: Any | None = None
    encoding: str | None = None
    metadata: Any = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    document_type: DocumentType | None = None
    created_at: datetime | None = field(default_factory=datetime.now)
    modified_at: datetime | None = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.document_type is None:
            self.document_type = _FORMAT_TYPE_MAP.get(self.format, DocumentType.TEXT)

    @property
    def type(self) -> DocumentType:
        """Shorthand for document_type."""
        return self.document_type

    def get_content_as_string(self) -> str:
        """Return content as a string."""
        if isinstance(self.content, str):
            return self.content
        if isinstance(self.content, dict):
            return json.dumps(self.content, ensure_ascii=False)
        if isinstance(self.content, (list, tuple)):
            return json.dumps(self.content, ensure_ascii=False)
        if isinstance(self.content, bytes):
            return self.content.decode(self.encoding or "utf-8", errors="replace")
        return str(self.content)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        content_preview = self.get_content_as_string()
        if len(content_preview) > 100:
            content_preview = content_preview[:100] + "..."
        return {
            "id": self.id,
            "content": content_preview,
            "document_type": self.document_type.value if self.document_type else None,
            "format": self.format.value,
            "file_path": str(self.file_path) if self.file_path else None,
            "encoding": self.encoding,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
        }
