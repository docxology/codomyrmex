"""Compression utilities.

This module provides data compression and decompression utilities supporting:
- gzip compression with configurable levels
- zlib compression for raw deflate
- ZIP archive creation and extraction
- Stream-based compression
- Automatic format detection via magic bytes
"""
import gzip
import os
import zipfile
import zlib
from io import BytesIO
from typing import IO

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class CompressionError(CodomyrmexError):
    """Raised when compression operations fail."""

    pass


class Compressor:
    """Compressor for various formats.

    Supports gzip, zlib, and ZIP formats with configurable compression levels.
    """

    SUPPORTED_FORMATS = {"gzip", "zlib", "zip"}

    def __init__(self, format: str = "gzip"):
        """Initialize compressor.

        Args:
            format: Compression format (gzip, zlib, zip)

        Raises:
            ValueError: If format is not supported
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Use one of: {self.SUPPORTED_FORMATS}")
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

    def detect_format(self, data: bytes) -> str | None:
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

    # --- File Utilities ---

    def compress_file(self, input_path: str, output_path: str | None = None, level: int = 6) -> str:
        """Compress a file.

        Args:
            input_path: Path to input file
            output_path: Path to output file (defaults to input_path + extension)
            level: Compression level

        Returns:
            Path to compressed file

        Raises:
            CompressionError: If compression fails
        """
        try:
            ext_map = {"gzip": ".gz", "zlib": ".zlib", "zip": ".zip"}
            if output_path is None:
                output_path = input_path + ext_map.get(self.format, ".compressed")

            with open(input_path, "rb") as f:
                data = f.read()

            compressed = self.compress(data, level)

            with open(output_path, "wb") as f:
                f.write(compressed)

            original_size = os.path.getsize(input_path)
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

            logger.info(f"Compressed {input_path} -> {output_path} ({ratio:.1f}% reduction)")
            return output_path
        except Exception as e:
            logger.error(f"File compression error: {e}")
            raise CompressionError(f"Failed to compress file: {str(e)}") from e

    def decompress_file(self, input_path: str, output_path: str | None = None) -> str:
        """Decompress a file.

        Args:
            input_path: Path to compressed file
            output_path: Path to output file (defaults to removing extension)

        Returns:
            Path to decompressed file

        Raises:
            CompressionError: If decompression fails
        """
        try:
            if output_path is None:
                # Remove common compression extensions
                for ext in [".gz", ".gzip", ".zlib", ".zip", ".compressed"]:
                    if input_path.endswith(ext):
                        output_path = input_path[:-len(ext)]
                        break
                else:
                    output_path = input_path + ".decompressed"

            with open(input_path, "rb") as f:
                data = f.read()

            decompressed = self.decompress(data)

            with open(output_path, "wb") as f:
                f.write(decompressed)

            logger.info(f"Decompressed {input_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"File decompression error: {e}")
            raise CompressionError(f"Failed to decompress file: {str(e)}") from e

    @staticmethod
    def get_compression_ratio(original: bytes, compressed: bytes) -> float:
        """Calculate compression ratio.

        Args:
            original: Original data
            compressed: Compressed data

        Returns:
            Compression ratio as percentage reduction (0-100)
        """
        if len(original) == 0:
            return 0.0
        return (1 - len(compressed) / len(original)) * 100


# Convenience functions
def compress_data(data: bytes, format: str = "gzip", level: int = 6) -> bytes:
    """Compress data using specified format.

    Args:
        data: Data to compress
        format: Compression format (gzip, zlib, zip)
        level: Compression level (0-9)

    Returns:
        Compressed data
    """
    return Compressor(format).compress(data, level)


def decompress_data(data: bytes, format: str = "gzip") -> bytes:
    """Decompress data using specified format.

    Args:
        data: Compressed data
        format: Compression format (gzip, zlib, zip)

    Returns:
        Decompressed data
    """
    return Compressor(format).decompress(data)


def auto_decompress(data: bytes) -> bytes:
    """Automatically detect format and decompress.

    Args:
        data: Compressed data

    Returns:
        Decompressed data

    Raises:
        CompressionError: If format cannot be detected
    """
    compressor = Compressor()
    detected = compressor.detect_format(data)
    if detected is None:
        raise CompressionError("Unable to detect compression format")
    return Compressor(detected).decompress(data)


def compare_formats(data: bytes, level: int = 6) -> dict[str, dict[str, float]]:
    """
    Compare compression across all supported formats.

    Args:
        data: Data to compress
        level: Compression level

    Returns:
        Dict with format -> {compressed_size, ratio, time_ms}
    """
    import time

    results = {}
    original_size = len(data)

    for fmt in Compressor.SUPPORTED_FORMATS:
        compressor = Compressor(fmt)
        start = time.time()
        try:
            compressed = compressor.compress(data, level)
            elapsed = (time.time() - start) * 1000
            ratio = (1 - len(compressed) / original_size) * 100 if original_size > 0 else 0
            results[fmt] = {
                "compressed_size": len(compressed),
                "ratio": round(ratio, 2),
                "time_ms": round(elapsed, 2),
            }
        except Exception as e:
            results[fmt] = {"error": str(e)}

    return results
