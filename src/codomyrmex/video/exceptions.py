"""Video module exception classes.

This module defines all exception classes for video processing operations
including reading, writing, processing, and analysis.

Exception Hierarchy:
    VideoError (base)
    ├── VideoReadError - Failed to read video file
    ├── VideoWriteError - Failed to write video file
    ├── VideoProcessingError - Processing operation failed
    ├── FrameExtractionError - Frame extraction failed
    ├── AudioExtractionError - Audio extraction failed
    ├── UnsupportedFormatError - Video format not supported
    └── VideoAnalysisError - Analysis operation failed
"""

from pathlib import Path
from typing import Any

from codomyrmex.exceptions import CodomyrmexError


class VideoError(CodomyrmexError):
    """Base exception for all video-related errors.

    Attributes:
        message: The error message
        video_path: Path to the video file involved, if any
        context: Additional context information
    """

    def __init__(
        self,
        message: str,
        video_path: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if video_path:
            self.context["video_path"] = str(video_path)


class VideoReadError(VideoError):
    """Raised when reading a video file fails.

    This can occur due to:
    - File not found
    - Corrupted video file
    - Missing codec
    - Permission denied
    """

    pass


class VideoWriteError(VideoError):
    """Raised when writing a video file fails.

    This can occur due to:
    - Invalid output path
    - Disk full
    - Permission denied
    - Codec encoding error
    """

    def __init__(
        self,
        message: str,
        video_path: str | Path | None = None,
        output_path: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, video_path=video_path, **kwargs)
        if output_path:
            self.context["output_path"] = str(output_path)


class VideoProcessingError(VideoError):
    """Raised when a video processing operation fails.

    This can occur during:
    - Resizing
    - Cropping
    - Rotating
    - Applying filters
    - Trimming
    - Merging
    """

    def __init__(
        self,
        message: str,
        video_path: str | Path | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, video_path=video_path, **kwargs)
        if operation:
            self.context["operation"] = operation


class FrameExtractionError(VideoError):
    """Raised when frame extraction fails.

    This can occur due to:
    - Invalid timestamp
    - Corrupted frame data
    - Memory allocation failure
    """

    def __init__(
        self,
        message: str,
        video_path: str | Path | None = None,
        timestamp: float | None = None,
        frame_number: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, video_path=video_path, **kwargs)
        if timestamp is not None:
            self.context["timestamp"] = timestamp
        if frame_number is not None:
            self.context["frame_number"] = frame_number


class AudioExtractionError(VideoError):
    """Raised when audio extraction from video fails.

    This can occur due to:
    - No audio track in video
    - Audio codec not supported
    - Extraction processing error
    """

    def __init__(
        self,
        message: str,
        video_path: str | Path | None = None,
        audio_format: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, video_path=video_path, **kwargs)
        if audio_format:
            self.context["audio_format"] = audio_format


class UnsupportedFormatError(VideoError):
    """Raised when the video format is not supported.

    Supported formats typically include:
    - MP4, AVI, MOV, MKV, WEBM for input
    - MP4, AVI, MOV for output
    """

    def __init__(
        self,
        message: str,
        format_type: str | None = None,
        supported_formats: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if format_type:
            self.context["format_type"] = format_type
        if supported_formats:
            self.context["supported_formats"] = supported_formats


class VideoAnalysisError(VideoError):
    """Raised when video analysis fails.

    This can occur during:
    - Metadata extraction
    - Duration calculation
    - Codec detection
    - Resolution detection
    """

    def __init__(
        self,
        message: str,
        video_path: str | Path | None = None,
        analysis_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, video_path=video_path, **kwargs)
        if analysis_type:
            self.context["analysis_type"] = analysis_type


__all__ = [
    "VideoError",
    "VideoReadError",
    "VideoWriteError",
    "VideoProcessingError",
    "FrameExtractionError",
    "AudioExtractionError",
    "UnsupportedFormatError",
    "VideoAnalysisError",
]
