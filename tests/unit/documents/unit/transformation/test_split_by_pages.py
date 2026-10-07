"""Zero-mock tests for splitting PDF documents by pages.

The PDFs are real files built byte-by-byte (Helvetica text, one line per page)
and read back with pypdf.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pypdf", reason="pypdf not installed (uv sync --extra documents)")

from codomyrmex.documents.core.document_reader import read_document
from codomyrmex.documents.exceptions import DocumentConversionError
from codomyrmex.documents.models.document import (
    Document,
    DocumentFormat,
)
from codomyrmex.documents.transformation.splitter import split_document


def _write_pdf(path: Path, page_texts: list[str]) -> Path:
    """Write a minimal valid PDF with one line of Helvetica text per page."""
    n_pages = len(page_texts)
    page_ids = [4 + 2 * i for i in range(n_pages)]
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for pid, text in zip(page_ids, page_texts, strict=True):
        stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
        objects.append(
            (
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 3 0 R >> >> /Contents {pid + 1} 0 R >>"
            ).encode()
        )
        objects.append(
            f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_at}\n%%EOF\n"
    ).encode()
    path.write_bytes(bytes(out))
    return path


@pytest.fixture
def five_page_pdf(tmp_path) -> Path:
    return _write_pdf(tmp_path / "five.pdf", [f"Page number {i}" for i in range(1, 6)])


@pytest.mark.unit
class TestSplitPdfByPages:
    def test_one_page_per_chunk_by_default(self, five_page_pdf):
        doc = Document("ignored", DocumentFormat.PDF, file_path=five_page_pdf)
        chunks = split_document(doc, {"method": "by_pages"})
        assert len(chunks) == 5
        for i, chunk in enumerate(chunks, start=1):
            assert chunk.format == DocumentFormat.PDF
            assert chunk.content.strip() == f"Page number {i}"
            fields = chunk.metadata.custom_fields
            assert fields["chunk_index"] == i - 1
            assert fields["page_start"] == fields["page_end"] == i
            assert fields["source_file"] == str(five_page_pdf)

    def test_groups_pages_with_short_last_chunk(self, five_page_pdf):
        doc = Document("ignored", DocumentFormat.PDF, file_path=five_page_pdf)
        chunks = split_document(doc, {"method": "by_pages", "pages": 2})
        assert [
            (
                c.metadata.custom_fields["page_start"],
                c.metadata.custom_fields["page_end"],
            )
            for c in chunks
        ] == [(1, 2), (3, 4), (5, 5)]
        assert "Page number 1" in chunks[0].content
        assert "Page number 2" in chunks[0].content
        assert "Page number 3" not in chunks[0].content
        assert chunks[2].content.strip() == "Page number 5"

    def test_document_read_from_disk(self, five_page_pdf):
        doc = read_document(five_page_pdf)
        assert doc.format == DocumentFormat.PDF
        chunks = split_document(doc, {"method": "by_pages", "pages": 5})
        assert len(chunks) == 1
        assert chunks[0].metadata.custom_fields["page_end"] == 5

    def test_without_source_file_raises(self):
        doc = Document("Page number 1\nPage number 2", DocumentFormat.PDF)
        with pytest.raises(DocumentConversionError, match="source file"):
            split_document(doc, {"method": "by_pages"})

    @pytest.mark.parametrize("pages", [0, -1, 1.5, "2", True])
    def test_invalid_pages_raises(self, five_page_pdf, pages):
        doc = Document("ignored", DocumentFormat.PDF, file_path=five_page_pdf)
        with pytest.raises(DocumentConversionError, match="positive integer"):
            split_document(doc, {"method": "by_pages", "pages": pages})

    def test_unreadable_file_raises(self, tmp_path):
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"not a pdf")
        doc = Document("ignored", DocumentFormat.PDF, file_path=bad)
        with pytest.raises(DocumentConversionError):
            split_document(doc, {"method": "by_pages"})
