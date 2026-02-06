"""Document writing operations."""

from __future__ import annotations

from pathlib import Path

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..config import get_config
from ..exceptions import DocumentWriteError, UnsupportedFormatError
from ..models.document import Document, DocumentFormat

logger = get_logger(__name__)


class DocumentWriter:
    """Unified document writer supporting multiple formats."""

    def __init__(self):

        self.config = get_config()

    def write(
        self,
        document: Document,
        file_path: str | Path,
        format: DocumentFormat | None = None,
        encoding: str | None = None,
    ) -> None:
        """
        Write a document to a file.

        Args:
            document: Document object to write
            file_path: Path where document should be written
            format: Optional format override (uses document.format if not provided)
            encoding: Optional encoding override (uses document.encoding if not provided)

        Raises:
            DocumentWriteError: If writing fails
            UnsupportedFormatError: If format is not supported
        """
        file_path = Path(file_path)
        format = format or document.format
        encoding = encoding or document.encoding or self.config.default_encoding

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format == DocumentFormat.MARKDOWN:
                from ..formats.markdown_handler import write_markdown
                content = document.get_content_as_string()
                write_markdown(content, str(file_path), encoding=encoding)
            elif format == DocumentFormat.JSON:
                from ..formats.json_handler import write_json
                if isinstance(document.content, dict):
                    write_json(document.content, str(file_path), encoding=encoding)
                else:
                    import json
                    data = json.loads(document.get_content_as_string())
                    write_json(data, str(file_path), encoding=encoding)
            elif format == DocumentFormat.YAML:
                from ..formats.yaml_handler import write_yaml
                if isinstance(document.content, dict):
                    write_yaml(document.content, str(file_path), encoding=encoding)
                else:
                    import yaml
                    data = yaml.safe_load(document.get_content_as_string())
                    write_yaml(data, str(file_path), encoding=encoding)
            elif format == DocumentFormat.PDF:
                from ..formats.pdf_handler import write_pdf
                content = document.get_content_as_string()
                write_pdf(content, str(file_path), metadata=document.metadata)
            elif format == DocumentFormat.TEXT:
                from ..formats.text_handler import write_text
                content = document.get_content_as_string()
                write_text(content, str(file_path), encoding=encoding)
            else:
                raise UnsupportedFormatError(
                    f"Format {format.value} not yet implemented",
                    format=format.value
                )

            logger.info(f"Successfully wrote document to {file_path}")

        except Exception as e:
            logger.error(f"Error writing document to {file_path}: {e}")
            raise DocumentWriteError(
                f"Failed to write document: {str(e)}",
                file_path=str(file_path)
            ) from e


def write_document(
    document: Document,
    file_path: str | Path,
    format: DocumentFormat | None = None,
    encoding: str | None = None,
) -> None:
    """
    Write a document to a file.

    Convenience function that creates a DocumentWriter and writes the document.

    Args:
        document: Document object to write
        file_path: Path where document should be written
        format: Optional format override
        encoding: Optional encoding override
    """
    writer = DocumentWriter()
    writer.write(document, file_path, format=format, encoding=encoding)

