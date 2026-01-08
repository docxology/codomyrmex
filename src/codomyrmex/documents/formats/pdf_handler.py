"""PDF document handler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..exceptions import DocumentReadError, DocumentWriteError

logger = get_logger(__name__)


@dataclass
class PDFDocument:
    """Represents a PDF document."""
    
    content: str  # Extracted text content
    metadata: dict
    page_count: int
    file_path: Optional[Path] = None
    
    def get_text(self) -> str:
        """Get text content."""
        return self.content


def read_pdf(file_path: str | Path) -> PDFDocument:
    """
    Read PDF content from a file.
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        PDFDocument with extracted text and metadata
    
    Raises:
        DocumentReadError: If reading fails
    """
    file_path = Path(file_path)
    
    try:
        # Try pypdf first (newer library)
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(str(file_path))
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
            
            metadata = reader.metadata or {}
            page_count = len(reader.pages)
            
            return PDFDocument(
                content=text_content,
                metadata=metadata,
                page_count=page_count,
                file_path=file_path,
            )
        except ImportError:
            # Fallback to PyPDF2
            try:
                import PyPDF2
                
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text_content = ""
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
                    
                    metadata = pdf_reader.metadata or {}
                    page_count = len(pdf_reader.pages)
                    
                    return PDFDocument(
                        content=text_content,
                        metadata=metadata,
                        page_count=page_count,
                        file_path=file_path,
                    )
            except ImportError:
                raise DocumentReadError(
                    "PDF libraries not available. Install with: pip install pypdf or pip install PyPDF2",
                    file_path=str(file_path)
                )
        
    except Exception as e:
        logger.error(f"Error reading PDF file {file_path}: {e}")
        raise DocumentReadError(
            f"Failed to read PDF file: {str(e)}",
            file_path=str(file_path)
        ) from e


def write_pdf(
    content: str,
    file_path: str | Path,
    metadata: Optional[dict] = None,
) -> None:
    """
    Write text content to a PDF file.
    
    Args:
        content: Text content to write
        file_path: Path where PDF should be written
        metadata: Optional PDF metadata (title, author, etc.)
    
    Raises:
        DocumentWriteError: If writing fails
    """
    file_path = Path(file_path)
    metadata = metadata or {}
    
    try:
        # Try reportlab first (better for generation)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            c = canvas.Canvas(str(file_path), pagesize=letter)
            
            # Set metadata
            if metadata.get("title"):
                c.setTitle(metadata["title"])
            if metadata.get("author"):
                c.setAuthor(metadata["author"])
            if metadata.get("subject"):
                c.setSubject(metadata["subject"])
            
            # Write content
            width, height = letter
            y = height - 50
            lines = content.split('\n')
            
            for line in lines:
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, line[:80])  # Limit line length
                y -= 20
            
            c.save()
            logger.debug(f"Wrote PDF to {file_path}")
            
        except ImportError:
            # Fallback to fpdf
            try:
                from fpdf import FPDF
                
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                
                # Set metadata
                if metadata.get("title"):
                    pdf.set_title(metadata["title"])
                if metadata.get("author"):
                    pdf.set_author(metadata["author"])
                
                # Write content
                pdf.set_font("Arial", size=12)
                for line in content.split('\n'):
                    pdf.cell(0, 10, txt=line, ln=1)
                
                pdf.output(str(file_path))
                logger.debug(f"Wrote PDF to {file_path}")
                
            except ImportError:
                raise DocumentWriteError(
                    "PDF generation libraries not available. Install with: pip install reportlab or pip install fpdf",
                    file_path=str(file_path)
                )
        
    except Exception as e:
        logger.error(f"Error writing PDF file {file_path}: {e}")
        raise DocumentWriteError(
            f"Failed to write PDF file: {str(e)}",
            file_path=str(file_path)
        ) from e



