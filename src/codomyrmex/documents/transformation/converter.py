"""Document format conversion."""

import copy as py_copy

from codomyrmex.documents.exceptions import (
    DocumentConversionError,
    UnsupportedFormatError,
)
from codomyrmex.documents.models.document import Document, DocumentFormat
from codomyrmex.logging_monitoring.core.logger_config import get_logger

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
        # Handle structured to structured conversion directly if possible
        if document.format in [
            DocumentFormat.JSON,
            DocumentFormat.YAML,
            DocumentFormat.CSV,
        ]:
            if target_format in [DocumentFormat.JSON, DocumentFormat.YAML]:
                if isinstance(document.content, (dict, list)):
                    converted_content = py_copy.deepcopy(document.content)
                    return Document(
                        content=converted_content,
                        format=target_format,
                        file_path=document.file_path,
                        encoding=document.encoding,
                        metadata=document.metadata.copy(),
                    )

        # Get content as string for basic conversion
        content_str = document.get_content_as_string()

        # Convert based on target format
        if target_format == DocumentFormat.MARKDOWN:
            converted_content = _to_markdown(content_str, document.format)
        elif target_format == DocumentFormat.JSON:
            converted_content = _to_json(content_str, document.format)
        elif target_format == DocumentFormat.YAML:
            converted_content = _to_yaml(content_str, document.format)
        elif target_format == DocumentFormat.TEXT:
            if document.format == DocumentFormat.HTML:
                from codomyrmex.documents.formats.html_handler import strip_html_tags

                converted_content = strip_html_tags(content_str)
            else:
                converted_content = content_str
        elif target_format == DocumentFormat.HTML:
            converted_content = _to_html(content_str, document.format)
        else:
            raise UnsupportedFormatError(
                f"Conversion to {target_format.value} not yet implemented",
                format=target_format.value,
            )

        # Create new document with copied metadata
        new_metadata = document.metadata.copy()

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
        if isinstance(e, (DocumentConversionError, UnsupportedFormatError)):
            raise
        raise DocumentConversionError(f"Failed to convert document: {str(e)}") from e


def _to_markdown(content: str, source_format: DocumentFormat) -> str:
    """Convert content to markdown."""
    if source_format == DocumentFormat.HTML:
        try:
            from markdownify import markdownify as md

            return md(content, heading_style="ATX", strip=["script", "style"])
        except ImportError:
            # Fallback: strip HTML tags for basic conversion
            import re

            clean = re.sub(r"<[^>]+>", "", content)
            return clean.strip()
    elif source_format == DocumentFormat.TEXT:
        return content
    else:
        return content


def _to_json(content: str, source_format: DocumentFormat) -> dict | list:
    """Convert content to JSON."""
    if source_format == DocumentFormat.YAML:
        import yaml

        return yaml.safe_load(content) or {}
    elif source_format == DocumentFormat.JSON:
        import json

        return json.loads(content)
    elif source_format == DocumentFormat.CSV:
        import json

        try:
            # If it's already a JSON string (from get_content_as_string for a list), parse it as JSON
            return json.loads(content)
        except json.JSONDecodeError:
            import csv
            import io

            f = io.StringIO(content)
            reader = csv.DictReader(f)
            return list(reader)
    else:
        # Convert text to JSON object
        return {"content": content}


def _to_yaml(content: str, source_format: DocumentFormat) -> dict | list:
    """Convert content to YAML."""
    if source_format == DocumentFormat.JSON:
        import json

        return json.loads(content)
    elif source_format == DocumentFormat.YAML:
        import yaml

        return yaml.safe_load(content) or {}
    elif source_format == DocumentFormat.CSV:
        return _to_json(content, source_format)
    else:
        # Convert text to YAML object
        return {"content": content}


def _to_html(content: str, source_format: DocumentFormat) -> str:
    """Convert content to HTML."""
    if source_format == DocumentFormat.MARKDOWN:
        try:
            import markdown

            return markdown.markdown(content)
        except ImportError:
            return f"<html><body><pre>{content}</pre></body></html>"
    else:
        return f"<html><body><pre>{content}</pre></body></html>"
