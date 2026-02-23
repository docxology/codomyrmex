# Video Module - Programmable AI Interface (PAI)

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Identity

- **Name**: video
- - **Category**: Media Processing
- **Dependencies**: logging_monitoring, environment_setup

## Capabilities

### Primary Functions

1. **Video Processing**
   - Input: Video file path + operation parameters
   - Output: ProcessingResult with new video path
   - Operations: resize, crop, rotate, convert, filter, trim, merge

2. **Frame Extraction**
   - Input: Video file path + timestamps
   - Output: PIL Image frames
   - Features: single/batch extraction, thumbnails

3. **Audio Extraction**
   - Input: Video file path
   - Output: Audio file path (MP3, WAV, AAC)

4. **Video Analysis**
   - Input: Video file path
   - Output: VideoInfo with metadata

### Availability Flags

```python
PROCESSING_AVAILABLE  # VideoProcessor available
EXTRACTION_AVAILABLE  # FrameExtractor available
ANALYSIS_AVAILABLE    # VideoAnalyzer available
MOVIEPY_AVAILABLE     # moviepy backend
OPENCV_AVAILABLE      # OpenCV backend
PIL_AVAILABLE         # Pillow for images
```

## Interface Contracts

### VideoProcessor Interface

```python
class VideoProcessor:
    def resize(video_path, width, height, output_path=None,
               maintain_aspect_ratio=True) -> ProcessingResult
    def crop(video_path, x, y, width, height, output_path=None) -> ProcessingResult
    def rotate(video_path, angle, output_path=None, expand=True) -> ProcessingResult
    def convert(video_path, output_format, output_path=None,
                video_codec=None, bitrate=None) -> ProcessingResult
    def apply_filter(video_path, filter_type, intensity=1.0,
                     output_path=None) -> ProcessingResult
    def trim(video_path, start, end, output_path=None) -> ProcessingResult
    def merge(video_paths, output_path, transition=None) -> ProcessingResult
```

### FrameExtractor Interface

```python
class FrameExtractor:
    def extract_frame(video_path, timestamp) -> PIL.Image
    def extract_frames(video_path, interval, start=0, end=None) -> list[PIL.Image]
    def extract_frames_at_timestamps(video_path, timestamps) -> ExtractionResult
    def generate_thumbnail(video_path, timestamp=None, width=320) -> PIL.Image
    def extract_audio(video_path, output_path=None, audio_format="mp3",
                      bitrate="192k") -> Path
    def save_frames(frames, output_directory, prefix="frame",
                    format="png") -> list[Path]
```

### VideoAnalyzer Interface

```python
class VideoAnalyzer:
    def get_info(video_path) -> VideoInfo
    def get_duration(video_path) -> float
    def get_resolution(video_path) -> tuple[int, int]
    def get_codec(video_path) -> str
    def get_fps(video_path) -> float
    def get_frame_count(video_path) -> int
    def has_audio(video_path) -> bool
    def is_valid_video(video_path) -> bool
    def compare_videos(video_path1, video_path2) -> VideoComparison
```

## Data Models

### VideoInfo

```python
VideoInfo:
    file_path: Path
    duration: float          # seconds
    width: int               # pixels
    height: int              # pixels
    fps: float
    frame_count: int
    video_codec: str
    audio_codec: Optional[str]
    bitrate: int             # bits/second
    file_size: int           # bytes
    has_audio: bool
    rotation: int            # degrees

    # Properties
    resolution: tuple[int, int]
    aspect_ratio: float
    file_size_mb: float

    # Methods
    to_dict() -> dict
```

### ProcessingResult

```python
ProcessingResult:
    output_path: Path
    duration: float
    file_size: int
    width: int
    height: int
    operation: str
    processing_time: float
    success: bool
    message: str

    # Properties
    file_size_mb: float

    # Methods
    to_dict() -> dict
```

### ExtractionResult

```python
ExtractionResult:
    source_path: Path
    frames: list[PIL.Image]
    timestamps: list[float]
    output_paths: list[Path]
    audio_path: Optional[Path]
    frame_count: int
    processing_time: float

    # Methods
    to_dict() -> dict
```

### FilterType

```python
FilterType(Enum):
    GRAYSCALE
    BLUR, SHARPEN
    BRIGHTNESS, CONTRAST, SATURATION
    SEPIA, INVERT
    MIRROR_HORIZONTAL, MIRROR_VERTICAL
    ROTATE_90, ROTATE_180, ROTATE_270
```

## Error Handling

### Exception Hierarchy

```
VideoError (base)
├── VideoReadError        # File read failures
├── VideoWriteError       # File write failures
├── VideoProcessingError  # Processing failures
├── FrameExtractionError  # Frame extraction failures
├── AudioExtractionError  # Audio extraction failures
├── UnsupportedFormatError # Invalid format
└── VideoAnalysisError    # Analysis failures
```

### Error Context

All exceptions include context:
```python
except VideoProcessingError as e:
    e.context.get("video_path")
    e.context.get("operation")
```

## Configuration

```python
VideoConfig:
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

## Integration Points

### Upstream Dependencies
- `logging_monitoring` - Logging
- `environment_setup` - Dependency validation

### Downstream Consumers
- `audio` - Audio processing from extracted audio
- `llm` - Vision analysis of extracted frames
- `documents` - Save video metadata

## Resource Management

### Memory
- Frame extraction: ~50MB per 1080p frame
- Processing: 2-3x source file size

### Disk
- Temporary files during processing
- Auto-cleanup enabled by default

### CPU/GPU
- moviepy: CPU-bound encoding
- OpenCV: Can use GPU for some operations

## Thread Safety

- Create separate instances per thread
- VideoAnalyzer is thread-safe
- VideoProcessor is NOT thread-safe

## Versioning

- Follows semantic versioning
- Breaking changes in major versions only
- Format support additions are minor versions
