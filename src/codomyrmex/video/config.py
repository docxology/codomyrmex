"""Video module configuration with presets, validation, and serialization.

Provides:
- VideoConfig: main config dataclass with all video processing settings
- Presets: high_quality, web_optimized, thumbnail_only, mobile configs
- Config validation, serialization (to_dict/from_dict), and diff
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


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
        ffmpeg_path: Custom ffmpeg binary path
        opencv_backend: OpenCV capture backend
    """

    temp_directory: Path | None = None
    default_output_format: str = "mp4"
    default_codec: str = "libx264"
    default_audio_codec: str = "aac"
    default_fps: int = 30
    default_bitrate: str = "5000k"
    thumbnail_width: int = 320
    max_concurrent_operations: int = 2
    cleanup_temp_files: bool = True
    ffmpeg_path: str | None = None
    opencv_backend: str = "auto"
    max_resolution: tuple[int, int] = (3840, 2160)
    quality_preset: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        """Serialize config to a plain dictionary."""
        d = asdict(self)
        if d.get("temp_directory"):
            d["temp_directory"] = str(d["temp_directory"])
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VideoConfig":
        """Deserialize config from a dictionary."""
        d = dict(data)
        if d.get("temp_directory"):
            d["temp_directory"] = Path(d["temp_directory"])
        if "max_resolution" in d and isinstance(d["max_resolution"], list):
            d["max_resolution"] = tuple(d["max_resolution"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def validate(self) -> list[str]:
        """Return a list of configuration issues (empty = valid)."""
        issues: list[str] = []
        if self.default_fps <= 0:
            issues.append(f"default_fps must be positive, got {self.default_fps}")
        if self.max_concurrent_operations < 1:
            issues.append("max_concurrent_operations must be >= 1")
        if self.thumbnail_width < 16:
            issues.append(f"thumbnail_width too small: {self.thumbnail_width}")
        if self.default_output_format not in ("mp4", "avi", "mkv", "webm", "mov"):
            issues.append(f"Unsupported format: {self.default_output_format}")
        if self.quality_preset not in ("ultrafast", "fast", "medium", "slow", "veryslow"):
            issues.append(f"Unknown quality_preset: {self.quality_preset}")
        return issues

    def diff(self, other: "VideoConfig") -> dict[str, tuple[Any, Any]]:
        """Compare two configs and return fields that differ."""
        d1, d2 = self.to_dict(), other.to_dict()
        return {k: (d1[k], d2[k]) for k in d1 if d1.get(k) != d2.get(k)}


# ── Presets ─────────────────────────────────────────────────────────

def high_quality() -> VideoConfig:
    """Preset for high-quality output (slow encoding)."""
    return VideoConfig(
        default_codec="libx264",
        default_bitrate="20000k",
        default_fps=60,
        quality_preset="slow",
        max_resolution=(3840, 2160),
    )


def web_optimized() -> VideoConfig:
    """Preset for web delivery (small files, fast seeking)."""
    return VideoConfig(
        default_codec="libx264",
        default_bitrate="2500k",
        default_fps=30,
        default_output_format="mp4",
        quality_preset="fast",
        max_resolution=(1920, 1080),
    )


def thumbnail_only() -> VideoConfig:
    """Preset for thumbnail extraction only."""
    return VideoConfig(
        thumbnail_width=640,
        max_concurrent_operations=4,
        cleanup_temp_files=True,
    )


def mobile_optimized() -> VideoConfig:
    """Preset for mobile playback."""
    return VideoConfig(
        default_bitrate="1500k",
        default_fps=30,
        default_output_format="mp4",
        quality_preset="fast",
        thumbnail_width=240,
        max_resolution=(1280, 720),
    )


# ── Globals ─────────────────────────────────────────────────────────

_config: VideoConfig = VideoConfig()


def get_config() -> VideoConfig:
    """Get the global video configuration."""
    return _config


def set_config(config: VideoConfig) -> None:
    """Set the global video configuration."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset configuration to defaults."""
    global _config
    _config = VideoConfig()


def configure(
    temp_directory: Path | None = None,
    default_output_format: str | None = None,
    default_codec: str | None = None,
    default_fps: int | None = None,
    thumbnail_width: int | None = None,
    quality_preset: str | None = None,
    **kwargs: object,
) -> VideoConfig:
    """Configure video processing settings.

    Args:
        temp_directory: Directory for temporary files
        default_output_format: Default output format
        default_codec: Default video codec
        default_fps: Default FPS
        thumbnail_width: Default thumbnail width
        quality_preset: Encoding speed/quality tradeoff
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
    if quality_preset is not None:
        _config.quality_preset = quality_preset
    return _config


__all__ = [
    "VideoConfig",
    "get_config",
    "set_config",
    "reset_config",
    "configure",
    "high_quality",
    "web_optimized",
    "thumbnail_only",
    "mobile_optimized",
]
