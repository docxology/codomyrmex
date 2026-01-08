from typing import IO, Optional

from io import BytesIO
import gzip
import zipfile
import zipfile
import zlib

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger




























































"""
"""Core functionality module

This module provides compressor functionality including:
- 6 functions: __init__, compress, decompress...
- 2 classes: CompressionError, Compressor

Usage:
    # Example usage here
"""
Compression utilities.
"""



logger = get_logger(__name__)


class CompressionError(CodomyrmexError):
    """Raised when compression operations fail."""

    pass


class Compressor:
    """Compressor for various formats."""

    def __init__(self, format: str = "gzip"):
        """Initialize compressor.

        Args:
            format: Compression format (gzip, zlib, zip)
        """
        self.format = format

    def compress(self, data: bytes, level: int = 6) -> bytes:
        """Compress data using the configured format.

        Args:
            data: Data to compress
            level: Compression level (0-9, higher = more compression)

        Returns:
            Compressed data

        Raises:
            CompressionError: If compression fails
        """
        try:
            if self.format == "gzip":
                return gzip.compress(data, compresslevel=level)
            elif self.format == "zlib":
                return zlib.compress(data, level=level)
            elif self.format == "zip":
                buffer = BytesIO()
                with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=level) as zf:
                    zf.writestr("data", data)
                return buffer.getvalue()
            else:
                raise ValueError(f"Unknown format: {self.format}")
        except Exception as e:
            logger.error(f"Compression error: {e}")
            raise CompressionError(f"Failed to compress: {str(e)}") from e

    def decompress(self, data: bytes) -> bytes:
        """Decompress data using the configured format.

        Args:
            data: Compressed data

        Returns:
            Decompressed data

        Raises:
            CompressionError: If decompression fails
        """
        try:
            if self.format == "gzip":
                return gzip.decompress(data)
            elif self.format == "zlib":
                return zlib.decompress(data)
            elif self.format == "zip":
                with zipfile.ZipFile(BytesIO(data), "r") as zf:
                    return zf.read("data")
            else:
                raise ValueError(f"Unknown format: {self.format}")
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            raise CompressionError(f"Failed to decompress: {str(e)}") from e

    def compress_stream(self, input_stream: IO[bytes], output_stream: IO[bytes], level: int = 6) -> None:
        """Compress data from input stream to output stream.

        Args:
            input_stream: Input stream
            output_stream: Output stream
            level: Compression level
        """
        data = input_stream.read()
        compressed = self.compress(data, level)
        output_stream.write(compressed)

    def decompress_stream(self, input_stream: IO[bytes], output_stream: IO[bytes]) -> None:
        """Decompress data from input stream to output stream.

        Args:
            input_stream: Input stream
            output_stream: Output stream
        """
        data = input_stream.read()
        decompressed = self.decompress(data)
        output_stream.write(decompressed)

    def detect_format(self, data: bytes) -> Optional[str]:
        """Detect compression format from data.

        Args:
            data: Compressed data

        Returns:
            Format name if detected, None otherwise
        """
        # Check magic bytes
        if data.startswith(b"\x1f\x8b"):
            return "gzip"
        elif data.startswith(b"PK"):
            return "zip"
        elif len(data) > 2 and data[:2] in [b"\x78\x01", b"\x78\x9c", b"\x78\xda"]:
            return "zlib"
        return None


