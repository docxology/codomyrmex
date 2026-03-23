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
    description="list supported video codecs, audio codecs, and filter types.",
)
def video_list_formats() -> dict[str, Any]:
    """list all supported video formats, codecs, and filters.

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


# ── Universal Video Transcriber tools ─────────────────────────────────


@mcp_tool(
    category="video",
    description=(
        "Transcribe any video URL to timestamped text using the "
        "nativ3ai/universal-video-transcriber pipeline: "
        "URL → yt-dlp → ffmpeg → faster-whisper → JSON. "
        "Supports YouTube, X/Twitter, Vimeo, Reddit, and any yt-dlp-compatible site."
    ),
)
def video_transcribe_url(
    url: str,
    model_size: str = "small",
    language: str | None = None,
    word_timestamps: bool = True,
    persist_media: bool = False,
    cookies_from_browser: str | None = None,
    mode: str = "auto",
) -> dict[str, Any]:
    """Transcribe a video URL.

    Args:
        url: Any URL resolvable by yt-dlp (YouTube, X, Vimeo, etc.).
        model_size: Whisper model size: ``"tiny"``, ``"base"``, ``"small"``
            (default), ``"medium"``, ``"large-v2"``, ``"large-v3"``.
        language: Force language code e.g. ``"en"`` (None = auto-detect).
        word_timestamps: Include word-level timing (default True).
        persist_media: Keep downloaded media after transcription.
        cookies_from_browser: Use cookies from ``"chrome"``, ``"firefox"``,
            or ``"safari"`` for auth-gated videos.
        mode: ``"auto"`` (default), ``"cli"``, or ``"rest"``.

    Returns:
        dict matching upstream JSON schema: source_url, platform, title,
        duration_sec, language, transcript, segments, metadata, status.

    """
    try:
        from codomyrmex.video.transcription import VideoTranscriber

        t = VideoTranscriber(mode=mode)
        return t.transcribe_to_dict(
            url,
            model_size=model_size,
            language=language,
            word_timestamps=word_timestamps,
            persist_media=persist_media,
            cookies_from_browser=cookies_from_browser,
        )
    except Exception as exc:
        return {"status": "error", "source_url": url, "message": str(exc)}


@mcp_tool(
    category="video",
    description=(
        "Check that universal-video-transcriber dependencies are ready: "
        "yt-dlp, ffmpeg, faster-whisper, the transcriber script, and optionally "
        "the REST API server."
    ),
)
def video_transcriber_doctor(mode: str = "auto") -> dict[str, Any]:
    """Run a dependency doctor check for the video transcriber.

    Args:
        mode: ``"auto"`` (default), ``"cli"``, or ``"rest"``.

    Returns:
        dict with keys: ok, mode, dependencies, message.

    """
    try:
        from codomyrmex.video.transcription import VideoTranscriber

        t = VideoTranscriber(mode=mode)
        return t.doctor()
    except Exception as exc:
        return {"ok": False, "mode": mode, "message": str(exc)}


@mcp_tool(
    category="video",
    description=(
        "list available Whisper model sizes for video transcription, "
        "ordered from smallest/fastest to largest/most accurate."
    ),
)
def video_transcriber_list_models() -> dict[str, Any]:
    """list available Whisper model sizes.

    Returns:
        dict with keys: status, models (list), recommended.

    """
    try:
        from codomyrmex.video.transcription import WHISPER_MODELS

        return {
            "status": "success",
            "models": list(WHISPER_MODELS),
            "recommended": "small",
            "note": (
                "'small' provides good speed/accuracy balance. "
                "Use 'medium' or 'large-v3' for highest accuracy."
            ),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
