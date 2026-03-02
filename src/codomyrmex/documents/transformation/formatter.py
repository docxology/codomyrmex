"""Document formatting utilities."""

from codomyrmex.documents.models.document import Document
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


def format_document(document: Document, style: str = "default") -> Document:
    """
    Format a document according to a style.

    Args:
        document: Document to format
        style: Formatting style (default, compact, pretty)

    Returns:
        Formatted Document
    """
    if style == "default":
        return document

    try:
        if document.format.value == "json":
            return _format_json(document, style)
        elif document.format.value == "yaml":
            return _format_yaml(document, style)
        else:
            return document
    except Exception as e:
        logger.warning(f"Formatting failed: {e}, returning original document")
        return document


def _format_json(document: Document, style: str) -> Document:
    """Format JSON document."""
    import json

    if isinstance(document.content, dict):
        data = document.content
    else:
        data = json.loads(document.get_content_as_string())

    if style == "compact":
        formatted_content = json.dumps(data, separators=(',', ':'))
    elif style == "pretty":
        formatted_content = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        formatted_content = json.dumps(data, indent=2)

    formatted_doc = Document(
        content=formatted_content,
        format=document.format,
        file_path=document.file_path,
        encoding=document.encoding,
        metadata=document.metadata,
    )

    return formatted_doc


def _format_yaml(document: Document, style: str) -> Document:
    """Format YAML document."""
    import yaml

    if isinstance(document.content, dict):
        data = document.content
    else:
        data = yaml.safe_load(document.get_content_as_string()) or {}

    if style == "compact":
        formatted_content = yaml.dump(data, default_flow_style=True)
    else:
        formatted_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)

    formatted_doc = Document(
        content=formatted_content,
        format=document.format,
        file_path=document.file_path,
        encoding=document.encoding,
        metadata=document.metadata,
    )

    return formatted_doc



