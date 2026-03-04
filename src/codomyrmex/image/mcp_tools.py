"""MCP tool definitions for the image module.

Exposes image metadata extraction and format information as MCP tools.
"""

from __future__ import annotations

import os
from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _read_file_bytes(path: str, max_bytes: int = 32) -> bytes:
    """Read the first *max_bytes* of a file for header inspection."""
    with open(path, "rb") as fh:
        return fh.read(max_bytes)


# ── Format signatures ───────────────────────────────────────────────
_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"RIFF", "webp"),  # first 4 bytes; need "WEBP" at offset 8
    (b"BM", "bmp"),
    (b"II\x2a\x00", "tiff"),
    (b"MM\x00\x2a", "tiff"),
]


@mcp_tool(
    category="image",
    description="Detect image format from file header bytes (magic number detection).",
)
def image_detect_format(file_path: str) -> dict[str, Any]:
    """Detect the image format of a file by inspecting its header bytes.

    Args:
        file_path: Absolute path to the image file.

    Returns:
        dict with keys: status, format, file_path
    """
    try:
        if not os.path.isfile(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        header = _read_file_bytes(file_path, max_bytes=32)
        detected = "unknown"
        for sig, fmt in _SIGNATURES:
            if header[: len(sig)] == sig:
                # Extra check for WEBP (RIFF....WEBP)
                if fmt == "webp" and header[8:12] != b"WEBP":
                    continue
                detected = fmt
                break

        return {"status": "success", "format": detected, "file_path": file_path}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="image",
    description="Get basic file metadata for an image (size, extension, existence).",
)
def image_file_info(file_path: str) -> dict[str, Any]:
    """Return basic file-level metadata for an image path.

    Args:
        file_path: Absolute path to the image file.

    Returns:
        dict with keys: status, file_path, exists, size_bytes, extension
    """
    try:
        exists = os.path.isfile(file_path)
        if not exists:
            return {
                "status": "success",
                "file_path": file_path,
                "exists": False,
                "size_bytes": 0,
                "extension": "",
            }
        stat = os.stat(file_path)
        _, ext = os.path.splitext(file_path)
        return {
            "status": "success",
            "file_path": file_path,
            "exists": True,
            "size_bytes": stat.st_size,
            "extension": ext.lstrip(".").lower(),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="image",
    description="List supported image formats recognized by the detect_format tool.",
)
def image_list_formats() -> dict[str, Any]:
    """List all image formats the detection engine can identify.

    Returns:
        dict with keys: status, formats
    """
    try:
        formats = sorted({fmt for _, fmt in _SIGNATURES})
        return {"status": "success", "formats": formats}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
