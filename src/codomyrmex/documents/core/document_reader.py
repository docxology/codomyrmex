"""Document reading operations."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentReadError, UnsupportedFormatError
from ..models.document import Document, DocumentFormat
from ..utils.encoding_detector import detect_encoding
from ..utils.mime_type_detector import detect_format_from_path

logger = get_logger(__name__)


class DocumentReader:
    """Unified document reader supporting multiple formats."""
    
    def __init__(self):
        """Brief description of __init__.
        
        Args:
            self : Description of self
        
            Returns: Description of return value
        """
"""
        self.config = get_config()
    
    def read(
        self,
        file_path: str | Path,
        format: Optional[DocumentFormat] = None,
        encoding: Optional[str] = None,
    ) -> Document:
        """
        Read a document from a file.
        
        Args:
            file_path: Path to the document file
            format: Optional format hint (auto-detected if not provided)
            encoding: Optional encoding hint (auto-detected if not provided)
        
        Returns:
            Document object with content and metadata
        
        Raises:
            DocumentReadError: If reading fails
            UnsupportedFormatError: If format is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocumentReadError(f"File not found: {file_path}", file_path=str(file_path))
        
        # Detect format if not provided
        if format is None:
            format = self._detect_format(file_path)
        
        # Detect encoding if not provided
        if encoding is None:
            encoding = detect_encoding(file_path) or self.config.default_encoding
        
        # Read based on format
        try:
            if format == DocumentFormat.MARKDOWN:
                from ..formats.markdown_handler import read_markdown
                content = read_markdown(str(file_path), encoding=encoding)
            elif format == DocumentFormat.JSON:
                from ..formats.json_handler import read_json
                content = read_json(str(file_path), encoding=encoding)
            elif format == DocumentFormat.YAML:
                from ..formats.yaml_handler import read_yaml
                content = read_yaml(str(file_path), encoding=encoding)
            elif format == DocumentFormat.PDF:
                from ..formats.pdf_handler import read_pdf
                pdf_doc = read_pdf(str(file_path))
                content = pdf_doc
            elif format == DocumentFormat.TEXT:
                from ..formats.text_handler import read_text
                content = read_text(str(file_path), encoding=encoding)
            else:
                raise UnsupportedFormatError(
                    f"Format {format.value} not yet implemented",
                    format=format.value
                )
            
            # Create document object
            document = Document(
                content=content,
                format=format,
                file_path=file_path,
                encoding=encoding,
            )
            
            # Extract metadata
            from ..metadata.extractor import extract_metadata
            metadata = extract_metadata(str(file_path))
            document.metadata = metadata
            
            return document
            
        except Exception as e:
            logger.error(f"Error reading document {file_path}: {e}")
            raise DocumentReadError(
                f"Failed to read document: {str(e)}",
                file_path=str(file_path)
            ) from e
    
    def _detect_format(self, file_path: Path) -> DocumentFormat:
        """Detect document format from file path."""
        format_str = detect_format_from_path(file_path)
        
        format_mapping = {
            "markdown": DocumentFormat.MARKDOWN,
            "json": DocumentFormat.JSON,
            "yaml": DocumentFormat.YAML,
            "yml": DocumentFormat.YAML,
            "pdf": DocumentFormat.PDF,
            "txt": DocumentFormat.TEXT,
            "text": DocumentFormat.TEXT,
            "html": DocumentFormat.HTML,
            "xml": DocumentFormat.XML,
            "csv": DocumentFormat.CSV,
        }
        
        return format_mapping.get(format_str.lower(), DocumentFormat.TEXT)


def read_document(
    file_path: str | Path,
    format: Optional[DocumentFormat] = None,
    encoding: Optional[str] = None,
) -> Document:
    """
    Read a document from a file.
    
    Convenience function that creates a DocumentReader and reads the document.
    
    Args:
        file_path: Path to the document file
        format: Optional format hint
        encoding: Optional encoding hint
    
    Returns:
        Document object
    """
    reader = DocumentReader()
    return reader.read(file_path, format=format, encoding=encoding)

