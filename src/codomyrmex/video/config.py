"""Video module configuration.

This module provides configuration management for video processing operations.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class VideoConfig:
    """Global configuration for video processing.

    Attributes:
        temp_directory: Directory for temporary files
        default_output_format: Default format for output videos
        default_codec: Default video codec
        default_audio_codec: Default audio codec
        default_fps: Default frames per second
        default_bitrate: Default video bitrate
        thumbnail_width: Default thumbnail width
        max_concurrent_operations: Max parallel operations
        cleanup_temp_files: Auto-cleanup temporary files
    """

    temp_directory: Optional[Path] = None
    default_output_format: str = "mp4"
    default_codec: str = "libx264"
    default_audio_codec: str = "aac"
    default_fps: int = 30
    default_bitrate: str = "5000k"
    thumbnail_width: int = 320
    max_concurrent_operations: int = 2
    cleanup_temp_files: bool = True
    ffmpeg_path: Optional[str] = None
    opencv_backend: str = "auto"


# Global configuration instance
_config: VideoConfig = VideoConfig()


def get_config() -> VideoConfig:
    """Get the global video configuration.

    Returns:
        Current VideoConfig instance
    """
    return _config


def set_config(config: VideoConfig) -> None:
    """Set the global video configuration.

    Args:
        config: New VideoConfig instance
    """
    global _config
    _config = config


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _config
    _config = VideoConfig()


def configure(
    temp_directory: Optional[Path] = None,
    default_output_format: Optional[str] = None,
    default_codec: Optional[str] = None,
    default_fps: Optional[int] = None,
    thumbnail_width: Optional[int] = None,
    **kwargs: object,
) -> VideoConfig:
    """Configure video processing settings.

    Args:
        temp_directory: Directory for temporary files
        default_output_format: Default output format
        default_codec: Default video codec
        default_fps: Default FPS
        thumbnail_width: Default thumbnail width
        **kwargs: Additional configuration options

    Returns:
        Updated VideoConfig instance
    """
    global _config

    if temp_directory is not None:
        _config.temp_directory = temp_directory
    if default_output_format is not None:
        _config.default_output_format = default_output_format
    if default_codec is not None:
        _config.default_codec = default_codec
    if default_fps is not None:
        _config.default_fps = default_fps
    if thumbnail_width is not None:
        _config.thumbnail_width = thumbnail_width

    return _config


__all__ = [
    "VideoConfig",
    "get_config",
    "set_config",
    "reset_config",
    "configure",
]
