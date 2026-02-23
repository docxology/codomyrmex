# Video Module API Specification

## Overview

This document provides the complete API reference for the video module.

## VideoProcessor

### Constructor

```python
VideoProcessor(config: Optional[VideoConfig] = None) -> VideoProcessor
```

### Methods

#### resize

```python
def resize(
    video_path: str | Path,
    width: int,
    height: int,
    output_path: Optional[str | Path] = None,
    maintain_aspect_ratio: bool = True,
) -> ProcessingResult
```

Resize video to target dimensions.

**Parameters:**
- `video_path`: Path to input video
- `width`: Target width in pixels
- `height`: Target height in pixels
- `output_path`: Optional output path
- `maintain_aspect_ratio`: Scale to fit within dimensions if True

**Returns:** `ProcessingResult`

---

#### crop

```python
def crop(
    video_path: str | Path,
    x: int,
    y: int,
    width: int,
    height: int,
    output_path: Optional[str | Path] = None,
) -> ProcessingResult
```

Crop video to specified region.

**Parameters:**
- `video_path`: Path to input video
- `x`: Left edge of crop region
- `y`: Top edge of crop region
- `width`: Width of crop region
- `height`: Height of crop region
- `output_path`: Optional output path

---

#### rotate

```python
def rotate(
    video_path: str | Path,
    angle: float,
    output_path: Optional[str | Path] = None,
    expand: bool = True,
) -> ProcessingResult
```

Rotate video by angle (clockwise).

**Parameters:**
- `video_path`: Path to input video
- `angle`: Rotation angle in degrees
- `output_path`: Optional output path
- `expand`: Expand frame to fit rotated video

---

#### convert

```python
def convert(
    video_path: str | Path,
    output_format: str,
    output_path: Optional[str | Path] = None,
    video_codec: Optional[str] = None,
    audio_codec: Optional[str] = None,
    bitrate: Optional[str] = None,
) -> ProcessingResult
```

Convert video to different format.

**Parameters:**
- `video_path`: Path to input video
- `output_format`: Target format (e.g., "mp4", "avi")
- `output_path`: Optional output path
- `video_codec`: Video codec (e.g., "libx264")
- `audio_codec`: Audio codec (e.g., "aac")
- `bitrate`: Target bitrate (e.g., "5000k")

---

#### apply_filter

```python
def apply_filter(
    video_path: str | Path,
    filter_type: FilterType,
    intensity: float = 1.0,
    output_path: Optional[str | Path] = None,
) -> ProcessingResult
```

Apply visual filter to video.

**Parameters:**
- `video_path`: Path to input video
- `filter_type`: Type of filter (FilterType enum)
- `intensity`: Filter intensity (0.0-1.0)
- `output_path`: Optional output path

---

#### trim

```python
def trim(
    video_path: str | Path,
    start: float,
    end: float,
    output_path: Optional[str | Path] = None,
) -> ProcessingResult
```

Trim video to time range.

**Parameters:**
- `video_path`: Path to input video
- `start`: Start time in seconds
- `end`: End time in seconds
- `output_path`: Optional output path

---

#### merge

```python
def merge(
    video_paths: list[str | Path],
    output_path: str | Path,
    transition: Optional[str] = None,
    transition_duration: float = 1.0,
) -> ProcessingResult
```

Merge multiple videos into one.

**Parameters:**
- `video_paths`: List of video paths to merge
- `output_path`: Output path for merged video
- `transition`: Transition type (reserved for future)
- `transition_duration`: Transition duration in seconds

---

## FrameExtractor

### Constructor

```python
FrameExtractor(config: Optional[VideoConfig] = None) -> FrameExtractor
```

### Methods

#### extract_frame

```python
def extract_frame(
    video_path: str | Path,
    timestamp: float,
) -> PIL.Image
```

Extract single frame at timestamp.

**Parameters:**
- `video_path`: Path to video file
- `timestamp`: Time in seconds

**Returns:** PIL Image

---

#### extract_frames

```python
def extract_frames(
    video_path: str | Path,
    interval: float,
    start: float = 0.0,
    end: Optional[float] = None,
) -> list[PIL.Image]
```

Extract frames at regular intervals.

**Parameters:**
- `video_path`: Path to video file
- `interval`: Time between frames (seconds)
- `start`: Start time (seconds)
- `end`: End time (None = video end)

**Returns:** List of PIL Images

---

#### extract_frames_at_timestamps

```python
def extract_frames_at_timestamps(
    video_path: str | Path,
    timestamps: list[float],
) -> ExtractionResult
```

Extract frames at specific timestamps.

**Parameters:**
- `video_path`: Path to video file
- `timestamps`: List of timestamps in seconds

**Returns:** `ExtractionResult`

---

#### generate_thumbnail

