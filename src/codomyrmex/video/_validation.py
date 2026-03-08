"""Shared validation utilities for the video module."""

from __future__ import annotations

from pathlib import Path

from codomyrmex.video.exceptions import UnsupportedFormatError, VideoReadError

SUPPORTED_FORMATS: frozenset[str] = frozenset(
    {".mp4", ".avi", ".mov", ".mkv", ".webm", ".wmv", ".flv", ".m4v"}
)


def validate_video_path(video_path: str | Path) -> Path:
    """Validate that a video path exists and is a supported format.

    Args:
        video_path: Path to validate.

    Returns:
        Validated Path object.

    Raises:
        VideoReadError: If the file does not exist.
        UnsupportedFormatError: If the format is not supported.
    """
    path = Path(video_path)

    if not path.exists():
        raise VideoReadError(f"Video file not found: {path}", video_path=path)

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(
            f"Unsupported format: {path.suffix}",
            format_type=path.suffix,
            supported_formats=list(SUPPORTED_FORMATS),
        )

    return path
