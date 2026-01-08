from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

from codomyrmex.logging_monitoring import get_logger




"""Document model definitions."""
























































"""Document model definitions."""




"""Core functionality module

This module provides document functionality including:
- 3 functions: __post_init__, type, get_content_as_string
- 3 classes: DocumentType, DocumentFormat, Document

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
class DocumentType(Enum):
    """Types of documents."""
    TEXT = "text"
    STRUCTURED = "structured"
    BINARY = "binary"
    MARKUP = "markup"


class DocumentFormat(Enum):
    """Supported document formats."""
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    HTML = "html"
    TEXT = "text"
    RTF = "rtf"
    DOCX = "docx"
    XLSX = "xlsx"


@dataclass
class Document:
    """Represents a document with content and metadata."""
    
    content: Any  # Can be str, dict, bytes depending on format
    format: DocumentFormat
    file_path: Optional[Path] = None
    encoding: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    version: Optional[str] = None
    
    def __post_init__(self):
    """Brief description of __post_init__.

Args:
    self : Description of self

    Returns: Description of return value
"""
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.modified_at is None:
            self.modified_at = datetime.now()
    
    @property
    def type(self) -> DocumentType:
        """Get the document type based on format."""
        type_mapping = {
            DocumentFormat.MARKDOWN: DocumentType.MARKUP,
            DocumentFormat.HTML: DocumentType.MARKUP,
            DocumentFormat.XML: DocumentType.MARKUP,
            DocumentFormat.JSON: DocumentType.STRUCTURED,
            DocumentFormat.YAML: DocumentType.STRUCTURED,
            DocumentFormat.CSV: DocumentType.STRUCTURED,
            DocumentFormat.PDF: DocumentType.BINARY,
            DocumentFormat.DOCX: DocumentType.BINARY,
            DocumentFormat.XLSX: DocumentType.BINARY,
            DocumentFormat.RTF: DocumentType.BINARY,
            DocumentFormat.TEXT: DocumentType.TEXT,
        }
        return type_mapping.get(self.format, DocumentType.TEXT)
    
    def get_content_as_string(self) -> str:
        """Get content as string, converting if necessary."""
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, dict):
            return json.dumps(self.content, indent=2)
        elif isinstance(self.content, bytes):
            encoding = self.encoding or "utf-8"
            return self.content.decode(encoding)
        else:
            return str(self.content)



