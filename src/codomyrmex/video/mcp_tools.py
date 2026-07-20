"""MCP tool definitions for the video module.

Exposes video configuration management and format listing as MCP tools.
Video processing tools require optional dependencies (moviepy, opencv-python).
"""

from __future__ import annotations

from collections.abc import Sequence
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


# ── Video processing / extraction / analysis tools ──────────────────────


@mcp_tool(
    category="video",
    description=(
        "Process a video file with operations: resize, crop, rotate, trim, "
        "convert, or apply a visual filter. Requires moviepy backend."
    ),
)
def video_process(
    video_path: str,
    operation: str,
    output_path: str | None = None,
    width: int | None = None,
    height: int | None = None,
    x: int | None = None,
    y: int | None = None,
    angle: float | None = None,
    start: float | None = None,
    end: float | None = None,
    filter_type: str | None = None,
    output_format: str | None = None,
    intensity: float = 1.0,
) -> dict[str, Any]:
    """Process a video file with the specified operation.

    Args:
        video_path: Path to the input video file.
        operation: One of ``"resize"``, ``"crop"``, ``"rotate"``,
            ``"trim"``, ``"filter"``, ``"convert"``.
        output_path: Path for output video (auto-generated if not provided).
        width: Target width for resize/crop.
        height: Target height for resize/crop.
        x: Left edge for crop.
        y: Top edge for crop.
        angle: Rotation angle in degrees (for rotate).
        start: Start time in seconds (for trim).
        end: End time in seconds (for trim).
        filter_type: Filter name for filter operation
            (grayscale, blur, sharpen, brightness, contrast, saturation,
            sepia, invert, mirror_horizontal, mirror_vertical,
            rotate_90, rotate_180, rotate_270).
        output_format: Target format for convert (e.g. ``"mp4"``).
        intensity: Filter intensity (0.0–2.0, for filter operation).

    Returns:
        dict with keys: status, result (output_path, duration, file_size,
        width, height, operation, processing_time).
    """
    try:
        from codomyrmex.video.models import FilterType
        from codomyrmex.video.processing import VideoProcessor

        processor = VideoProcessor()

        if operation == "resize":
            if width is None or height is None:
                return {
                    "status": "error",
                    "message": "resize requires width and height",
                }
            result = processor.resize(
                video_path,
                width=width,
                height=height,
                output_path=output_path,
            )
        elif operation == "crop":
            if width is None or height is None or x is None or y is None:
                return {
                    "status": "error",
                    "message": "crop requires x, y, width, height",
                }
            result = processor.crop(
                video_path,
                x=x,
                y=y,
                width=width,
                height=height,
                output_path=output_path,
            )
        elif operation == "rotate":
            if angle is None:
                return {"status": "error", "message": "rotate requires angle"}
            result = processor.rotate(
                video_path,
                angle=angle,
                output_path=output_path,
            )
        elif operation == "trim":
            if start is None or end is None:
                return {
                    "status": "error",
                    "message": "trim requires start and end",
                }
            result = processor.trim(
                video_path,
                start=start,
                end=end,
                output_path=output_path,
            )
        elif operation == "filter":
            if filter_type is None:
                return {
                    "status": "error",
                    "message": "filter requires filter_type",
                }
            try:
                ft = FilterType(filter_type)
            except ValueError:
                valid = [f.value for f in FilterType]
                return {
                    "status": "error",
                    "message": f"Unknown filter_type '{filter_type}'. Valid: {valid}",
                }
            result = processor.apply_filter(
                video_path,
                filter_type=ft,
                intensity=intensity,
                output_path=output_path,
            )
        elif operation == "convert":
            if output_format is None:
                return {
                    "status": "error",
                    "message": "convert requires output_format",
                }
            result = processor.convert(
                video_path,
                output_format=output_format,
                output_path=output_path,
            )
        else:
            return {
                "status": "error",
                "message": (
                    f"Unknown operation '{operation}'. Valid: resize, crop, "
                    "rotate, trim, filter, convert"
                ),
            }

        return {"status": "success", "result": result.to_dict()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Extract a single frame from a video at a specified timestamp.",
)
def video_extract_frame(
    video_path: str,
    timestamp: float,
    output_path: str,
    format: str = "png",
) -> dict[str, Any]:
    """Extract a single frame from a video.

    Args:
        video_path: Path to the video file.
        timestamp: Time in seconds to extract the frame.
        output_path: Path to save the frame image.
        format: Output image format (png, jpg, webp). Default ``"png"``.

    Returns:
        dict with keys: status, output_path, timestamp, width, height.
    """
    try:
        from codomyrmex.video.extraction import FrameExtractor

        extractor = FrameExtractor()
        frame = extractor.extract_frame(video_path, timestamp=timestamp)
        frame.save(output_path, format=format.upper())

        return {
            "status": "success",
            "output_path": output_path,
            "timestamp": timestamp,
            "width": frame.width,
            "height": frame.height,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Extract multiple frames from a video at regular intervals.",
)
def video_extract_frames(
    video_path: str,
    interval: float,
    output_directory: str,
    start: float = 0.0,
    end: float | None = None,
    format: str = "png",
    prefix: str = "frame",
) -> dict[str, Any]:
    """Extract multiple frames at regular intervals.

    Args:
        video_path: Path to the video file.
        interval: Time between frames in seconds.
        output_directory: Directory to save frames.
        start: Start time in seconds. Default 0.0.
        end: End time in seconds (None for video end).
        format: Image format (png, jpg). Default ``"png"``.
        prefix: Filename prefix. Default ``"frame"``.

    Returns:
        dict with keys: status, frame_count, output_paths, timestamps.
    """
    try:
        from codomyrmex.video.extraction import FrameExtractor

        extractor = FrameExtractor()
        frames = extractor.extract_frames(
            video_path,
            interval=interval,
            start=start,
            end=end,
        )
        saved = extractor.save_frames(
            frames,
            output_directory=output_directory,
            prefix=prefix,
            format=format,
        )
        return {
            "status": "success",
            "frame_count": len(saved),
            "output_paths": [str(p) for p in saved],
            "timestamps": [round(start + i * interval, 2) for i in range(len(saved))],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Generate a thumbnail image from a video.",
)
def video_thumbnail(
    video_path: str,
    output_path: str,
    timestamp: float | None = None,
    width: int = 320,
) -> dict[str, Any]:
    """Generate a thumbnail from a video.

    Args:
        video_path: Path to the video file.
        output_path: Path to save the thumbnail.
        timestamp: Time to capture (None for 10% into video).
        width: Thumbnail width in pixels. Default 320.

    Returns:
        dict with keys: status, output_path, width, height.
    """
    try:
        from codomyrmex.video.extraction import FrameExtractor

        extractor = FrameExtractor()
        thumbnail = extractor.generate_thumbnail(
            video_path,
            timestamp=timestamp,
            width=width,
        )
        thumbnail.save(output_path)

        return {
            "status": "success",
            "output_path": output_path,
            "width": thumbnail.width,
            "height": thumbnail.height,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Extract the audio track from a video file.",
)
def video_extract_audio(
    video_path: str,
    output_path: str,
    audio_format: str = "mp3",
    bitrate: str = "192k",
) -> dict[str, Any]:
    """Extract audio track from a video.

    Args:
        video_path: Path to the video file.
        output_path: Path for the extracted audio.
        audio_format: Audio format (mp3, wav, aac). Default ``"mp3"``.
        bitrate: Audio bitrate. Default ``"192k"``.

    Returns:
        dict with keys: status, audio_path.
    """
    try:
        from codomyrmex.video.extraction import FrameExtractor

        extractor = FrameExtractor()
        audio_path = extractor.extract_audio(
            video_path,
            output_path=output_path,
            audio_format=audio_format,
            bitrate=bitrate,
        )
        return {"status": "success", "audio_path": str(audio_path)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Get metadata and information about a video file.",
)
def video_info(video_path: str) -> dict[str, Any]:
    """Get video file information and metadata.

    Args:
        video_path: Path to the video file.

    Returns:
        dict with keys: status, info (duration, width, height, fps,
        frame_count, video_codec, audio_codec, has_audio, file_size).
    """
    try:
        from codomyrmex.video.analysis import VideoAnalyzer

        analyzer = VideoAnalyzer()
        info = analyzer.get_info(video_path)
        return {"status": "success", "info": info.to_dict()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Merge multiple video files into a single output video.",
)
def video_merge(
    video_paths: Sequence[str],
    output_path: str,
) -> dict[str, Any]:
    """Merge multiple videos into one.

    Args:
        video_paths: list of video file paths to merge.
        output_path: Path for merged output video.

    Returns:
        dict with keys: status, result (output_path, duration, file_size,
        width, height).
    """
    try:
        from codomyrmex.video.processing import VideoProcessor

        processor = VideoProcessor()
        result = processor.merge(list(video_paths), output_path)
        return {"status": "success", "result": result.to_dict()}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="video",
    description="Validate that a file is a readable, well-formed video.",
)
def video_validate(video_path: str) -> dict[str, Any]:
    """Check if a file is a valid, readable video.

    Args:
        video_path: Path to the video file.

    Returns:
        dict with keys: status, is_valid, has_audio, format, codec.
    """
    try:
        from pathlib import Path

        from codomyrmex.video.analysis import VideoAnalyzer

        analyzer = VideoAnalyzer()
        is_valid = analyzer.is_valid_video(video_path)
        result: dict[str, Any] = {
            "status": "success",
            "is_valid": is_valid,
        }

        if is_valid:
            info = analyzer.get_info(video_path)
            result["has_audio"] = info.has_audio
            result["format"] = Path(video_path).suffix.lstrip(".")
            result["codec"] = info.video_codec

        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
