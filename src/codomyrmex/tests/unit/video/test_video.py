"""Unit tests for the video module.

Tests cover:
- Module imports and availability flags
- Exception classes
- Data models (VideoInfo, ProcessingResult, etc.)
- Configuration management
- VideoProcessor, FrameExtractor, VideoAnalyzer initialization
"""

from pathlib import Path

import pytest


# Test imports
def test_video_module_imports() -> None:
    """Test that video module can be imported."""
    from codomyrmex import video
    assert hasattr(video, "__version__")


def test_video_exceptions_import() -> None:
    """Test that all exception classes can be imported."""
    from codomyrmex.video.exceptions import (
        AudioExtractionError,
        FrameExtractionError,
        UnsupportedFormatError,
        VideoAnalysisError,
        VideoError,
        VideoProcessingError,
        VideoReadError,
        VideoWriteError,
    )

    # Verify exception hierarchy
    assert issubclass(VideoReadError, VideoError)
    assert issubclass(VideoWriteError, VideoError)
    assert issubclass(VideoProcessingError, VideoError)
    assert issubclass(FrameExtractionError, VideoError)
    assert issubclass(AudioExtractionError, VideoError)
    assert issubclass(UnsupportedFormatError, VideoError)
    assert issubclass(VideoAnalysisError, VideoError)


def test_video_exception_context() -> None:
    """Test that exceptions properly store context."""
    from codomyrmex.video.exceptions import VideoProcessingError

    error = VideoProcessingError(
        "Test error",
        video_path="/path/to/video.mp4",
        operation="resize",
    )

    assert error.context.get("video_path") == "/path/to/video.mp4"
    assert error.context.get("operation") == "resize"
    assert "Test error" in str(error)


def test_frame_extraction_error_context() -> None:
    """Test FrameExtractionError context."""
    from codomyrmex.video.exceptions import FrameExtractionError

    error = FrameExtractionError(
        "Failed to extract frame",
        video_path="/path/to/video.mp4",
        timestamp=5.5,
        frame_number=165,
    )

    assert error.context.get("timestamp") == 5.5
    assert error.context.get("frame_number") == 165


def test_availability_flags() -> None:
    """Test that availability flags are defined."""
    from codomyrmex.video import (
        ANALYSIS_AVAILABLE,
        EXTRACTION_AVAILABLE,
        MOVIEPY_AVAILABLE,
        OPENCV_AVAILABLE,
        PIL_AVAILABLE,
        PROCESSING_AVAILABLE,
    )

    # These should be boolean values
    assert isinstance(PROCESSING_AVAILABLE, bool)
    assert isinstance(EXTRACTION_AVAILABLE, bool)
    assert isinstance(ANALYSIS_AVAILABLE, bool)
    assert isinstance(MOVIEPY_AVAILABLE, bool)
    assert isinstance(OPENCV_AVAILABLE, bool)
    assert isinstance(PIL_AVAILABLE, bool)


# Configuration tests
class TestVideoConfig:
    """Tests for video configuration."""

    def test_video_config_defaults(self) -> None:
        """Test VideoConfig default values."""
        from codomyrmex.video.config import VideoConfig

        config = VideoConfig()

        assert config.default_output_format == "mp4"
        assert config.default_codec == "libx264"
        assert config.default_audio_codec == "aac"
        assert config.default_fps == 30
        assert config.default_bitrate == "5000k"
        assert config.thumbnail_width == 320
        assert config.max_concurrent_operations == 2
        assert config.cleanup_temp_files is True

    def test_get_set_config(self) -> None:
        """Test get_config and set_config."""
        from codomyrmex.video.config import (
            VideoConfig,
            get_config,
            reset_config,
            set_config,
        )

        # Get default config
        get_config()

        # Set new config
        new_config = VideoConfig(default_fps=60)
        set_config(new_config)

        # Verify change
        current = get_config()
        assert current.default_fps == 60

        # Reset
        reset_config()
        reset_config_value = get_config()
        assert reset_config_value.default_fps == 30

    def test_configure_function(self) -> None:
        """Test configure helper function."""
        from codomyrmex.video.config import configure, get_config, reset_config

        configure(thumbnail_width=640)
        config = get_config()
        assert config.thumbnail_width == 640

        reset_config()


