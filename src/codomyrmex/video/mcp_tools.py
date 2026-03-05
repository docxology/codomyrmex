"""MCP tool definitions for the video module.

Exposes video configuration management and format listing as MCP tools.
Video processing tools require optional dependencies (moviepy, opencv-python).
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_config():
    """Lazy import of video config functions."""
    from codomyrmex.video.config import VideoConfig, get_config

    return VideoConfig, get_config


def _get_models():
    """Lazy import of video model enums."""
    from codomyrmex.video.models import AudioCodec, FilterType, VideoCodec

    return VideoCodec, AudioCodec, FilterType


@mcp_tool(
    category="video",
    description="Get current video processing configuration and validate it.",
)
def video_get_config() -> dict[str, Any]:
    """Return current video processing configuration.

    Returns:
        dict with keys: status, config, issues
    """
    try:
        _VideoConfig, get_config = _get_config()
        config = get_config()
        issues = config.validate()
        return {
            "status": "success",
            "config": config.to_dict(),
            "issues": issues,
            "valid": len(issues) == 0,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="List supported video codecs, audio codecs, and filter types.",
)
def video_list_formats() -> dict[str, Any]:
    """List all supported video formats, codecs, and filters.

    Returns:
        dict with keys: status, video_codecs, audio_codecs, filters
    """
    try:
        VideoCodec, AudioCodec, FilterType = _get_models()
        return {
            "status": "success",
            "video_codecs": [{"name": vc.name, "value": vc.value} for vc in VideoCodec],
            "audio_codecs": [{"name": ac.name, "value": ac.value} for ac in AudioCodec],
            "filters": [{"name": ft.name, "value": ft.value} for ft in FilterType],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Check video module availability: which processing backends are installed.",
)
def video_check_availability() -> dict[str, Any]:
    """Check which video processing backends are available.

    Returns:
        dict with keys: status, processing, extraction, analysis, moviepy, opencv, pil
    """
    try:
        from codomyrmex.video import (
            ANALYSIS_AVAILABLE,
            EXTRACTION_AVAILABLE,
            MOVIEPY_AVAILABLE,
            OPENCV_AVAILABLE,
            PIL_AVAILABLE,
            PROCESSING_AVAILABLE,
        )

        return {
            "status": "success",
            "processing": PROCESSING_AVAILABLE,
            "extraction": EXTRACTION_AVAILABLE,
            "analysis": ANALYSIS_AVAILABLE,
            "moviepy": MOVIEPY_AVAILABLE,
            "opencv": OPENCV_AVAILABLE,
            "pil": PIL_AVAILABLE,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
