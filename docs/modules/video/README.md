# Video Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Video module provides comprehensive video processing capabilities including manipulation, frame extraction, audio extraction, and analysis. It uses moviepy and OpenCV as backends for robust video operations, with graceful degradation when optional dependencies are not installed. The module exposes a clean API surface with typed models, configurable settings, and granular exception handling.

## Key Features

- **Video Processing**: Resize, crop, rotate, convert, filter, trim, and merge video files
- **Frame Extraction**: Extract single frames at timestamps, extract at intervals, and generate thumbnails
- **Audio Extraction**: Extract audio tracks in multiple formats (MP3, WAV, AAC)
- **Video Analysis**: Get complete metadata (duration, resolution, FPS, codec, frame count), validate videos, and compare two videos
- **Multiple Backends**: Supports moviepy and OpenCV with automatic detection via availability flags
- **Visual Filters**: Built-in filters including grayscale, mirror, invert, rotation, brightness, and contrast adjustment
- **Format Support**: Input: MP4, AVI, MOV, MKV, WEBM, WMV, FLV, M4V. Output: MP4, AVI, MOV, WEBM, MKV

## Key Components

### Processing (`processing/`)

| Component | Description |
|-----------|-------------|
| `VideoProcessor` | Primary video manipulation class with `resize()`, `crop()`, `rotate()`, `convert()`, `apply_filter()`, `trim()`, and `merge()` methods |

### Extraction (`extraction/`)

| Component | Description |
|-----------|-------------|
| `FrameExtractor` | Frame and audio extraction with `extract_frame()`, `extract_frames()`, `generate_thumbnail()`, and `extract_audio()` methods |

### Analysis (`analysis/`)

| Component | Description |
|-----------|-------------|
| `VideoAnalyzer` | Video metadata and comparison with `get_info()`, `get_duration()`, `has_audio()`, and `is_valid_video()` methods |

### Models and Configuration

| Component | Description |
|-----------|-------------|
| `VideoConfig` | Module configuration with `get_config()`, `set_config()`, `reset_config()`, and `configure()` functions |
| `VideoInfo` | Dataclass containing video metadata (duration, resolution, FPS, codec) |
| `ProcessingResult` | Dataclass representing the result of a processing operation |
| `ExtractionResult` | Dataclass representing the result of an extraction operation |
| `VideoComparison` | Dataclass for comparing two videos |
| `FilterType` | Enum of available visual filters (GRAYSCALE, MIRROR_HORIZONTAL, MIRROR_VERTICAL, INVERT, ROTATE_90/180/270, BRIGHTNESS, CONTRAST) |
| `VideoCodec` | Enum of supported video codecs |
| `AudioCodec` | Enum of supported audio codecs |

### Exceptions

| Component | Description |
|-----------|-------------|
| `VideoError` | Base exception for all video operations |
| `VideoReadError` | Error reading video files |
| `VideoWriteError` | Error writing video files |
| `VideoProcessingError` | Error during video processing operations |
| `FrameExtractionError` | Error during frame extraction |
| `AudioExtractionError` | Error during audio extraction |
| `UnsupportedFormatError` | Unsupported video format encountered |
| `VideoAnalysisError` | Error during video analysis |

### Availability Flags

| Flag | Description |
|------|-------------|
| `PIL_AVAILABLE` | Whether PIL/Pillow is available for image handling |
| `MOVIEPY_AVAILABLE` | Whether moviepy backend is available |
| `OPENCV_AVAILABLE` | Whether OpenCV backend is available |
| `PROCESSING_AVAILABLE` | Whether any processing backend is available |
| `EXTRACTION_AVAILABLE` | Whether frame extraction is available |
| `ANALYSIS_AVAILABLE` | Whether video analysis is available |

## Installation

```bash
# Install video dependencies
uv sync --extra video
```

## Quick Start

### Video Processing

```python
from codomyrmex.video import VideoProcessor, FilterType

processor = VideoProcessor()

# Resize video
result = processor.resize("input.mp4", width=1280, height=720)

# Crop region
result = processor.crop("input.mp4", x=100, y=50, width=800, height=600)

# Apply visual filter
result = processor.apply_filter("input.mp4", FilterType.GRAYSCALE)

# Trim to time range
result = processor.trim("input.mp4", start=10.0, end=30.0)

# Merge multiple videos
result = processor.merge(["video1.mp4", "video2.mp4"], "merged.mp4")
```

### Frame Extraction

```python
from codomyrmex.video import FrameExtractor

extractor = FrameExtractor()

# Extract single frame at timestamp
frame = extractor.extract_frame("video.mp4", timestamp=5.0)
frame.save("frame.png")

# Generate thumbnail
thumbnail = extractor.generate_thumbnail("video.mp4")
thumbnail.save("thumb.jpg")

# Extract audio track
audio_path = extractor.extract_audio("video.mp4", audio_format="mp3")
```

### Video Analysis

```python
from codomyrmex.video import VideoAnalyzer

analyzer = VideoAnalyzer()

# Get complete video metadata
info = analyzer.get_info("video.mp4")
print(f"Duration: {info.duration}s, Resolution: {info.width}x{info.height}, FPS: {info.fps}")

# Quick checks
duration = analyzer.get_duration("video.mp4")
has_audio = analyzer.has_audio("video.mp4")
is_valid = analyzer.is_valid_video("video.mp4")
```

## Related Modules

- [audio](../audio/) - Audio processing capabilities (complementary media processing)
- [data_visualization](../data_visualization/) - Visualization tools that may consume video analysis output
- [compression](../compression/) - General compression utilities applicable to media files

## Navigation

- **Source**: [src/codomyrmex/video/](../../../src/codomyrmex/video/)
- **Parent**: [docs/modules/](../README.md)
