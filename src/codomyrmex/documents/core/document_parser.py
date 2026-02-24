"""Document parsing operations."""

from __future__ import annotations

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..exceptions import DocumentParseError
from ..models.document import Document, DocumentFormat

logger = get_logger(__name__)


class DocumentParser:
    """Parser for converting content strings into Document objects."""

    def parse(
        self,
        content: str,
        format: DocumentFormat,
        file_path: str | None = None,
    ) -> Document:
        """
        Parse content string into a Document object.

        Args:
            content: Content string to parse
            format: Format of the content
            file_path: Optional file path for context

        Returns:
            Document object

        Raises:
            DocumentParseError: If parsing fails
        """
        try:
            parsed_content = self._parse_content(content, format)

            document = Document(
                content=parsed_content,
                format=format,
                file_path=file_path,
            )

            return document

        except Exception as e:
            logger.error(f"Error parsing document: {e}")
            raise DocumentParseError(f"Failed to parse document: {str(e)}") from e

    def _parse_content(self, content: str, format: DocumentFormat) -> Any:
        """Parse content based on format."""
        if format == DocumentFormat.JSON:
            import json
            return json.loads(content)
        elif format == DocumentFormat.YAML:
            import yaml
            return yaml.safe_load(content)
        elif format in [DocumentFormat.MARKDOWN, DocumentFormat.TEXT, DocumentFormat.HTML]:
            return content
        else:
            # For other formats, return as string for now
            return content


def parse_document(
    content: str,
    format: DocumentFormat,
    file_path: str | None = None,
) -> Document:
    """
    Parse content string into a Document object.

    Convenience function that creates a DocumentParser and parses the content.

    Args:
        content: Content string to parse
        format: Format of the content
        file_path: Optional file path for context

    Returns:
        Document object
    """
    parser = DocumentParser()
    return parser.parse(content, format, file_path)