# Model tests
class TestVideoModels:
    """Tests for video data models."""

    def test_filter_type_enum(self) -> None:
        """Test FilterType enum values."""
        from codomyrmex.video.models import FilterType

        assert FilterType.GRAYSCALE.value == "grayscale"
        assert FilterType.BLUR.value == "blur"
        assert FilterType.SHARPEN.value == "sharpen"
        assert FilterType.BRIGHTNESS.value == "brightness"
        assert FilterType.CONTRAST.value == "contrast"
        assert FilterType.SEPIA.value == "sepia"
        assert FilterType.INVERT.value == "invert"
        assert FilterType.MIRROR_HORIZONTAL.value == "mirror_horizontal"
        assert FilterType.MIRROR_VERTICAL.value == "mirror_vertical"

    def test_video_codec_enum(self) -> None:
        """Test VideoCodec enum values."""
        from codomyrmex.video.models import VideoCodec

        assert VideoCodec.H264.value == "libx264"
        assert VideoCodec.H265.value == "libx265"
        assert VideoCodec.VP9.value == "libvpx-vp9"

    def test_audio_codec_enum(self) -> None:
        """Test AudioCodec enum values."""
        from codomyrmex.video.models import AudioCodec

        assert AudioCodec.AAC.value == "aac"
        assert AudioCodec.MP3.value == "libmp3lame"
        assert AudioCodec.OPUS.value == "libopus"

    def test_video_info_dataclass(self) -> None:
        """Test VideoInfo dataclass."""
        from codomyrmex.video.models import VideoInfo

        info = VideoInfo(
            file_path=Path("/path/to/video.mp4"),
            duration=120.5,
            width=1920,
            height=1080,
            fps=29.97,
            frame_count=3600,
            video_codec="h264",
            audio_codec="aac",
            bitrate=5000000,
            file_size=75000000,
            has_audio=True,
        )

        assert info.resolution == (1920, 1080)
        assert abs(info.aspect_ratio - 1.777) < 0.01  # ~16:9
        assert abs(info.file_size_mb - 71.5) < 1.0

    def test_video_info_to_dict(self) -> None:
        """Test VideoInfo to_dict method."""
        from codomyrmex.video.models import VideoInfo

        info = VideoInfo(
            file_path=Path("/path/to/video.mp4"),
            duration=60.0,
            width=1280,
            height=720,
            fps=30.0,
        )

        data = info.to_dict()

        assert data["file_path"] == "/path/to/video.mp4"
        assert data["duration"] == 60.0
        assert data["width"] == 1280
        assert data["height"] == 720

    def test_processing_result_dataclass(self) -> None:
        """Test ProcessingResult dataclass."""
        from codomyrmex.video.models import ProcessingResult

        result = ProcessingResult(
            output_path=Path("/path/to/output.mp4"),
            duration=60.0,
            file_size=50000000,  # 50MB
            width=1280,
            height=720,
            operation="resize",
            processing_time=5.5,
            success=True,
        )

        assert abs(result.file_size_mb - 47.68) < 1.0
        assert result.success is True

        data = result.to_dict()
        assert data["operation"] == "resize"

    def test_extraction_result_dataclass(self) -> None:
        """Test ExtractionResult dataclass."""
        from codomyrmex.video.models import ExtractionResult

        result = ExtractionResult(
            source_path=Path("/path/to/video.mp4"),
            frames=[],  # Would be PIL Images
            timestamps=[0.0, 1.0, 2.0],
            output_paths=[
                Path("/frames/frame_0000.png"),
                Path("/frames/frame_0001.png"),
                Path("/frames/frame_0002.png"),
            ],
            frame_count=3,
            processing_time=1.2,
        )

        assert result.frame_count == 3
        assert len(result.timestamps) == 3

        data = result.to_dict()
        assert len(data["timestamps"]) == 3

    def test_video_comparison_dataclass(self) -> None:
        """Test VideoComparison dataclass."""
        from codomyrmex.video.models import VideoComparison

        comparison = VideoComparison(
            video1_path=Path("/video1.mp4"),
            video2_path=Path("/video2.mp4"),
            same_resolution=True,
            same_duration=True,
            same_fps=True,
            same_codec=False,
            duration_diff=0.1,
            size_diff=1000000,
        )

        assert comparison.same_resolution is True
        assert comparison.same_codec is False


