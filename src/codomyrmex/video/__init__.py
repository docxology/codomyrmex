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

# Import exceptions
from .exceptions import (
    VideoError,
    VideoReadError,
    VideoWriteError,
    VideoProcessingError,
    FrameExtractionError,
    AudioExtractionError,
    UnsupportedFormatError,
    VideoAnalysisError,
)

# Import configuration
from .config import (
    VideoConfig,
    get_config,
    set_config,
    reset_config,
    configure,
)

# Import models
from .models import (
    FilterType,
    VideoCodec,
    AudioCodec,
    VideoInfo,
    ProcessingResult,
    ExtractionResult,
    VideoComparison,
    PIL_AVAILABLE,
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


# Build __all__ dynamically
__all__ = [
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
