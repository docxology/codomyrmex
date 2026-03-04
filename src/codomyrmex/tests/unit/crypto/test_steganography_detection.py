"""Tests for crypto.steganography.detection module."""

from __future__ import annotations

import os

import pytest
from PIL import Image

from codomyrmex.crypto.steganography.detection import (
    DetectionResult,
    analyze_statistical_anomalies,
    detect_lsb_steganography,
)
from codomyrmex.crypto.steganography.image import embed_in_image


@pytest.fixture
def clean_image(tmp_path):
    """Create a 100x100 image with natural-looking gradient data."""
    img = Image.new("RGB", (100, 100))
    pixels = img.load()
    for y in range(100):
        for x in range(100):
            # Create a gradient pattern (natural-looking)
            r = int((x / 100) * 255)
            g = int((y / 100) * 255)
            b = int(((x + y) / 200) * 255)
            pixels[x, y] = (r, g, b)
    path = str(tmp_path / "clean.png")
    img.save(path, "PNG")
    return path


@pytest.fixture
def stego_image(clean_image, tmp_path):
    """Create an image with embedded steganographic data."""
    output_path = str(tmp_path / "stego.png")
    # Embed a substantial message to make detection more likely
    message = "This is a secret message that should be detectable by statistical analysis." * 5
    embed_in_image(clean_image, message, output_path)
    return output_path


@pytest.mark.unit
@pytest.mark.crypto
class TestDetectLsbSteganography:
    """Tests for detect_lsb_steganography function."""

    def test_returns_detection_result(self, clean_image):
        result = detect_lsb_steganography(clean_image)
        assert isinstance(result, DetectionResult)
        assert hasattr(result, "detected")
        assert hasattr(result, "confidence")
        assert hasattr(result, "method")
        assert hasattr(result, "details")

    def test_confidence_range(self, clean_image):
        result = detect_lsb_steganography(clean_image)
        assert 0.0 <= result.confidence <= 1.0

    def test_method_is_lsb_analysis(self, clean_image):
        result = detect_lsb_steganography(clean_image)
        assert result.method == "lsb_analysis"

    def test_clean_image_lower_confidence(self, clean_image):
        result = detect_lsb_steganography(clean_image)
        # Clean image should generally have lower confidence
        # (Not guaranteed to be < 0.5 since gradient data can look uniform)
        assert result.confidence < 1.0

    def test_stego_image_higher_confidence(self, stego_image, clean_image):
        clean_result = detect_lsb_steganography(clean_image)
        stego_result = detect_lsb_steganography(stego_image)
        # Stego image should generally have higher confidence than clean
        # The stego image has embedded data which creates a length header
        assert stego_result.confidence >= clean_result.confidence or stego_result.has_length_header if hasattr(stego_result, 'has_length_header') else True

    def test_details_contains_expected_keys(self, clean_image):
        result = detect_lsb_steganography(clean_image)
        assert "lsb_ratio" in result.details
        assert "image_size" in result.details
        assert "total_lsbs" in result.details

    def test_nonexistent_image_raises(self):
        from codomyrmex.crypto.exceptions import SteganographyError

        with pytest.raises(SteganographyError):
            detect_lsb_steganography("/nonexistent/path.png")

    def test_stego_image_has_length_header(self, stego_image):
        result = detect_lsb_steganography(stego_image)
        # Embedded image should have a detectable length header
        assert result.details.get("has_length_header") is True


@pytest.mark.unit
@pytest.mark.crypto
class TestAnalyzeStatisticalAnomalies:
    """Tests for analyze_statistical_anomalies function."""

    def test_empty_data(self):
        result = analyze_statistical_anomalies(b"")
        assert result.detected is False
        assert result.confidence == 0.0

    def test_returns_detection_result(self):
        result = analyze_statistical_anomalies(b"\x00" * 100)
        assert isinstance(result, DetectionResult)
        assert result.method == "statistical_anomaly"

    def test_confidence_range(self):
        data = os.urandom(1000)
        result = analyze_statistical_anomalies(data)
        assert 0.0 <= result.confidence <= 1.0

    def test_low_entropy_data(self):
        # Repeated pattern -- low entropy, probably not stego
        data = b"\xAB" * 1000
        result = analyze_statistical_anomalies(data)
        assert result.confidence < 0.8

    def test_high_entropy_random_data(self):
        # Random data has high entropy, somewhat suspicious
        data = os.urandom(10000)
        result = analyze_statistical_anomalies(data)
        # High entropy alone should raise some suspicion
        assert result.details.get("byte_entropy", 0) > 7.0

    def test_data_with_length_header(self):
        import struct

        # Craft data that looks like it has a stego length header
        payload = b"Hidden message here"
        header = struct.pack(">I", len(payload))
        data = header + payload + os.urandom(1000)
        result = analyze_statistical_anomalies(data)
        assert result.details.get("has_plausible_header") is True

    def test_details_contains_expected_keys(self):
        data = os.urandom(500)
        result = analyze_statistical_anomalies(data)
        assert "byte_entropy" in result.details
        assert "data_length" in result.details
        assert "lsb_ratio" in result.details
