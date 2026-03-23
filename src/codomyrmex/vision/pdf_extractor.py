"""PDF text extraction pipeline.

Extracts text from PDF documents using pymupdf (fitz) with an
optional VLM fallback for scanned/image-based PDFs.

Example::

    extractor = PDFExtractor()
    pages = extractor.extract_text("document.pdf")
    for page in pages:
        print(f"Page {page.page_number}: {page.text[:100]}...")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .models import PageContent

if TYPE_CHECKING:
    from .vlm_client import VLMClient

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extracts text and metadata from PDF files.

    Uses ``pymupdf`` (fitz) for text extraction. Falls back to
    VLM-based extraction for scanned PDFs when a :class:`VLMClient`
    is provided.

    Example::

        extractor = PDFExtractor()
        pages = extractor.extract_text("report.pdf")
    """

    @staticmethod
    def is_available() -> bool:
        """Check if pymupdf is installed."""
        try:
            import fitz

            return True
        except ImportError:
            return False

    def extract_text(self, pdf_path: str | Path) -> list[PageContent]:
        """Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            list of :class:`PageContent` for each page.

        Raises:
            FileNotFoundError: If the PDF doesn't exist.
            ImportError: If pymupdf is not installed.
        """
        path = Path(pdf_path)
        if not path.exists():
            msg = f"PDF not found: {path}"
            raise FileNotFoundError(msg)

        try:
            import fitz
        except ImportError as exc:
            msg = "pymupdf required: uv add pymupdf"
            raise ImportError(msg) from exc

        pages: list[PageContent] = []
        doc = fitz.open(str(path))

        try:
            for i, page in enumerate(doc):
                text = page.get_text("text")
                images = [
                    f"image_{j}" for j, img in enumerate(page.get_images(full=True))
                ]

                pages.append(
                    PageContent(
                        page_number=i + 1,
                        text=text.strip(),
                        images=images,
                        metadata={
                            "width": page.rect.width,
                            "height": page.rect.height,
                            "rotation": page.rotation,
                        },
                    )
                )
        finally:
            doc.close()

        return pages

    def extract_with_vlm(
        self,
        pdf_path: str | Path,
        vlm_client: VLMClient,
        pages: list[int] | None = None,
    ) -> list[PageContent]:
        """Extract text using VLM for scanned/image-based PDFs.

        Renders each page as an image and sends it to the VLM for
        text extraction.

        Args:
            pdf_path: Path to the PDF file.
            vlm_client: VLM client for image analysis.
            pages: Optional list of 1-indexed page numbers to extract.

        Returns:
            list of :class:`PageContent` with VLM-extracted text.

        Raises:
            FileNotFoundError: If the PDF doesn't exist.
            ImportError: If pymupdf is not installed.
        """
        path = Path(pdf_path)
        if not path.exists():
            msg = f"PDF not found: {path}"
            raise FileNotFoundError(msg)

        try:
            import fitz
        except ImportError as exc:
            msg = "pymupdf required: uv add pymupdf"
            raise ImportError(msg) from exc

        import tempfile

        results: list[PageContent] = []
        doc = fitz.open(str(path))

        try:
            page_range = range(len(doc))
            if pages:
                page_range = range(len(doc))
                page_range = [p - 1 for p in pages if 0 < p <= len(doc)]  # type: ignore[assignment]

            for i in page_range:
                page = doc[i]
                # Render page as PNG
                pix = page.get_pixmap(dpi=150)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    pix.save(tmp.name)
                    response = vlm_client.extract_text(tmp.name)

                results.append(
                    PageContent(
                        page_number=i + 1,
                        text=response,
                        metadata={
                            "extraction_method": "vlm",
                            "model": vlm_client.config.model_name,
                        },
                    )
                )
        finally:
            doc.close()

        return results

    def get_metadata(self, pdf_path: str | Path) -> dict[str, Any]:
        """Extract PDF metadata (title, author, etc.).

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            dict of PDF metadata.
        """
        path = Path(pdf_path)
        if not path.exists():
            msg = f"PDF not found: {path}"
            raise FileNotFoundError(msg)

        try:
            import fitz
        except ImportError as exc:
            msg = "pymupdf required: uv add pymupdf"
            raise ImportError(msg) from exc

        doc = fitz.open(str(path))
        try:
            meta = doc.metadata or {}
            meta["page_count"] = len(doc)
            return meta
        finally:
            doc.close()


__all__ = ["PDFExtractor"]
