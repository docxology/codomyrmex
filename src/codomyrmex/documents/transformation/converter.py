"""Document format conversion."""

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..exceptions import DocumentConversionError, UnsupportedFormatError
from ..models.document import Document, DocumentFormat

logger = get_logger(__name__)


def convert_document(document: Document, target_format: DocumentFormat) -> Document:
    """
    Convert a document to a different format.
    
    Args:
        document: Document to convert
        target_format: Target format
    
    Returns:
        New Document in target format
    
    Raises:
        DocumentConversionError: If conversion fails
        UnsupportedFormatError: If conversion is not supported
    """
    if document.format == target_format:
        logger.debug("Document already in target format")
        return document
    
    try:
        # Get content as string first
        content_str = document.get_content_as_string()
        
        # Convert based on target format
        if target_format == DocumentFormat.MARKDOWN:
            # Convert to markdown (basic conversion)
            converted_content = _to_markdown(content_str, document.format)
        elif target_format == DocumentFormat.JSON:
            converted_content = _to_json(content_str, document.format)
        elif target_format == DocumentFormat.YAML:
            converted_content = _to_yaml(content_str, document.format)
        elif target_format == DocumentFormat.TEXT:
            converted_content = content_str
        else:
            raise UnsupportedFormatError(
                f"Conversion to {target_format.value} not yet implemented",
                format=target_format.value
            )
        
        # Create new document with copied metadata
        if document.metadata is not None and hasattr(document.metadata, 'copy'):
            new_metadata = document.metadata.copy()
        else:
            new_metadata = document.metadata

        converted_doc = Document(
            content=converted_content,
            format=target_format,
            file_path=document.file_path,
            encoding=document.encoding,
            metadata=new_metadata,
        )
        
        return converted_doc
        
    except Exception as e:
        logger.error(f"Error converting document: {e}")
        raise DocumentConversionError(f"Failed to convert document: {str(e)}") from e


def _to_markdown(content: str, source_format: DocumentFormat) -> str:
    """Convert content to markdown."""
    if source_format == DocumentFormat.HTML:
        # Basic HTML to markdown (would need markdownify or similar)
        return content  # Placeholder
    elif source_format == DocumentFormat.TEXT:
        # Text to markdown (wrap in code block or preserve)
        return content
    else:
        return content


def _to_json(content: str, source_format: DocumentFormat) -> dict:
    """Convert content to JSON."""
    if source_format == DocumentFormat.YAML:
        import yaml
        return yaml.safe_load(content) or {}
    elif source_format == DocumentFormat.JSON:
        import json
        return json.loads(content)
    else:
        # Convert text to JSON object
        return {"content": content}


def _to_yaml(content: str, source_format: DocumentFormat) -> dict:
    """Convert content to YAML."""
    if source_format == DocumentFormat.JSON:
        import json
        return json.loads(content)
    elif source_format == DocumentFormat.YAML:
        import yaml
        return yaml.safe_load(content) or {}
    else:
        # Convert text to YAML object
        return {"content": content}



