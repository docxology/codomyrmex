"""Document splitting operations."""

from codomyrmex.documents.exceptions import DocumentConversionError
from codomyrmex.documents.models.document import Document
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def split_document(document: Document, criteria: dict) -> list[Document]:
    """
    Split a document into multiple documents based on criteria.

    Args:
        document: Document to split
        criteria: Split criteria (e.g., {"method": "by_pages", "pages": 10})

    Returns:
        list of split documents

    Raises:
        DocumentConversionError: If splitting fails
    """
    method = criteria.get("method", "by_sections")

    try:
        if method == "by_sections":
            return _split_by_sections(document, criteria)
        if method == "by_size":
            return _split_by_size(document, criteria)
        if method == "by_pages" and document.format.value == "pdf":
            return _split_by_pages(document, criteria)
        if method == "by_rows" and document.format.value == "csv":
            return _split_by_rows(document, criteria)
        # Default: split by lines
        return _split_by_lines(document, criteria)

    except Exception as e:
        logger.error("Error splitting document: %s", e)
        if isinstance(e, DocumentConversionError):
            raise
        raise DocumentConversionError(f"Failed to split document: {e!s}") from e


def _split_by_sections(document: Document, criteria: dict) -> list[Document]:
    """Split document by sections (markdown headers, etc.)."""
    content = document.get_content_as_string()
    sections = []
    current_section = []

    for line in content.split("\n"):
        if line.strip().startswith("#"):
            if current_section:
                sections.append("\n".join(current_section))
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section))

    split_docs = []
    for i, section_content in enumerate(sections):
        new_metadata = document.metadata.copy()
        new_metadata.custom_fields["section_index"] = i

        split_doc = Document(
            content=section_content,
            format=document.format,
            metadata=new_metadata,
        )
        split_docs.append(split_doc)

    return split_docs


def _split_by_size(document: Document, criteria: dict) -> list[Document]:
    """Split document by size (characters)."""
    max_size = criteria.get("max_size", 10000)
    content = document.get_content_as_string()

    split_docs = []
    for i in range(0, len(content), max_size):
        chunk = content[i : i + max_size]
        new_metadata = document.metadata.copy()
        new_metadata.custom_fields["chunk_index"] = i // max_size

        split_doc = Document(
            content=chunk,
            format=document.format,
            metadata=new_metadata,
        )
        split_docs.append(split_doc)

    return split_docs


def _split_by_pages(document: Document, criteria: dict) -> list[Document]:
    """Split a PDF document into chunks of ``criteria["pages"]`` pages (default 1).

    Extracted PDF text does not keep page boundaries, so the source PDF is
    re-read page by page with pypdf from ``document.file_path`` (or the
    ``file_path`` of a ``PDFDocument`` content object). Each chunk's text is its
    pages' extracted text joined by newlines; ``custom_fields`` records
    ``chunk_index``, ``page_start``, ``page_end`` (1-based, inclusive) and
    ``source_file``.

    Raises:
        DocumentConversionError: If ``pages`` is not a positive integer, no
            source file is known, or pypdf is not installed.
    """
    pages_per_chunk = criteria.get("pages", 1)
    if (
        isinstance(pages_per_chunk, bool)
        or not isinstance(pages_per_chunk, int)
        or pages_per_chunk < 1
    ):
        raise DocumentConversionError(
            f"'pages' must be a positive integer, got {pages_per_chunk!r}"
        )

    source = document.file_path or getattr(document.content, "file_path", None)
    if not source:
        raise DocumentConversionError(
            "Splitting a PDF by pages needs the source file (document.file_path); "
            "page boundaries are not kept in extracted text."
        )

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise DocumentConversionError(
            "pypdf is required to split PDFs by pages. "
            "Install it with: uv sync --extra documents"
        ) from exc

    page_texts = [page.extract_text() or "" for page in PdfReader(str(source)).pages]

    split_docs = []
    for chunk_index, start in enumerate(range(0, len(page_texts), pages_per_chunk)):
        chunk = page_texts[start : start + pages_per_chunk]
        new_metadata = document.metadata.copy()
        new_metadata.custom_fields["chunk_index"] = chunk_index
        new_metadata.custom_fields["page_start"] = start + 1
        new_metadata.custom_fields["page_end"] = start + len(chunk)
        new_metadata.custom_fields["source_file"] = str(source)
        split_docs.append(
            Document(
                content="\n".join(chunk),
                format=document.format,
                metadata=new_metadata,
            )
        )
    return split_docs


def _split_by_rows(document: Document, criteria: dict) -> list[Document]:
    """Split CSV document (list of dicts) by rows."""
    rows_per_chunk = criteria.get("rows_per_chunk", 100)
    if not isinstance(document.content, list):
        return [document]

    split_docs = []
    for i in range(0, len(document.content), rows_per_chunk):
        chunk = document.content[i : i + rows_per_chunk]
        new_metadata = document.metadata.copy()
        new_metadata.custom_fields["chunk_index"] = i // rows_per_chunk

        split_doc = Document(
            content=chunk,
            format=document.format,
            metadata=new_metadata,
        )
        split_docs.append(split_doc)
    return split_docs


def _split_by_lines(document: Document, criteria: dict) -> list[Document]:
    """Split document by number of lines."""
    lines_per_chunk = criteria.get("lines_per_chunk", 100)
    content = document.get_content_as_string()
    lines = content.split("\n")

    split_docs = []
    for i in range(0, len(lines), lines_per_chunk):
        chunk_lines = lines[i : i + lines_per_chunk]
        chunk_content = "\n".join(chunk_lines)
        new_metadata = document.metadata.copy()
        new_metadata.custom_fields["chunk_index"] = i // lines_per_chunk

        split_doc = Document(
            content=chunk_content,
            format=document.format,
            metadata=new_metadata,
        )
        split_docs.append(split_doc)

    return split_docs
