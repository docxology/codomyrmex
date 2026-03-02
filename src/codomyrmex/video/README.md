# Video Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The video module provides comprehensive video processing capabilities including manipulation, frame extraction, and analysis. It uses moviepy and OpenCV backends for robust video operations.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Generate and process video content (resize, crop, merge, filter) | Direct Python import |
| **EXECUTE** | Run video analysis and transformation pipelines | Direct Python import |
| **OBSERVE** | Inspect video metadata, duration, codecs, and frame content | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge to process, analyze, and extract frames from video files.

## Features

### Video Processing
- **Resize** - Scale videos to target dimensions
- **Crop** - Extract regions from video
- **Rotate** - Rotate by any angle
- **Convert** - Change format/codec
- **Filter** - Apply visual effects
- **Trim** - Cut to time range
- **Merge** - Concatenate multiple videos

### Frame Extraction
- Extract single frames at timestamp
- Extract frames at intervals
- Generate thumbnails
- Save frames to files

### Audio Extraction
- Extract audio tracks
- Multiple output formats (MP3, WAV, AAC)

### Video Analysis
- Get complete video metadata
- Duration, resolution, FPS, codec
- Frame count, aspect ratio
- Compare two videos

## Key Exports

### Processing Classes (when dependencies available)
- **`VideoProcessor`** — Video manipulation operations (resize, crop, rotate, convert, filter, trim, merge)
- **`FrameExtractor`** — Frame extraction, thumbnail generation, and audio extraction from video
- **`VideoAnalyzer`** — Video metadata extraction, duration queries, and comparison

### Exceptions
- **`VideoError`** — Base exception for all video-related errors
- **`VideoReadError`** — Raised when reading a video file fails (not found, corrupted, missing codec)
- **`VideoWriteError`** — Raised when writing a video file fails (invalid path, disk full, codec error)
- **`VideoProcessingError`** — Raised when a video processing operation fails (resize, crop, filter)
- **`FrameExtractionError`** — Raised when frame extraction fails (invalid timestamp, corrupted frame)
- **`AudioExtractionError`** — Raised when audio extraction from video fails (no audio track, codec error)
- **`UnsupportedFormatError`** — Raised when the video format is not supported
- **`VideoAnalysisError`** — Raised when video analysis fails (metadata extraction, codec detection)

### Configuration
- **`VideoConfig`** — Global configuration for video processing (temp dir, codecs, FPS, bitrate defaults)
- `get_config` / `set_config` / `reset_config` / `configure` — Configuration management functions

### Data Models
- **`VideoCodec`** — Enum of common video codecs (H264, H265, VP8, VP9, AV1, MPEG4, MJPEG)
- **`AudioCodec`** — Enum of common audio codecs (AAC, MP3, OPUS, VORBIS, FLAC, PCM)
- **`VideoInfo`** — Dataclass with complete video file metadata (duration, resolution, FPS, codec, bitrate)
- **`ProcessingResult`** — Dataclass result of a video processing operation (output path, dimensions, timing)
- **`ExtractionResult`** — Dataclass result of frame or audio extraction (frames, timestamps, paths)
- **`VideoComparison`** — Dataclass result of comparing two videos (resolution, duration, codec differences)
- **`FilterType`** — Enum of available video filters (grayscale, blur, sharpen, brightness, etc.)

### Availability Flags
- **`PIL_AVAILABLE`** — Boolean flag indicating whether Pillow (PIL) image dependencies are available
- **`MOVIEPY_AVAILABLE`** — Boolean flag indicating whether moviepy video editing dependencies are available
- **`OPENCV_AVAILABLE`** — Boolean flag indicating whether OpenCV (cv2) dependencies are available
- **`PROCESSING_AVAILABLE`** — Boolean flag indicating whether video processing is available (moviepy or OpenCV)
- **`EXTRACTION_AVAILABLE`** — Boolean flag indicating whether frame/audio extraction dependencies are available
- **`ANALYSIS_AVAILABLE`** — Boolean flag indicating whether video analysis dependencies are available

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Quick Start

### Video Processing

```python
from codomyrmex.video import VideoProcessor, FilterType

processor = VideoProcessor()

# Resize
result = processor.resize("input.mp4", width=1280, height=720)

# Crop
result = processor.crop("input.mp4", x=100, y=50, width=800, height=600)

# Apply filter
result = processor.apply_filter("input.mp4", FilterType.GRAYSCALE)

# Trim
result = processor.trim("input.mp4", start=10.0, end=30.0)

# Merge videos
result = processor.merge(["video1.mp4", "video2.mp4"], "merged.mp4")
```

### Frame Extraction

```python
from codomyrmex.video import FrameExtractor

extractor = FrameExtractor()

# Extract single frame
frame = extractor.extract_frame("video.mp4", timestamp=5.0)
frame.save("frame.png")

# Generate thumbnail
thumbnail = extractor.generate_thumbnail("video.mp4")
thumbnail.save("thumb.jpg")

# Extract multiple frames
frames = extractor.extract_frames("video.mp4", interval=1.0)

# Extract audio
audio_path = extractor.extract_audio("video.mp4", audio_format="mp3")
```

### Video Analysis

```python
from codomyrmex.video import VideoAnalyzer

analyzer = VideoAnalyzer()

# Get full info
info = analyzer.get_info("video.mp4")
print(f"Duration: {info.duration}s")
print(f"Resolution: {info.width}x{info.height}")
print(f"FPS: {info.fps}")

# Quick checks
duration = analyzer.get_duration("video.mp4")
has_audio = analyzer.has_audio("video.mp4")
is_valid = analyzer.is_valid_video("video.mp4")
```

## Directory Contents

- `__init__.py` - Main module exports
- `exceptions.py` - Video-specific exceptions
- `config.py` - Module configuration
- `models.py` - Data models
- `README.md` - This file
- `SPEC.md` - Technical specification
- `AGENTS.md` - AI agent guidance
- `PAI.md` - Programmable AI Interface
- `API_SPECIFICATION.md` - API reference
- `MCP_TOOL_SPECIFICATION.md` - MCP tools
- `processing/` - Video processing operations
- `extraction/` - Frame/audio extraction
- `analysis/` - Video analysis

## Supported Formats

### Input
MP4, AVI, MOV, MKV, WEBM, WMV, FLV, M4V

### Output
MP4, AVI, MOV, WEBM, MKV

## Available Filters

| Filter | Description |
|--------|-------------|
| GRAYSCALE | Black and white |
| MIRROR_HORIZONTAL | Flip horizontally |
| MIRROR_VERTICAL | Flip vertically |
| INVERT | Invert colors |
| ROTATE_90/180/270 | Rotate by degrees |
| BRIGHTNESS | Adjust brightness |
| CONTRAST | Adjust contrast |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k video -v
```

## Navigation

- **Full Documentation**: [docs/modules/video/](../../../docs/modules/video/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
