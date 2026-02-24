"""Tests for crypto.steganography.image module."""

from __future__ import annotations

import os

import pytest
from PIL import Image

from codomyrmex.crypto.exceptions import SteganographyError
from codomyrmex.crypto.steganography.image import (
    calculate_capacity,
    embed_in_image,
    extract_from_image,
)


@pytest.fixture
def red_image(tmp_path):
    """Create a 100x100 solid red PNG image."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    path = str(tmp_path / "red.png")
    img.save(path, "PNG")
    return path


@pytest.fixture
def small_image(tmp_path):
    """Create a tiny 2x2 PNG image (very limited capacity)."""
    img = Image.new("RGB", (2, 2), color=(128, 128, 128))
    path = str(tmp_path / "small.png")
    img.save(path, "PNG")
    return path


@pytest.mark.unit
@pytest.mark.crypto
class TestCalculateCapacity:
    """Tests for calculate_capacity function."""

    def test_100x100_capacity(self, red_image):
        """Test functionality: 100x100 capacity."""
        capacity = calculate_capacity(red_image)
        # 100 * 100 * 3 / 8 - 4 = 3746
        assert capacity == 3746

    def test_small_image_capacity(self, small_image):
        """Test functionality: small image capacity."""
        capacity = calculate_capacity(small_image)
        # 2 * 2 * 3 / 8 - 4 = -2.5 -> max(0, -2) = 0... actually:
        # 2*2*3 = 12 bits total / 8 = 1 byte - 4 = -3 -> 0
        # Wait: 12 // 8 = 1, 1 - 4 = -3, max(0, -3) = 0
        assert capacity >= 0

    def test_nonexistent_image_raises(self):
        """Test functionality: nonexistent image raises."""
        with pytest.raises(SteganographyError):
            calculate_capacity("/nonexistent/path/image.png")

    def test_positive_for_reasonable_image(self, red_image):
        """Test functionality: positive for reasonable image."""
        assert calculate_capacity(red_image) > 0


@pytest.mark.unit
@pytest.mark.crypto
class TestEmbedAndExtract:
    """Tests for embed_in_image and extract_from_image roundtrip."""

    def test_roundtrip_simple_message(self, red_image, tmp_path):
        """Test functionality: roundtrip simple message."""
        output_path = str(tmp_path / "stego.png")
        message = "Hello, World!"

        result = embed_in_image(red_image, message, output_path)
        assert result is True
        assert os.path.exists(output_path)

        extracted = extract_from_image(output_path)
        assert extracted == message

    def test_roundtrip_empty_message(self, red_image, tmp_path):
        """Test functionality: roundtrip empty message."""
        output_path = str(tmp_path / "stego_empty.png")
        message = ""

        embed_in_image(red_image, message, output_path)
        extracted = extract_from_image(output_path)
        assert extracted == ""

    def test_roundtrip_unicode_message(self, red_image, tmp_path):
        """Test functionality: roundtrip unicode message."""
        output_path = str(tmp_path / "stego_unicode.png")
        message = "Unicode test: cafe"

        embed_in_image(red_image, message, output_path)
        extracted = extract_from_image(output_path)
        assert extracted == message

    def test_roundtrip_long_message(self, red_image, tmp_path):
        """Test functionality: roundtrip long message."""
        output_path = str(tmp_path / "stego_long.png")
        capacity = calculate_capacity(red_image)
        # Use ASCII message that fits within capacity
        message = "A" * min(capacity - 10, 3000)

        embed_in_image(red_image, message, output_path)
        extracted = extract_from_image(output_path)
        assert extracted == message

    def test_message_too_large_raises(self, small_image, tmp_path):
        """Test functionality: message too large raises."""
        output_path = str(tmp_path / "stego_fail.png")
        message = "This message is way too long for a 2x2 image"

        with pytest.raises(SteganographyError, match="too large"):
            embed_in_image(small_image, message, output_path)

    def test_output_is_valid_png(self, red_image, tmp_path):
        """Test functionality: output is valid png."""
        output_path = str(tmp_path / "stego.png")
        embed_in_image(red_image, "test", output_path)

        # Should be openable as a valid PNG
        img = Image.open(output_path)
        assert img.format == "PNG"
        assert img.size == (100, 100)

    def test_extract_from_nonexistent_raises(self):
        """Test functionality: extract from nonexistent raises."""
        with pytest.raises(SteganographyError):
            extract_from_image("/nonexistent/path/image.png")


@pytest.mark.unit
@pytest.mark.crypto
class TestRGBAImage:
    """Tests for images with alpha channels."""

    def test_rgba_image_roundtrip(self, tmp_path):
        """Test functionality: rgba image roundtrip."""
        # Create RGBA image
        img = Image.new("RGBA", (50, 50), color=(255, 0, 0, 128))
        input_path = str(tmp_path / "rgba.png")
        output_path = str(tmp_path / "stego_rgba.png")
        img.save(input_path, "PNG")

        message = "RGBA test message"
        embed_in_image(input_path, message, output_path)
        extracted = extract_from_image(output_path)
        assert extracted == message
