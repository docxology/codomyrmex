"""Core PDF dark mode filter implementations.

Provides pixel-level filter operations inspired by dark-pdf's JavaScript logic,
implemented natively in Python using PyMuPDF and Pillow.

The filter pipeline applies transformations in this order:
    1. Inversion - inverts colors for dark background
    2. Brightness - adjusts overall brightness
    3. Contrast - adjusts contrast
    4. Sepia - applies warm sepia tone

Default values match dark-pdf's defaults (90% inversion, 90% brightness,
90% contrast, 10% sepia).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise ImportError(
        "PyMuPDF is required for PDF dark mode filters. "
        "Install with: uv sync --extra dark"
    ) from e


@dataclass
class DarkPDFFilter:
    """Configurable dark mode filter for PDF pages.

    Applies pixel-level transformations matching dark-pdf's filter logic:
    inversion, brightness, contrast, and sepia.

    Args:
        inversion: Inversion amount, 0.0-1.0 (default 0.90, maps to dark-pdf's 90%).
        brightness: Brightness multiplier, 0.1-3.0 (default 0.90, maps to dark-pdf's 90%).
        contrast: Contrast multiplier, 0.1-3.0 (default 0.90, maps to dark-pdf's 90%).
        sepia: Sepia amount, 0.0-1.0 (default 0.10, maps to dark-pdf's 10%).
        dpi: Resolution for rendering PDF pages to images (default 150).
    """

    inversion: float = 0.90
    brightness: float = 0.90
    contrast: float = 0.90
    sepia: float = 0.10
    dpi: int = 150

    def __post_init__(self) -> None:
        """Validate parameter ranges."""
        if not 0.0 <= self.inversion <= 1.0:
            raise ValueError(f"inversion must be 0.0-1.0, got {self.inversion}")
        if not 0.1 <= self.brightness <= 3.0:
            raise ValueError(f"brightness must be 0.1-3.0, got {self.brightness}")
        if not 0.1 <= self.contrast <= 3.0:
            raise ValueError(f"contrast must be 0.1-3.0, got {self.contrast}")
        if not 0.0 <= self.sepia <= 1.0:
            raise ValueError(f"sepia must be 0.0-1.0, got {self.sepia}")
        if self.dpi < 36:
            raise ValueError(f"dpi must be >= 36, got {self.dpi}")

    def apply_to_image(self, image: Image.Image) -> Image.Image:
        """Apply dark mode filters to a PIL Image.

        Processes the image through the filter pipeline:
        inversion -> brightness -> contrast -> sepia.

        Args:
            image: Input PIL Image (RGB or RGBA).

        Returns:
            New PIL Image with filters applied.
        """
        # Convert to RGB if needed, preserving alpha
        has_alpha = image.mode == "RGBA"
        if has_alpha:
            alpha = image.split()[3]
            rgb = image.convert("RGB")
        elif image.mode != "RGB":
            rgb = image.convert("RGB")
        else:
            rgb = image.copy()

        # Work with numpy for vectorized operations
        pixels = np.array(rgb, dtype=np.float64)

        # 1. Inversion: r = r + (255 - 2 * r) * inversion
        if self.inversion > 0:
            pixels = pixels + (255.0 - 2.0 * pixels) * self.inversion

        # 2. Brightness: multiply by brightness factor
        if self.brightness != 1.0:
            pixels *= self.brightness

        # 3. Contrast: ((pixel/255 - 0.5) * (1 + factor) + 0.5) * 255
        if self.contrast != 1.0:
            contrast_factor = (self.contrast - 0.5) * 2.0
            pixels = ((pixels / 255.0 - 0.5) * (1.0 + contrast_factor) + 0.5) * 255.0

        # 4. Sepia: blend with sepia color transform
        if self.sepia > 0:
            r = pixels[:, :, 0]
            g = pixels[:, :, 1]
            b = pixels[:, :, 2]

            sepia_r = 0.393 * r + 0.769 * g + 0.189 * b
            sepia_g = 0.349 * r + 0.686 * g + 0.168 * b
            sepia_b = 0.272 * r + 0.534 * g + 0.131 * b

            pixels[:, :, 0] = r + (sepia_r - r) * self.sepia
            pixels[:, :, 1] = g + (sepia_g - g) * self.sepia
            pixels[:, :, 2] = b + (sepia_b - b) * self.sepia

        # Clamp to valid range
        np.clip(pixels, 0, 255, out=pixels)

        result = Image.fromarray(pixels.astype(np.uint8))

        if has_alpha:
            result.putalpha(alpha)

        return result

    def apply_to_pdf(
        self,
        input_path: str | Path,
        output_path: str | Path,
    ) -> None:
        """Apply dark mode filters to an entire PDF.

        Renders each page as an image, applies filters, then reassembles
        into a new PDF.

        Args:
            input_path: Path to the input PDF file.
            output_path: Path for the output PDF file.

        Raises:
            FileNotFoundError: If input_path does not exist.
            RuntimeError: If PDF processing fails.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input PDF not found: {input_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate zoom factor from DPI (PDF default is 72 DPI)
        zoom = self.dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        src_doc = fitz.open(str(input_path))
        out_doc = fitz.open()

        try:
            for page_num in range(len(src_doc)):
                page = src_doc[page_num]
                pix = page.get_pixmap(matrix=matrix)

                # Convert pixmap to PIL Image
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                # Apply filters
                filtered = self.apply_to_image(img)

                # Convert back to pixmap and insert into new document
                img_bytes = filtered.tobytes("raw", "RGB")
                filtered_pix = fitz.Pixmap(
                    fitz.csRGB, filtered.width, filtered.height, img_bytes, 0
                )

                # Create new page with same dimensions as original
                rect = page.rect
                new_page = out_doc.new_page(
                    width=rect.width, height=rect.height
                )
                new_page.insert_image(rect, pixmap=filtered_pix)

            out_doc.save(str(output_path))
        finally:
            src_doc.close()
            out_doc.close()


def apply_dark_mode(
    input_path: str | Path,
    output_path: str | Path,
    *,
    inversion: float = 0.90,
    brightness: float = 0.90,
    contrast: float = 0.90,
    sepia: float = 0.10,
    dpi: int = 150,
) -> None:
    """Apply dark mode filters to a PDF file.

    Convenience function that creates a DarkPDFFilter and processes the PDF.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path for the output PDF file.
        inversion: Inversion amount, 0.0-1.0 (default 0.90).
        brightness: Brightness multiplier, 0.1-3.0 (default 0.90).
        contrast: Contrast multiplier, 0.1-3.0 (default 0.90).
        sepia: Sepia amount, 0.0-1.0 (default 0.10).
        dpi: Resolution for rendering PDF pages (default 150).
    """
    pdf_filter = DarkPDFFilter(
        inversion=inversion,
        brightness=brightness,
        contrast=contrast,
        sepia=sepia,
        dpi=dpi,
    )
    pdf_filter.apply_to_pdf(input_path, output_path)
