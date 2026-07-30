# Video Module Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The video module provides video processing, extraction, and analysis capabilities through a clean, modular API. The supported `video` extra installs OpenCV and Pillow. The legacy MoviePy adapter remains capability-detected and fails closed when MoviePy is absent; it is not installed by the extra because MoviePy 2.2.1 constrains Pillow below the repository's security-patched baseline. Availability probes do not import OpenCV or MoviePy; native backends load only when an operation selects them, so package discovery remains free of native-media side effects.

## Architecture

```
video/
├── __init__.py              # Main exports, availability flags
├── exceptions.py            # Exception hierarchy
├── config.py                # Module configuration
├── models.py                # Data models
├── processing/
│   └── video_processor.py   # VideoProcessor class
├── extraction/
│   └── frame_extractor.py   # FrameExtractor class
└── analysis/
    └── video_analyzer.py    # VideoAnalyzer class
```

## Components

### VideoProcessor

Handles video manipulation operations.

**Backend**: OpenCV for supported operations; the capability-detected MoviePy adapter is optional and not installed by the `video` extra.

**Operations**:
| Method | Description | Codec Support |
|--------|-------------|---------------|
| resize | Scale dimensions | H264, H265 |
| crop | Extract region | H264, H265 |
| rotate | Rotate by angle | H264, H265 |
| convert | Change format | All |
| apply_filter | Visual effects | H264 |
| trim | Time-based cut | H264, H265 |
| merge | Concatenate | H264 |

### FrameExtractor

Handles frame and audio extraction.

**Backend**: OpenCV (frames); audio extraction requires a separately managed compatible MoviePy installation.

**Capabilities**:
- Single frame extraction at timestamp
- Batch frame extraction at intervals
- Thumbnail generation with aspect ratio
- Audio track extraction (MP3, WAV, AAC)

### VideoAnalyzer

Handles video metadata extraction.

**Backend**: OpenCV (primary); MoviePy is a separately managed optional fallback.

**Metadata Extracted**:
- Duration, width, height, FPS
- Frame count, codec, bitrate
- File size, audio presence
- Aspect ratio, rotation

## Data Models

### VideoInfo

```python
@dataclass
class VideoInfo:
    file_path: Path
    duration: float          # Seconds
    width: int               # Pixels
    height: int              # Pixels
    fps: float               # Frames per second
    frame_count: int         # Total frames
    video_codec: str         # e.g., "h264"
    audio_codec: Optional[str]
    bitrate: int             # bits/second
    file_size: int           # bytes
    has_audio: bool
    rotation: int            # degrees
```

### ProcessingResult

```python
@dataclass
class ProcessingResult:
    output_path: Path
    duration: float
    file_size: int
    width: int
    height: int
    operation: str
    processing_time: float
    success: bool
    message: str
```

### ExtractionResult

```python
@dataclass
class ExtractionResult:
    source_path: Path
    frames: list[PIL.Image]
    timestamps: list[float]
    output_paths: list[Path]
    audio_path: Optional[Path]
    frame_count: int
    processing_time: float
```

### FilterType

```python
class FilterType(Enum):
    GRAYSCALE = "grayscale"
    BLUR = "blur"
    SHARPEN = "sharpen"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SEPIA = "sepia"
    INVERT = "invert"
    MIRROR_HORIZONTAL = "mirror_horizontal"
    MIRROR_VERTICAL = "mirror_vertical"
    ROTATE_90 = "rotate_90"
    ROTATE_180 = "rotate_180"
    ROTATE_270 = "rotate_270"
```

## Exception Hierarchy

```
CodomyrmexError
└── VideoError
    ├── VideoReadError
    ├── VideoWriteError
    ├── VideoProcessingError
    ├── FrameExtractionError
    ├── AudioExtractionError
    ├── UnsupportedFormatError
    └── VideoAnalysisError
```

## Dependencies

```toml
[project.optional-dependencies]
video = [
    "opencv-python>=4.8.0",
    "pillow>=12.3.0",
]
```

MoviePy is intentionally not part of this extra. Upstream MoviePy 2.2.1
requires Pillow below 12, while Codomyrmex requires the security-patched
Pillow 12.3 baseline. MoviePy-only operations therefore fail closed unless an
operator supplies and validates a compatible backend.

## Configuration

```python
@dataclass
class VideoConfig:
    temp_directory: Optional[Path]
    default_output_format: str = "mp4"
    default_codec: str = "libx264"
    default_audio_codec: str = "aac"
    default_fps: int = 30
    default_bitrate: str = "5000k"
    thumbnail_width: int = 320
    max_concurrent_operations: int = 2
    cleanup_temp_files: bool = True
```

## Supported Formats

### Input
| Format | Extension | Codecs |
|--------|-----------|--------|
| MP4 | .mp4 | H264, H265, MPEG4 |
| AVI | .avi | MJPEG, H264, XVID |
| MOV | .mov | H264, ProRes |
| MKV | .mkv | H264, H265, VP9 |
| WebM | .webm | VP8, VP9 |
| WMV | .wmv | WMV9, VC1 |
| FLV | .flv | H263, VP6 |

### Output
| Format | Codec | Container |
|--------|-------|-----------|
| MP4 | libx264 | MPEG-4 |
| AVI | mjpeg | AVI |
| MOV | libx264 | QuickTime |
| WebM | libvpx | WebM |

## Performance Considerations

### Memory Usage
- Frame extraction: ~50MB per 1080p frame
- Video processing: 2-3x source file size in memory
- Batch operations: Use streaming when possible

### Processing Speed
- Resize: ~1-2x realtime
- Filters: ~0.5-1x realtime
- Merge: ~0.3x realtime (encoding bound)

### Recommendations
1. Use OpenCV for frame extraction (faster)
2. Treat MoviePy-only operations as unavailable unless a compatible backend has been separately validated
3. Process in smaller chunks for large files
4. Enable codec hardware acceleration when available

## Thread Safety

- **VideoProcessor**: Not thread-safe per instance
- **FrameExtractor**: Thread-safe for extraction
- **VideoAnalyzer**: Thread-safe

For concurrent processing, create separate instances per thread.

## Testing

```bash
uv run python -m pytest tests/ -k video -v
```

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../README.md)
