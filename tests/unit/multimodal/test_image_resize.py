"""Zero-mock tests for ImageProcessor.resize_if_needed with real Pillow images."""

from __future__ import annotations

import io
import random

import pytest

Image = pytest.importorskip("PIL.Image", reason="Pillow not installed")

from codomyrmex.llm.multimodal import (
    ImageContent,
    ImageProcessor,
    MediaContent,
    MediaType,
)


def _noise_image_bytes(width: int, height: int, fmt: str) -> bytes:
    """Encode deterministic RGB noise (poorly compressible) in ``fmt``."""
    pixels = random.Random(0).randbytes(width * height * 3)
    image = Image.frombytes("RGB", (width, height), pixels)
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def _dimensions(data: bytes) -> tuple[int, int]:
    with Image.open(io.BytesIO(data)) as image:
        return image.size


@pytest.mark.unit
class TestResizeIfNeeded:
    def test_small_image_returned_unchanged(self):
        data = _noise_image_bytes(8, 8, "PNG")
        content = MediaContent(media_type=MediaType.IMAGE, data=data, format="png")
        assert ImageProcessor().resize_if_needed(content, max_bytes=10_000) is content

    @pytest.mark.parametrize("fmt", ["PNG", "JPEG"])
    def test_large_image_is_downscaled_below_budget(self, fmt):
        data = _noise_image_bytes(320, 160, fmt)
        budget = len(data) // 4
        content = MediaContent(
            media_type=MediaType.IMAGE,
            data=data,
            format=fmt.lower(),
            metadata={"source": "noise"},
        )
        resized = ImageProcessor().resize_if_needed(content, max_bytes=budget)

        assert resized is not content
        assert resized.size_bytes <= budget
        width, height = _dimensions(resized.data)
        assert width < 320
        assert height < 160
        assert width / height == pytest.approx(2.0, rel=0.05)
        with Image.open(io.BytesIO(resized.data)) as image:
            assert image.format == fmt
        assert resized.metadata["source"] == "noise"
        assert resized.metadata["original_size"] == len(data)
        assert resized.metadata["original_dimensions"] == (320, 160)
        assert resized.metadata["dimensions"] == (width, height)
        # The input is not modified.
        assert content.data == data
        assert "original_size" not in content.metadata

    def test_image_content_dimensions_updated(self):
        data = _noise_image_bytes(200, 200, "PNG")
        content = ImageContent(
            media_type=MediaType.IMAGE,
            data=data,
            format="png",
            width=200,
            height=200,
        )
        resized = ImageProcessor().resize_if_needed(content, max_bytes=len(data) // 3)
        assert isinstance(resized, ImageContent)
        assert resized.dimensions == _dimensions(resized.data)
        assert resized.width < 200

    def test_non_image_rejected(self):
        content = MediaContent(media_type=MediaType.AUDIO, data=b"x" * 100)
        with pytest.raises(ValueError, match="Only images"):
            ImageProcessor().resize_if_needed(content, max_bytes=10)

    def test_non_positive_budget_rejected(self):
        content = MediaContent(media_type=MediaType.IMAGE, data=b"x")
        with pytest.raises(ValueError, match="positive"):
            ImageProcessor().resize_if_needed(content, max_bytes=0)

    def test_unreachable_budget_raises(self):
        data = _noise_image_bytes(64, 64, "PNG")
        content = MediaContent(media_type=MediaType.IMAGE, data=data, format="png")
        with pytest.raises(ValueError, match="Cannot reduce"):
            ImageProcessor().resize_if_needed(content, max_bytes=20)