# Processor tests
class TestVideoProcessor:
    """Tests for VideoProcessor class."""

    def test_video_processor_import(self) -> None:
        """Test VideoProcessor can be imported."""
        try:
            from codomyrmex.video.processing.video_processor import VideoProcessor
            assert callable(VideoProcessor)
        except ImportError:
            pytest.skip("Video processing dependencies not installed")

    def test_supported_formats(self) -> None:
        """Test supported format constants."""
        from codomyrmex.video.processing.video_processor import (
            SUPPORTED_INPUT_FORMATS,
            SUPPORTED_OUTPUT_FORMATS,
        )

        assert ".mp4" in SUPPORTED_INPUT_FORMATS
        assert ".avi" in SUPPORTED_INPUT_FORMATS
        assert ".mov" in SUPPORTED_INPUT_FORMATS
        assert ".mkv" in SUPPORTED_INPUT_FORMATS
        assert ".webm" in SUPPORTED_INPUT_FORMATS

        assert ".mp4" in SUPPORTED_OUTPUT_FORMATS
        assert ".avi" in SUPPORTED_OUTPUT_FORMATS


# Extractor tests
class TestFrameExtractor:
    """Tests for FrameExtractor class."""

    def test_frame_extractor_import(self) -> None:
        """Test FrameExtractor can be imported."""
        try:
            from codomyrmex.video.extraction.frame_extractor import FrameExtractor
            assert callable(FrameExtractor)
        except ImportError:
            pytest.skip("Frame extraction dependencies not installed")

    def test_supported_formats(self) -> None:
        """Test supported format constants."""
        from codomyrmex.video.extraction.frame_extractor import SUPPORTED_FORMATS

        assert ".mp4" in SUPPORTED_FORMATS
        assert ".avi" in SUPPORTED_FORMATS
        assert ".mov" in SUPPORTED_FORMATS


# Analyzer tests
class TestVideoAnalyzer:
    """Tests for VideoAnalyzer class."""

    def test_video_analyzer_import(self) -> None:
        """Test VideoAnalyzer can be imported."""
        try:
            from codomyrmex.video.analysis.video_analyzer import VideoAnalyzer
            assert callable(VideoAnalyzer)
        except ImportError:
            pytest.skip("Video analysis dependencies not installed")

    def test_supported_formats(self) -> None:
        """Test supported format constants."""
        from codomyrmex.video.analysis.video_analyzer import SUPPORTED_FORMATS

        assert ".mp4" in SUPPORTED_FORMATS
        assert ".avi" in SUPPORTED_FORMATS
        assert ".mov" in SUPPORTED_FORMATS


# Error handling tests
class TestErrorHandling:
    """Tests for error handling."""

    def test_unsupported_format_error(self) -> None:
        """Test UnsupportedFormatError creation."""
        from codomyrmex.video.exceptions import UnsupportedFormatError

        error = UnsupportedFormatError(
            "Format not supported",
            format_type=".xyz",
            supported_formats=[".mp4", ".avi"],
        )

        assert error.context.get("format_type") == ".xyz"
        assert ".mp4" in error.context.get("supported_formats", [])

    def test_audio_extraction_error(self) -> None:
        """Test AudioExtractionError creation."""
        from codomyrmex.video.exceptions import AudioExtractionError

        error = AudioExtractionError(
            "No audio track",
            video_path="/video.mp4",
            audio_format="mp3",
        )

        assert error.context.get("audio_format") == "mp3"

    def test_video_write_error(self) -> None:
        """Test VideoWriteError creation."""
        from codomyrmex.video.exceptions import VideoWriteError

        error = VideoWriteError(
            "Failed to write",
            video_path="/input.mp4",
            output_path="/output.mp4",
        )

        assert error.context.get("video_path") == "/input.mp4"
        assert error.context.get("output_path") == "/output.mp4"


# Coverage push — video/analysis
class TestVideoAnalyzerCoverage:
    """Coverage tests for VideoAnalyzer."""

    def test_import(self):
        from codomyrmex.video.analysis.video_analyzer import VideoAnalyzer
        assert callable(VideoAnalyzer)
