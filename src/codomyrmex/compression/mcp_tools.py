"""MCP tool definitions for the compression module.

Exposes data compression, decompression, and format comparison as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_compressor():
    """Lazy import of Compressor to avoid circular deps."""
    from codomyrmex.compression.core.compressor import Compressor

    return Compressor


def _get_compare_formats():
    """Lazy import of compare_formats to avoid circular deps."""
    from codomyrmex.compression.core.compressor import compare_formats

    return compare_formats


@mcp_tool(
    category="compression",
    description="Compress data using gzip, zlib, or zip format and return base64-encoded result.",
)
def compression_compress(
    data: str,
    format: str = "gzip",
    level: int = 6,
) -> dict[str, Any]:
    """Compress a UTF-8 string and return base64-encoded compressed bytes.

    Args:
        data: The text data to compress.
        format: Compression format - 'gzip', 'zlib', or 'zip' (default 'gzip').
        level: Compression level 0-9, higher means more compression (default 6).

    Returns:
        dict with status, compressed_size, original_size, ratio, and compressed_b64.
    """
    import base64

    try:
        Compressor = _get_compressor()
        compressor = Compressor(format=format)
        raw = data.encode("utf-8")
        compressed = compressor.compress(raw, level)
        ratio = Compressor.get_compression_ratio(raw, compressed)

        return {
            "status": "success",
            "original_size": len(raw),
            "compressed_size": len(compressed),
            "ratio": round(ratio, 2),
            "format": format,
            "compressed_b64": base64.b64encode(compressed).decode("ascii"),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="compression",
    description="Detect compression format from base64-encoded data using magic bytes.",
)
def compression_detect_format(
    data_b64: str,
) -> dict[str, Any]:
    """Detect the compression format of base64-encoded data.

    Args:
        data_b64: Base64-encoded compressed data.

    Returns:
        dict with status and detected format (or null if unknown).
    """
    import base64

    try:
        Compressor = _get_compressor()
        raw = base64.b64decode(data_b64)
        compressor = Compressor()
        detected = compressor.detect_format(raw)

        return {
            "status": "success",
            "detected_format": detected,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="compression",
    description="Compare compression ratios and speed across all supported formats.",
)
def compression_compare_formats(
    data: str,
    level: int = 6,
) -> dict[str, Any]:
    """Compare compression performance across gzip, zlib, and zip for given text.

    Args:
        data: The text data to compress for comparison.
        level: Compression level 0-9 (default 6).

    Returns:
        dict with status, original_size, and per-format results (compressed_size, ratio, time_ms).
    """
    try:
        compare = _get_compare_formats()
        raw = data.encode("utf-8")
        results = compare(raw, level=level)

        return {
            "status": "success",
            "original_size": len(raw),
            "formats": results,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
