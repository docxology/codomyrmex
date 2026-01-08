"""Document splitting operations."""

from typing import List

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..exceptions import DocumentConversionError
from ..models.document import Document

logger = get_logger(__name__)


def split_document(document: Document, criteria: dict) -> List[Document]:
    """
    Split a document into multiple documents based on criteria.
    
    Args:
        document: Document to split
        criteria: Split criteria (e.g., {"method": "by_pages", "pages": 10})
    
    Returns:
        List of split documents
    
    Raises:
        DocumentConversionError: If splitting fails
    """
    method = criteria.get("method", "by_sections")
    
    try:
        if method == "by_sections":
            return _split_by_sections(document, criteria)
        elif method == "by_size":
            return _split_by_size(document, criteria)
        elif method == "by_pages" and document.format.value == "pdf":
            return _split_by_pages(document, criteria)
        else:
            # Default: split by lines
            return _split_by_lines(document, criteria)
            
    except Exception as e:
        logger.error(f"Error splitting document: {e}")
        raise DocumentConversionError(f"Failed to split document: {str(e)}") from e


def _split_by_sections(document: Document, criteria: dict) -> List[Document]:
    """Split document by sections (markdown headers, etc.)."""
    content = document.get_content_as_string()
    sections = []
    current_section = []
    
    for line in content.split('\n'):
        if line.strip().startswith('#'):
            if current_section:
                sections.append('\n'.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    
    if current_section:
        sections.append('\n'.join(current_section))
    
    split_docs = []
    for i, section_content in enumerate(sections):
        split_doc = Document(
            content=section_content,
            format=document.format,
            metadata={**document.metadata, "section": i} if document.metadata else {"section": i},
        )
        split_docs.append(split_doc)
    
    return split_docs


def _split_by_size(document: Document, criteria: dict) -> List[Document]:
    """Split document by size (characters)."""
    max_size = criteria.get("max_size", 10000)
    content = document.get_content_as_string()
    
    split_docs = []
    for i in range(0, len(content), max_size):
        chunk = content[i:i + max_size]
        split_doc = Document(
            content=chunk,
            format=document.format,
            metadata={**document.metadata, "chunk": i // max_size} if document.metadata else {"chunk": i // max_size},
        )
        split_docs.append(split_doc)
    
    return split_docs


def _split_by_pages(document: Document, criteria: dict) -> List[Document]:
    """Split PDF document by pages."""
    # This would require PDF-specific handling
    # For now, return single document
    return [document]


def _split_by_lines(document: Document, criteria: dict) -> List[Document]:
    """Split document by number of lines."""
    lines_per_chunk = criteria.get("lines_per_chunk", 100)
    content = document.get_content_as_string()
    lines = content.split('\n')
    
    split_docs = []
    for i in range(0, len(lines), lines_per_chunk):
        chunk_lines = lines[i:i + lines_per_chunk]
        chunk_content = '\n'.join(chunk_lines)
        split_doc = Document(
            content=chunk_content,
            format=document.format,
            metadata={**document.metadata, "chunk": i // lines_per_chunk} if document.metadata else {"chunk": i // lines_per_chunk},
        )
        split_docs.append(split_doc)
    
    return split_docs