```python
def generate_thumbnail(
    video_path: str | Path,
    timestamp: Optional[float] = None,
    width: int = 320,
) -> PIL.Image
```

Generate thumbnail from video.

**Parameters:**
- `video_path`: Path to video file
- `timestamp`: Time to extract (None = 10% into video)
- `width`: Thumbnail width (height from aspect ratio)

**Returns:** PIL Image thumbnail

---

#### extract_audio

```python
def extract_audio(
    video_path: str | Path,
    output_path: Optional[str | Path] = None,
    audio_format: str = "mp3",
    bitrate: str = "192k",
) -> Path
```

Extract audio track from video.

**Parameters:**
- `video_path`: Path to video file
- `output_path`: Optional output path
- `audio_format`: Audio format (mp3, wav, aac)
- `bitrate`: Audio bitrate

**Returns:** Path to extracted audio

---

#### save_frames

```python
def save_frames(
    frames: list[PIL.Image],
    output_directory: str | Path,
    prefix: str = "frame",
    format: str = "png",
) -> list[Path]
```

Save frames to files.

**Parameters:**
- `frames`: List of PIL Images
- `output_directory`: Directory to save frames
- `prefix`: Filename prefix
- `format`: Image format

**Returns:** List of saved file paths

---

## VideoAnalyzer

### Constructor

```python
VideoAnalyzer() -> VideoAnalyzer
```

### Methods

#### get_info

```python
def get_info(video_path: str | Path) -> VideoInfo
```

Get complete video metadata.

**Returns:** `VideoInfo`

---

#### get_duration

```python
def get_duration(video_path: str | Path) -> float
```

Get video duration in seconds.

---

#### get_resolution

```python
def get_resolution(video_path: str | Path) -> tuple[int, int]
```

Get video resolution as (width, height).

---

#### get_codec

```python
def get_codec(video_path: str | Path) -> str
```

Get video codec identifier.

---

#### get_fps

```python
def get_fps(video_path: str | Path) -> float
```

Get frames per second.

---

#### get_frame_count

```python
def get_frame_count(video_path: str | Path) -> int
```

Get total frame count.

---

#### has_audio

```python
def has_audio(video_path: str | Path) -> bool
```

Check if video has audio track.

---

#### is_valid_video

```python
def is_valid_video(video_path: str | Path) -> bool
```

Check if file is a valid, readable video.

---

#### compare_videos

```python
def compare_videos(
    video_path1: str | Path,
    video_path2: str | Path,
    duration_tolerance: float = 0.5,
) -> VideoComparison
```

Compare two videos.

**Parameters:**
- `video_path1`: First video path
- `video_path2`: Second video path
- `duration_tolerance`: Tolerance for duration comparison

**Returns:** `VideoComparison`

---

## Data Models

### VideoInfo

| Attribute | Type | Description |
|-----------|------|-------------|
| file_path | Path | Video file path |
| duration | float | Duration (seconds) |
| width | int | Width (pixels) |
| height | int | Height (pixels) |
| fps | float | Frames per second |
| frame_count | int | Total frames |
| video_codec | str | Video codec |
| audio_codec | Optional[str] | Audio codec |
| bitrate | int | Bitrate (bps) |
| file_size | int | File size (bytes) |
| has_audio | bool | Has audio track |
| rotation | int | Rotation (degrees) |

### ProcessingResult

| Attribute | Type | Description |
|-----------|------|-------------|
| output_path | Path | Output file path |
| duration | float | Duration (seconds) |
| file_size | int | File size (bytes) |
| width | int | Output width |
| height | int | Output height |
| operation | str | Operation performed |
| processing_time | float | Time taken |
| success | bool | Operation succeeded |
| message | str | Status message |

### ExtractionResult

| Attribute | Type | Description |
|-----------|------|-------------|
| source_path | Path | Source video path |
| frames | list | PIL Images |
| timestamps | list[float] | Frame timestamps |
| output_paths | list[Path] | Saved file paths |
| audio_path | Optional[Path] | Extracted audio |
| frame_count | int | Frames extracted |
| processing_time | float | Time taken |

### FilterType

```python
class FilterType(Enum):
    GRAYSCALE
    BLUR
    SHARPEN
    BRIGHTNESS
    CONTRAST
    SATURATION
    SEPIA
    INVERT
    MIRROR_HORIZONTAL
    MIRROR_VERTICAL
    ROTATE_90
    ROTATE_180
    ROTATE_270
```

---

## Exceptions

### VideoError

Base exception for video errors.

### VideoReadError

Raised when video file cannot be read.

### VideoWriteError

Raised when video file cannot be written.

### VideoProcessingError

Raised when processing operation fails.

### FrameExtractionError

Raised when frame extraction fails.

### AudioExtractionError

Raised when audio extraction fails.

### UnsupportedFormatError

Raised when format is not supported.

### VideoAnalysisError

Raised when analysis fails.
