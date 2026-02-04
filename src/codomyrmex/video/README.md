# video

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The video module provides comprehensive video processing capabilities including manipulation, frame extraction, and analysis. It uses moviepy and OpenCV backends for robust video operations.

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

## Navigation

- **Full Documentation**: [docs/modules/video/](../../../docs/modules/video/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
