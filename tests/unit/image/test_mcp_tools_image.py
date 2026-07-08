"""Tests for image MCP tools.

Zero-mock tests that exercise the image format detection, file info,
and format listing tools using real temporary files.
"""

from __future__ import annotations

from codomyrmex.image.mcp_tools import (
    image_detect_format,
    image_file_info,
    image_list_formats,
)


class TestImageDetectFormat:
    """Tests for image_detect_format."""

    def test_detect_png(self, tmp_path):
        """Detect a file with a PNG magic number."""
        png_file = tmp_path / "test.png"
        # Minimal PNG header
        png_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 24)
        result = image_detect_format(str(png_file))
        assert result["status"] == "success"
        assert result["format"] == "png"

    def test_detect_jpeg(self, tmp_path):
        """Detect a file with a JPEG magic number."""
        jpeg_file = tmp_path / "test.jpg"
        jpeg_file.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 28)
        result = image_detect_format(str(jpeg_file))
        assert result["status"] == "success"
        assert result["format"] == "jpeg"

    def test_detect_unknown(self, tmp_path):
        """Return 'unknown' for non-image binary."""
        bin_file = tmp_path / "test.bin"
        bin_file.write_bytes(b"\x00\x01\x02\x03" * 8)
        result = image_detect_format(str(bin_file))
        assert result["status"] == "success"
        assert result["format"] == "unknown"

    def test_file_not_found(self):
        """Error for non-existent file."""
        result = image_detect_format("/nonexistent/path/foo.png")
        assert result["status"] == "error"
        assert (
            "not found" in result["message"].lower()
            or "File not found" in result["message"]
        )

    def test_detect_gif(self, tmp_path):
        """Detect a GIF89a header."""
        gif_file = tmp_path / "test.gif"
        gif_file.write_bytes(b"GIF89a" + b"\x00" * 26)
        result = image_detect_format(str(gif_file))
        assert result["status"] == "success"
        assert result["format"] == "gif"


class TestImageFileInfo:
    """Tests for image_file_info."""

    def test_existing_file(self, tmp_path):
        """Return metadata for an existing file."""
        img = tmp_path / "photo.jpeg"
        img.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
        result = image_file_info(str(img))
        assert result["status"] == "success"
        assert result["exists"] is True
        assert result["size_bytes"] == 104
        assert result["extension"] == "jpeg"

    def test_nonexistent_file(self):
        """Return exists=False for missing file."""
        result = image_file_info("/tmp/does_not_exist_abc123.png")
        assert result["status"] == "success"
        assert result["exists"] is False
        assert result["size_bytes"] == 0

    def test_no_extension(self, tmp_path):
        """Handle file without extension."""
        f = tmp_path / "noext"
        f.write_bytes(b"\x00")
        result = image_file_info(str(f))
        assert result["status"] == "success"
        assert result["extension"] == ""


class TestImageListFormats:
    """Tests for image_list_formats."""

    def test_returns_sorted_formats(self):
        """Formats are returned sorted and non-empty."""
        result = image_list_formats()
        assert result["status"] == "success"
        assert isinstance(result["formats"], list)
        assert len(result["formats"]) >= 4
        assert result["formats"] == sorted(result["formats"])

    def test_known_formats_present(self):
        """Known formats appear in the list."""
        result = image_list_formats()
        formats = result["formats"]
        assert "png" in formats
        assert "jpeg" in formats
        assert "gif" in formats
