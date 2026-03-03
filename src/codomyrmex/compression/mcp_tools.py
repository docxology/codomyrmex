"""MCP tools for the compression module.

Exposes data compression, decompression, and statistics comparison
as auto-discovered MCP tools.
"""

from __future__ import annotations

import base64

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="compression",
    description=(
        "Compress a base64 encoded string or a plain text string. "
        "Returns base64 encoded compressed data."
    ),
)
def compression_compress_data(
    data: str, is_base64: bool = False, format: str = "gzip", level: int = 6
) -> dict:
    """Compress data and return it as base64.

    Args:
        data: The string to compress.
        is_base64: Whether the input string is already base64 encoded bytes.
        format: The compression format (e.g., 'gzip', 'zlib', 'zip', 'zstd').
        level: Compression level.

    Returns:
        Dictionary with 'compressed_base64' and 'format'.
    """
    from codomyrmex.compression import compress

    try:
        if is_base64:
            raw_bytes = base64.b64decode(data)
        else:
            raw_bytes = data.encode("utf-8")

        compressed_bytes = compress(raw_bytes, format=format, level=level)
        return {
            "compressed_base64": base64.b64encode(compressed_bytes).decode("utf-8"),
            "format": format,
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="compression",
    description=(
        "Decompress a base64 encoded compressed string. "
        "Returns the decompressed data as a string (utf-8) or base64."
    ),
)
def compression_decompress_data(
    compressed_base64: str, format: str = "gzip", return_base64: bool = False
) -> dict:
    """Decompress base64 encoded data.

    Args:
        compressed_base64: The base64 encoded compressed data.
        format: The format to use for decompression.
        return_base64: If True, returns decompressed data as base64 instead of utf-8 string.

    Returns:
        Dictionary with 'decompressed' or 'error'.
    """
    from codomyrmex.compression import decompress

    try:
        compressed_bytes = base64.b64decode(compressed_base64)
        decompressed_bytes = decompress(compressed_bytes, format=format)

        if return_base64:
            return {
                "decompressed_base64": base64.b64encode(decompressed_bytes).decode(
                    "utf-8"
                )
            }
        else:
            return {"decompressed_text": decompressed_bytes.decode("utf-8")}

    except UnicodeDecodeError:
        # If it's not valid utf-8, fallback to base64
        return {
            "decompressed_base64": base64.b64encode(decompressed_bytes).decode("utf-8"),
            "warning": "Data is not valid UTF-8, returned as base64",
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="compression",
    description=(
        "Compare compression across formats for a given string. "
        "Returns statistics like size, ratio, and time for each format."
    ),
)
def compression_get_stats(data: str, is_base64: bool = False, level: int = 6) -> dict:
    """Get compression statistics for given data.

    Args:
        data: The string to test compression on.
        is_base64: Whether the input string is base64 encoded.
        level: The compression level to use.

    Returns:
        Dictionary of format statistics.
    """
    from codomyrmex.compression.core.compressor import compare_formats

    try:
        if is_base64:
            raw_bytes = base64.b64decode(data)
        else:
            raw_bytes = data.encode("utf-8")

        stats = compare_formats(raw_bytes, level=level)
        return {"stats": stats}
    except Exception as exc:
        return {"error": str(exc)}
