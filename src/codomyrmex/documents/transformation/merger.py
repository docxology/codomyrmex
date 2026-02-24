"""Document merging operations."""


from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..exceptions import DocumentConversionError
from ..models.document import Document, DocumentFormat

logger = get_logger(__name__)


def _metadata_as_dict(metadata):
    """Safely convert metadata to a dict for merging."""
    if metadata is None:
        return {}
    if isinstance(metadata, dict):
        return metadata
    if hasattr(metadata, 'to_dict'):
        return metadata.to_dict()
    return {}


def merge_documents(documents: list[Document], target_format: DocumentFormat = None) -> Document:
    """
    Merge multiple documents into a single document.

    Args:
        documents: List of documents to merge
        target_format: Optional target format (uses first document's format if not provided)

    Returns:
        Merged Document

    Raises:
        DocumentConversionError: If merging fails
    """
    if not documents:
        raise ValueError("Cannot merge empty list of documents")

    if len(documents) == 1:
        return documents[0]

    target_format = target_format or documents[0].format

    try:
        # Convert all documents to target format
        converted_docs = []
        for doc in documents:
            if doc.format != target_format:
                from .converter import convert_document
                doc = convert_document(doc, target_format)
            converted_docs.append(doc)

        # Merge content based on format
        if target_format == DocumentFormat.MARKDOWN:
            merged_content = _merge_markdown(converted_docs)
        elif target_format == DocumentFormat.JSON:
            merged_content = _merge_json(converted_docs)
        elif target_format == DocumentFormat.YAML:
            merged_content = _merge_yaml(converted_docs)
        elif target_format == DocumentFormat.TEXT:
            merged_content = _merge_text(converted_docs)
        else:
            merged_content = _merge_text(converted_docs)

        # Merge metadata
        merged_metadata = {}
        for doc in converted_docs:
            merged_metadata.update(_metadata_as_dict(doc.metadata))

        merged_doc = Document(
            content=merged_content,
            format=target_format,
            metadata=merged_metadata,
        )

        return merged_doc

    except Exception as e:
        logger.error(f"Error merging documents: {e}")
        raise DocumentConversionError(f"Failed to merge documents: {str(e)}") from e


def _merge_markdown(documents: list[Document]) -> str:
    """Merge markdown documents."""
    parts = []
    for i, doc in enumerate(documents):
        content = doc.get_content_as_string()
        if i > 0:
            parts.append("\n\n---\n\n")
        parts.append(content)
    return "".join(parts)


def _merge_json(documents: list[Document]) -> dict:
    """Merge JSON documents."""
    merged = {}
    for doc in documents:
        if isinstance(doc.content, dict):
            merged.update(doc.content)
        else:
            if "documents" not in merged:
                merged["documents"] = []
            merged["documents"].append(doc.content)
    return merged


def _merge_yaml(documents: list[Document]) -> dict:
    """Merge YAML documents."""
    merged = {}
    for doc in documents:
        if isinstance(doc.content, dict):
            merged.update(doc.content)
        else:
            if "documents" not in merged:
                merged["documents"] = []
            merged["documents"].append(doc.content)
    return merged


def _merge_text(documents: list[Document]) -> str:
    """Merge text documents."""
    parts = []
    for doc in documents:
        parts.append(doc.get_content_as_string())
    return "\n\n".join(parts)
