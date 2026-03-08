"""Tests for vision module — VLMClient, models, AnnotationExtractor.

Zero-Mock: Tests for VLMClient require Ollama with llava model.
Model tests (BoundingBox, Annotation, PageContent) use real objects.
Annotation parsing tests use real JSON parsing.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from codomyrmex.vision.annotation_extractor import AnnotationExtractor
from codomyrmex.vision.models import (
    Annotation,
    BoundingBox,
    PageContent,
    VLMConfig,
    VLMResponse,
)
from codomyrmex.vision.pdf_extractor import PDFExtractor
from codomyrmex.vision.vlm_client import VLMClient

# ── VLMConfig ─────────────────────────────────────────────────────────


class TestVLMConfig:
    """Verify VLM configuration defaults."""

    def test_defaults(self) -> None:
        cfg = VLMConfig()
        assert cfg.model_name == "llava"
        assert cfg.host == "localhost"
        assert cfg.port == 11434
        assert cfg.temperature == 0.2

    def test_custom_model(self) -> None:
        cfg = VLMConfig(model_name="bakllava", temperature=0.5)
        assert cfg.model_name == "bakllava"
        assert cfg.temperature == 0.5


# ── BoundingBox ───────────────────────────────────────────────────────


class TestBoundingBox:
    """Verify bounding box calculations."""

    def test_area(self) -> None:
        bbox = BoundingBox(x=0.1, y=0.2, width=0.5, height=0.3)
        assert bbox.area == pytest.approx(0.15)

    def test_center(self) -> None:
        bbox = BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0)
        assert bbox.center == (0.5, 0.5)

    def test_zero_area(self) -> None:
        bbox = BoundingBox()
        assert bbox.area == 0.0


# ── VLMResponse ───────────────────────────────────────────────────────


class TestVLMResponse:
    """Verify response data."""

    def test_construction(self) -> None:
        resp = VLMResponse(text="A cat sitting on a mat", model="llava")
        assert "cat" in resp.text
        assert resp.model == "llava"


# ── PageContent ───────────────────────────────────────────────────────


class TestPageContent:
    """Verify page content data."""

    def test_construction(self) -> None:
        page = PageContent(page_number=1, text="Hello world")
        assert page.page_number == 1
        assert page.text == "Hello world"

    def test_with_annotations(self) -> None:
        ann = Annotation(label="title", confidence=0.9)
        page = PageContent(page_number=1, annotations=[ann])
        assert len(page.annotations) == 1


# ── VLMClient ─────────────────────────────────────────────────────────


class TestVLMClient:
    """Test VLM client (requires Ollama with llava)."""

    def test_base_url(self) -> None:
        client = VLMClient()
        assert client.base_url == "http://localhost:11434"

    def test_custom_config(self) -> None:
        cfg = VLMConfig(model_name="bakllava", port=12345)
        client = VLMClient(cfg)
        assert client.base_url == "http://localhost:12345"

    def test_analyze_image_file_not_found(self) -> None:
        client = VLMClient()
        with pytest.raises(FileNotFoundError):
            client.analyze_image("/nonexistent/image.png")

    def test_extract_text_file_not_found(self) -> None:
        client = VLMClient()
        with pytest.raises(FileNotFoundError):
            client.extract_text("/nonexistent/image.png")

    @pytest.mark.skipif(
        not VLMClient().is_available(),
        reason="Ollama with llava not available",
    )
    def test_analyze_real_image(self) -> None:
        """Test with a real image if Ollama is running."""
        import struct

        # Create a simple test image (1x1 white pixel BMP)
        with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as f:
            # Minimal BMP header + 1 white pixel
            bmp_data = (
                b"BM"  # Signature
                + struct.pack("<I", 58)  # File size
                + b"\x00\x00\x00\x00"  # Reserved
                + struct.pack("<I", 54)  # Offset to pixel data
                + struct.pack("<I", 40)  # DIB header size
                + struct.pack("<i", 1)  # Width
                + struct.pack("<i", 1)  # Height
                + struct.pack("<HH", 1, 24)  # Planes, BPP
                + b"\x00" * 24  # Rest of DIB header
                + b"\xff\xff\xff\x00"  # White pixel + padding
            )
            f.write(bmp_data)
            f.flush()
            client = VLMClient()
            response = client.analyze_image(f.name, "What color is this image?")
            assert len(response.text) > 0


# ── AnnotationExtractor ──────────────────────────────────────────────


class TestAnnotationExtractor:
    """Test annotation parsing logic."""

    def test_parse_valid_json_response(self) -> None:
        extractor = AnnotationExtractor()
        annotations_json = json.dumps([
            {
                "label": "cat",
                "confidence": 0.95,
                "position": {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4},
                "attributes": {"color": "orange"},
            }
        ])
        response = VLMResponse(text=annotations_json)
        result = extractor._parse_annotations(response)
        assert len(result) == 1
        assert result[0].label == "cat"
        assert result[0].confidence == 0.95
        assert result[0].bounding_box.x == 0.1
        assert result[0].attributes["color"] == "orange"

    def test_parse_invalid_json_fallback(self) -> None:
        extractor = AnnotationExtractor()
        response = VLMResponse(text="I see a cat and a dog in the image")
        result = extractor._parse_annotations(response)
        assert len(result) == 1
        assert result[0].label == "raw_description"
        assert "cat" in result[0].attributes["raw_text"]

    def test_parse_markdown_wrapped_json(self) -> None:
        extractor = AnnotationExtractor()
        json_content = json.dumps([
            {"label": "logo", "confidence": 0.8, "position": {}, "attributes": {}}
        ])
        response = VLMResponse(text=f"```json\n{json_content}\n```")
        result = extractor._parse_annotations(response)
        assert len(result) == 1
        assert result[0].label == "logo"

    def test_build_prompt_default(self) -> None:
        extractor = AnnotationExtractor()
        prompt = extractor._build_prompt()
        assert "JSON array" in prompt

    def test_build_prompt_with_categories(self) -> None:
        extractor = AnnotationExtractor()
        prompt = extractor._build_prompt(categories=["text", "logo"])
        assert "text" in prompt
        assert "logo" in prompt

    def test_extract_annotations_file_not_found(self) -> None:
        extractor = AnnotationExtractor()
        vlm = VLMClient()
        with pytest.raises(FileNotFoundError):
            extractor.extract_annotations("/nonexistent.png", vlm)


# ── PDFExtractor ──────────────────────────────────────────────────────


class TestPDFExtractor:
    """Test PDF extractor (requires pymupdf for full tests)."""

    def test_extract_text_file_not_found(self) -> None:
        extractor = PDFExtractor()
        with pytest.raises(FileNotFoundError):
            extractor.extract_text("/nonexistent.pdf")

    def test_get_metadata_file_not_found(self) -> None:
        extractor = PDFExtractor()
        with pytest.raises(FileNotFoundError):
            extractor.get_metadata("/nonexistent.pdf")

    @pytest.mark.skipif(
        not PDFExtractor.is_available(),
        reason="pymupdf not installed",
    )
    def test_extract_text_real_pdf(self) -> None:
        """Test with a programmatically created PDF."""
        import fitz

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), "Hello Vision Module")
            doc.save(f.name)
            doc.close()

            extractor = PDFExtractor()
            pages = extractor.extract_text(f.name)
            assert len(pages) == 1
            assert "Hello Vision Module" in pages[0].text
