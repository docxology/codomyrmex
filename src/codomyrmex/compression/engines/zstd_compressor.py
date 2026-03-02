"""High-performance Zstd compressor."""

import logging

logger = logging.getLogger(__name__)

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

class ZstdCompressor:
    """Compressor using the Zstandard algorithm."""

    def __init__(self, level: int = 3):
        """Initialize this instance."""
        if not ZSTD_AVAILABLE:
            raise ImportError("zstandard package not available. Install with: pip install zstandard")
        self.level = level
        self.cctx = zstd.ZstdCompressor(level=level)
        self.dctx = zstd.ZstdDecompressor()

    def compress(self, data: bytes, level: int | None = None) -> bytes:
        """Compress data using Zstd.

        Args:
            data: Raw bytes to compress.
            level: Optional compression level override (1-22).
        """
        if level is not None and level != self.level:
            ctx = zstd.ZstdCompressor(level=level)
            return ctx.compress(data)
        return self.cctx.compress(data)

    def decompress(self, data: bytes) -> bytes:
        """Decompress data using Zstd."""
        return self.dctx.decompress(data)
