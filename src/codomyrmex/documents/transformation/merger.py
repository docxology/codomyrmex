"""Document merging operations."""

from codomyrmex.documents.exceptions import DocumentConversionError
from codomyrmex.documents.models.document import Document, DocumentFormat
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


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
        elif target_format == DocumentFormat.CSV:
            merged_content = _merge_csv(converted_docs)
        else:
            merged_content = _merge_text(converted_docs)

        # Merge metadata
        merged_metadata = documents[0].metadata.copy()
        for doc in documents[1:]:
            merged_metadata.update(doc.metadata)

        merged_doc = Document(
            content=merged_content,
            format=target_format,
            metadata=merged_metadata,
        )

        return merged_doc

    except Exception as e:
        logger.error(f"Error merging documents: {e}")
        if isinstance(e, DocumentConversionError):
            raise
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


def _merge_json(documents: list[Document]) -> dict | list:
    """Merge JSON documents."""
    if all(isinstance(doc.content, list) for doc in documents):
        merged_list = []
        for doc in documents:
            merged_list.extend(doc.content)
        return merged_list
    
    merged_dict = {}
    for doc in documents:
        if isinstance(doc.content, dict):
            merged_dict.update(doc.content)
        else:
            if "documents" not in merged_dict:
                merged_dict["documents"] = []
            merged_dict["documents"].append(doc.content)
    return merged_dict


def _merge_yaml(documents: list[Document]) -> dict | list:
    """Merge YAML documents."""
    return _merge_json(documents)


def _merge_text(documents: list[Document]) -> str:
    """Merge text documents."""
    parts = []
    for doc in documents:
        parts.append(doc.get_content_as_string())
    return "\n\n".join(parts)

def _merge_csv(documents: list[Document]) -> list[dict]:
    """Merge CSV documents (list of dicts)."""
    merged = []
    for doc in documents:
        if isinstance(doc.content, list):
            merged.extend(doc.content)
    return merged
