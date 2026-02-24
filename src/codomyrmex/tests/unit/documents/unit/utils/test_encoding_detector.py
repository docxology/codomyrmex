"""Zero-Mock tests for encoding detector — uses real file I/O via tmp_path."""

import pytest

from codomyrmex.documents.utils.encoding_detector import detect_encoding


@pytest.mark.unit
class TestEncodingDetector:
    """Test suite for EncodingDetector."""
    def test_detect_encoding_utf8_bom(self, tmp_path):
        """Test detecting UTF-8 with BOM from a real file."""
        f = tmp_path / "bom.txt"
        f.write_bytes(b"\xef\xbb\xbfcontent")

        enc = detect_encoding(str(f))
        assert enc.upper().replace("-", "") in ("UTF8SIG", "UTF8", "UTF-8-SIG", "UTF-8")

    def test_detect_encoding_plain_ascii(self, tmp_path):
        """Test detecting plain ASCII encoding from a real file."""
        f = tmp_path / "ascii.txt"
        f.write_bytes(b"hello world")

        enc = detect_encoding(str(f))
        assert enc is not None
        # ASCII content is typically detected as ASCII or UTF-8
        assert enc.upper() in ("ASCII", "UTF-8", "UTF8")

    def test_detect_encoding_utf8(self, tmp_path):
        """Test detecting UTF-8 with non-ASCII characters."""
        f = tmp_path / "utf8.txt"
        f.write_text("héllo wörld", encoding="utf-8")

        enc = detect_encoding(str(f))
        assert enc is not None
        assert "UTF" in enc.upper() or "utf" in enc.lower()
