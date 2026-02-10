"""Video processing module for Codomyrmex.

This module provides video processing capabilities including:
- Video processing (resize, crop, rotate, convert, filter, trim, merge)
- Frame extraction and thumbnail generation
- Audio extraction from video
- Video analysis and metadata extraction

Submodules:
    - processing: Video manipulation operations
    - extraction: Frame and audio extraction
    - analysis: Video metadata and comparison

Installation:
    Install video dependencies with:
    ```bash
    uv sync --extra video
    ```

Quick Start:
    ```python
    from codomyrmex.video import VideoProcessor, FrameExtractor, VideoAnalyzer

    # Process video
    processor = VideoProcessor()
    result = processor.resize("input.mp4", width=1280, height=720)
    result = processor.trim("input.mp4", start=10.0, end=30.0)

    # Extract frames
    extractor = FrameExtractor()
    frame = extractor.extract_frame("video.mp4", timestamp=5.0)
    frame.save("frame.png")

    thumbnail = extractor.generate_thumbnail("video.mp4")
    audio_path = extractor.extract_audio("video.mp4", audio_format="mp3")

    # Analyze video
    analyzer = VideoAnalyzer()
    info = analyzer.get_info("video.mp4")
    print(f"Duration: {info.duration}s, Resolution: {info.width}x{info.height}")
    ```
"""

__version__ = "0.1.0"

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Import exceptions
# Import configuration
from .config import (
    VideoConfig,
    configure,
    get_config,
    reset_config,
    set_config,
)
from .exceptions import (
    AudioExtractionError,
    FrameExtractionError,
    UnsupportedFormatError,
    VideoAnalysisError,
    VideoError,
    VideoProcessingError,
    VideoReadError,
    VideoWriteError,
)

# Import models
from .models import (
    PIL_AVAILABLE,
    AudioCodec,
    ExtractionResult,
    FilterType,
    ProcessingResult,
    VideoCodec,
    VideoComparison,
    VideoInfo,
)

# Import processing
try:
    from .processing import VideoProcessor
    from .processing.video_processor import MOVIEPY_AVAILABLE, OPENCV_AVAILABLE
    PROCESSING_AVAILABLE = MOVIEPY_AVAILABLE or OPENCV_AVAILABLE
except ImportError:
    VideoProcessor = None  # type: ignore
    MOVIEPY_AVAILABLE = False
    OPENCV_AVAILABLE = False
    PROCESSING_AVAILABLE = False

# Import extraction
try:
    from .extraction import FrameExtractor
    EXTRACTION_AVAILABLE = True
except ImportError:
    FrameExtractor = None  # type: ignore
    EXTRACTION_AVAILABLE = False

# Import analysis
try:
    from .analysis import VideoAnalyzer
    ANALYSIS_AVAILABLE = True
except ImportError:
    VideoAnalyzer = None  # type: ignore
    ANALYSIS_AVAILABLE = False


def cli_commands():
    """Return CLI commands for the video module."""
    return {
        "formats": {
            "help": "List supported video formats and capabilities",
            "handler": lambda **kwargs: print(
                f"Video Module v{__version__}\n"
                f"  Video codecs: {', '.join(vc.value if hasattr(vc, 'value') else str(vc) for vc in VideoCodec)}\n"
                f"  Audio codecs: {', '.join(ac.value if hasattr(ac, 'value') else str(ac) for ac in AudioCodec)}\n"
                f"  Filters: {', '.join(ft.value if hasattr(ft, 'value') else str(ft) for ft in FilterType)}\n"
                f"  Processing: {PROCESSING_AVAILABLE} | Extraction: {EXTRACTION_AVAILABLE} | Analysis: {ANALYSIS_AVAILABLE}"
            ),
        },
        "process": {
            "help": "Process a video file",
            "handler": lambda **kwargs: print(
                "Video Processing\n"
                "  Processor: VideoProcessor (resize, crop, rotate, convert, filter, trim, merge)\n"
                "  Extraction: FrameExtractor (frames, thumbnails, audio extraction)\n"
                "  Analysis: VideoAnalyzer (metadata, comparison)\n"
                "  Configure via VideoConfig or configure()"
            ),
        },
    }


# Build __all__ dynamically
__all__ = [
    # CLI integration
    "cli_commands",
    # Version
    "__version__",
    # Exceptions
    "VideoError",
    "VideoReadError",
    "VideoWriteError",
    "VideoProcessingError",
    "FrameExtractionError",
    "AudioExtractionError",
    "UnsupportedFormatError",
    "VideoAnalysisError",
    # Configuration
    "VideoConfig",
    "get_config",
    "set_config",
    "reset_config",
    "configure",
    # Models
    "FilterType",
    "VideoCodec",
    "AudioCodec",
    "VideoInfo",
    "ProcessingResult",
    "ExtractionResult",
    "VideoComparison",
    # Availability flags
    "PIL_AVAILABLE",
    "MOVIEPY_AVAILABLE",
    "OPENCV_AVAILABLE",
    "PROCESSING_AVAILABLE",
    "EXTRACTION_AVAILABLE",
    "ANALYSIS_AVAILABLE",
]

if PROCESSING_AVAILABLE:
    __all__.append("VideoProcessor")

if EXTRACTION_AVAILABLE:
    __all__.append("FrameExtractor")

if ANALYSIS_AVAILABLE:
    __all__.append("VideoAnalyzer")
