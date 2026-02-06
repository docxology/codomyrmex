"""Data models for video processing.

This module defines the core data structures used for video information,
processing results, and extraction results.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # type: ignore


class FilterType(Enum):
    """Available video filters."""

    GRAYSCALE = "grayscale"
    BLUR = "blur"
    SHARPEN = "sharpen"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    SEPIA = "sepia"
    INVERT = "invert"
    MIRROR_HORIZONTAL = "mirror_horizontal"
    MIRROR_VERTICAL = "mirror_vertical"
    ROTATE_90 = "rotate_90"
    ROTATE_180 = "rotate_180"
    ROTATE_270 = "rotate_270"


class VideoCodec(Enum):
    """Common video codecs."""

    H264 = "libx264"
    H265 = "libx265"
    VP8 = "libvpx"
    VP9 = "libvpx-vp9"
    AV1 = "libaom-av1"
    MPEG4 = "mpeg4"
    MJPEG = "mjpeg"


class AudioCodec(Enum):
    """Common audio codecs."""

    AAC = "aac"
    MP3 = "libmp3lame"
    OPUS = "libopus"
    VORBIS = "libvorbis"
    FLAC = "flac"
    PCM = "pcm_s16le"


@dataclass
class VideoInfo:
    """Information about a video file.

    Attributes:
        file_path: Path to the video file
        duration: Duration in seconds
        width: Video width in pixels
        height: Video height in pixels
        fps: Frames per second
        frame_count: Total number of frames
        video_codec: Video codec name
        audio_codec: Audio codec name (if audio present)
        bitrate: Video bitrate in bits/second
        file_size: File size in bytes
        has_audio: Whether video has an audio track
        creation_time: Video creation timestamp
        rotation: Video rotation in degrees
    """

    file_path: Path
    duration: float = 0.0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    frame_count: int = 0
    video_codec: str = ""
    audio_codec: str | None = None
    bitrate: int = 0
    file_size: int = 0
    has_audio: bool = False
    creation_time: str | None = None
    rotation: int = 0

    @property
    def resolution(self) -> tuple[int, int]:
        """Get resolution as (width, height) tuple."""
        return (self.width, self.height)

    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio (width / height)."""
        if self.height == 0:
            return 0.0
        return self.width / self.height

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": str(self.file_path),
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "frame_count": self.frame_count,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "bitrate": self.bitrate,
            "file_size": self.file_size,
            "has_audio": self.has_audio,
            "creation_time": self.creation_time,
            "rotation": self.rotation,
        }


@dataclass
class ProcessingResult:
    """Result of a video processing operation.

    Attributes:
        output_path: Path to the output video
        duration: Duration of output video
        file_size: File size in bytes
        width: Output width
        height: Output height
        operation: Operation performed
        processing_time: Time taken to process
        success: Whether operation succeeded
        message: Status message
    """

    output_path: Path
    duration: float = 0.0
    file_size: int = 0
    width: int = 0
    height: int = 0
    operation: str = ""
    processing_time: float = 0.0
    success: bool = True
    message: str = ""

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "output_path": str(self.output_path),
            "duration": self.duration,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
            "operation": self.operation,
            "processing_time": self.processing_time,
            "success": self.success,
            "message": self.message,
        }


@dataclass
class ExtractionResult:
    """Result of frame or audio extraction.

    Attributes:
        source_path: Path to the source video
        frames: List of extracted PIL Image frames
        timestamps: Timestamps of extracted frames
        output_paths: Paths to saved frame files
        audio_path: Path to extracted audio file
        frame_count: Number of frames extracted
        processing_time: Time taken to extract
    """

    source_path: Path
    frames: list = field(default_factory=list)  # List of PIL.Image
    timestamps: list[float] = field(default_factory=list)
    output_paths: list[Path] = field(default_factory=list)
    audio_path: Path | None = None
    frame_count: int = 0
    processing_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (without image data)."""
        return {
            "source_path": str(self.source_path),
            "timestamps": self.timestamps,
            "output_paths": [str(p) for p in self.output_paths],
            "audio_path": str(self.audio_path) if self.audio_path else None,
            "frame_count": self.frame_count,
            "processing_time": self.processing_time,
        }


@dataclass
class VideoComparison:
    """Result of comparing two videos.

    Attributes:
        video1_path: Path to first video
        video2_path: Path to second video
        same_resolution: Whether resolutions match
        same_duration: Whether durations match (within tolerance)
        same_fps: Whether FPS matches
        same_codec: Whether video codec matches
        duration_diff: Difference in duration (seconds)
        size_diff: Difference in file size (bytes)
        details: Additional comparison details
    """

    video1_path: Path
    video2_path: Path
    same_resolution: bool = False
    same_duration: bool = False
    same_fps: bool = False
    same_codec: bool = False
    duration_diff: float = 0.0
    size_diff: int = 0
    details: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "FilterType",
    "VideoCodec",
    "AudioCodec",
    "VideoInfo",
    "ProcessingResult",
    "ExtractionResult",
    "VideoComparison",
    "PIL_AVAILABLE",
]
