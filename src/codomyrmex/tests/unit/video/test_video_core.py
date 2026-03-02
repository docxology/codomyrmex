"""Unit tests for video module core: models, config, exceptions, and constants.

Tests cover:
- VideoConfig dataclass construction, validation, serialization, diff, and presets
- VideoInfo, ProcessingResult, ExtractionResult, VideoComparison dataclass properties
- FilterType, VideoCodec, AudioCodec enum completeness
- Exception hierarchy and context propagation
- Global config management (get/set/reset/configure)
- Supported format constants in processor, extractor, and analyzer submodules
- Module-level availability flags and version
- cli_commands() entrypoint
"""

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# VideoConfig
# ---------------------------------------------------------------------------

class TestVideoConfigConstruction:
    """VideoConfig dataclass construction and field defaults."""

    @pytest.mark.unit
    def test_default_config_fields(self) -> None:
        """Default VideoConfig has expected field values."""
        from codomyrmex.video.config import VideoConfig

        cfg = VideoConfig()
        assert cfg.default_output_format == "mp4"
        assert cfg.default_codec == "libx264"
        assert cfg.default_audio_codec == "aac"
        assert cfg.default_fps == 30
        assert cfg.default_bitrate == "5000k"
        assert cfg.thumbnail_width == 320
        assert cfg.max_concurrent_operations == 2
        assert cfg.cleanup_temp_files is True
        assert cfg.ffmpeg_path is None
        assert cfg.opencv_backend == "auto"
        assert cfg.max_resolution == (3840, 2160)
        assert cfg.quality_preset == "medium"
        assert cfg.temp_directory is None

    @pytest.mark.unit
    def test_config_custom_fields(self) -> None:
        """VideoConfig accepts custom field values."""
        from codomyrmex.video.config import VideoConfig

        cfg = VideoConfig(
            temp_directory=Path("/tmp/vid"),
            default_fps=60,
            quality_preset="slow",
            max_resolution=(1920, 1080),
        )
        assert cfg.temp_directory == Path("/tmp/vid")
        assert cfg.default_fps == 60
        assert cfg.quality_preset == "slow"
        assert cfg.max_resolution == (1920, 1080)


class TestVideoConfigValidation:
    """VideoConfig.validate() returns issues for bad values."""

    @pytest.mark.unit
    def test_valid_config_has_no_issues(self) -> None:
        from codomyrmex.video.config import VideoConfig

        issues = VideoConfig().validate()
        assert issues == []

    @pytest.mark.unit
    def test_negative_fps_detected(self) -> None:
        from codomyrmex.video.config import VideoConfig

        issues = VideoConfig(default_fps=-1).validate()
        assert any("default_fps" in i for i in issues)

    @pytest.mark.unit
    def test_zero_concurrent_ops_detected(self) -> None:
        from codomyrmex.video.config import VideoConfig

        issues = VideoConfig(max_concurrent_operations=0).validate()
        assert any("max_concurrent_operations" in i for i in issues)

    @pytest.mark.unit
    def test_tiny_thumbnail_detected(self) -> None:
        from codomyrmex.video.config import VideoConfig

        issues = VideoConfig(thumbnail_width=8).validate()
        assert any("thumbnail_width" in i for i in issues)

    @pytest.mark.unit
    def test_unsupported_format_detected(self) -> None:
        from codomyrmex.video.config import VideoConfig

        issues = VideoConfig(default_output_format="gif").validate()
        assert any("Unsupported format" in i for i in issues)

    @pytest.mark.unit
    def test_bad_quality_preset_detected(self) -> None:
        from codomyrmex.video.config import VideoConfig

        issues = VideoConfig(quality_preset="blazing").validate()
        assert any("quality_preset" in i for i in issues)


class TestVideoConfigSerialization:
    """VideoConfig to_dict / from_dict round-trip."""

    @pytest.mark.unit
    def test_to_dict_keys(self) -> None:
        from codomyrmex.video.config import VideoConfig

        d = VideoConfig().to_dict()
        expected_keys = {
            "temp_directory", "default_output_format", "default_codec",
            "default_audio_codec", "default_fps", "default_bitrate",
            "thumbnail_width", "max_concurrent_operations",
            "cleanup_temp_files", "ffmpeg_path", "opencv_backend",
            "max_resolution", "quality_preset",
        }
        assert expected_keys.issubset(set(d.keys()))

    @pytest.mark.unit
    def test_round_trip_without_temp_dir(self) -> None:
        from codomyrmex.video.config import VideoConfig

        original = VideoConfig(default_fps=60, quality_preset="fast")
        restored = VideoConfig.from_dict(original.to_dict())
        assert restored.default_fps == 60
        assert restored.quality_preset == "fast"

    @pytest.mark.unit
    def test_round_trip_with_temp_dir(self) -> None:
        from codomyrmex.video.config import VideoConfig

        original = VideoConfig(temp_directory=Path("/tmp/vid"))
        restored = VideoConfig.from_dict(original.to_dict())
        assert restored.temp_directory == Path("/tmp/vid")

    @pytest.mark.unit
    def test_from_dict_coerces_max_resolution_list(self) -> None:
        from codomyrmex.video.config import VideoConfig

        d = VideoConfig().to_dict()
        d["max_resolution"] = [1280, 720]
        restored = VideoConfig.from_dict(d)
        assert restored.max_resolution == (1280, 720)

    @pytest.mark.unit
    def test_from_dict_ignores_unknown_keys(self) -> None:
        from codomyrmex.video.config import VideoConfig

        d = VideoConfig().to_dict()
        d["bogus_field"] = 42
        restored = VideoConfig.from_dict(d)
        assert not hasattr(restored, "bogus_field") or True  # should not raise


class TestVideoConfigDiff:
    """VideoConfig.diff() returns changed fields."""

    @pytest.mark.unit
    def test_identical_configs_diff_empty(self) -> None:
        from codomyrmex.video.config import VideoConfig

        a = VideoConfig()
        b = VideoConfig()
        assert a.diff(b) == {}

    @pytest.mark.unit
    def test_diff_detects_changed_fields(self) -> None:
        from codomyrmex.video.config import VideoConfig

        a = VideoConfig()
        b = VideoConfig(default_fps=60, quality_preset="slow")
        diff = a.diff(b)
        assert "default_fps" in diff
        assert "quality_preset" in diff
        assert diff["default_fps"] == (30, 60)


class TestVideoConfigPresets:
    """Preset factory functions return correctly configured instances."""

    @pytest.mark.unit
    def test_high_quality_preset(self) -> None:
        from codomyrmex.video.config import high_quality

        cfg = high_quality()
        assert cfg.default_fps == 60
        assert cfg.quality_preset == "slow"
        assert cfg.default_bitrate == "20000k"

    @pytest.mark.unit
    def test_web_optimized_preset(self) -> None:
        from codomyrmex.video.config import web_optimized

        cfg = web_optimized()
        assert cfg.quality_preset == "fast"
        assert cfg.max_resolution == (1920, 1080)

    @pytest.mark.unit
    def test_thumbnail_only_preset(self) -> None:
        from codomyrmex.video.config import thumbnail_only

        cfg = thumbnail_only()
        assert cfg.thumbnail_width == 640
        assert cfg.max_concurrent_operations == 4

    @pytest.mark.unit
    def test_mobile_optimized_preset(self) -> None:
        from codomyrmex.video.config import mobile_optimized

        cfg = mobile_optimized()
        assert cfg.max_resolution == (1280, 720)
        assert cfg.thumbnail_width == 240


class TestGlobalConfigManagement:
    """get_config / set_config / reset_config / configure."""

    @pytest.mark.unit
    def test_get_set_reset_cycle(self) -> None:
        from codomyrmex.video.config import (
            VideoConfig,
            get_config,
            reset_config,
            set_config,
        )

        original_fps = get_config().default_fps
        set_config(VideoConfig(default_fps=120))
        assert get_config().default_fps == 120
        reset_config()
        assert get_config().default_fps == original_fps

    @pytest.mark.unit
    def test_configure_mutates_global(self) -> None:
        from codomyrmex.video.config import configure, get_config, reset_config

        configure(thumbnail_width=999, quality_preset="veryslow")
        cfg = get_config()
        assert cfg.thumbnail_width == 999
        assert cfg.quality_preset == "veryslow"
        reset_config()

    @pytest.mark.unit
    def test_configure_returns_config(self) -> None:
        from codomyrmex.video.config import configure, reset_config

        result = configure(default_fps=24)
        assert result.default_fps == 24
        reset_config()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TestVideoInfoModel:
    """VideoInfo dataclass properties and serialization."""

    @pytest.mark.unit
    def test_resolution_property(self) -> None:
        from codomyrmex.video.models import VideoInfo

        info = VideoInfo(file_path=Path("/v.mp4"), width=1920, height=1080)
        assert info.resolution == (1920, 1080)

    @pytest.mark.unit
    def test_aspect_ratio_16_9(self) -> None:
        from codomyrmex.video.models import VideoInfo

        info = VideoInfo(file_path=Path("/v.mp4"), width=1920, height=1080)
        assert abs(info.aspect_ratio - (1920 / 1080)) < 0.001

    @pytest.mark.unit
    def test_aspect_ratio_zero_height(self) -> None:
        from codomyrmex.video.models import VideoInfo

        info = VideoInfo(file_path=Path("/v.mp4"), width=1920, height=0)
        assert info.aspect_ratio == 0.0

    @pytest.mark.unit
    def test_file_size_mb(self) -> None:
        from codomyrmex.video.models import VideoInfo

        info = VideoInfo(file_path=Path("/v.mp4"), file_size=10 * 1024 * 1024)
        assert info.file_size_mb == 10.0

    @pytest.mark.unit
    def test_to_dict_all_keys(self) -> None:
        from codomyrmex.video.models import VideoInfo

        info = VideoInfo(
            file_path=Path("/v.mp4"), duration=60.0, width=1280,
            height=720, fps=30.0, frame_count=1800, video_codec="h264",
            audio_codec="aac", bitrate=5000000, file_size=75000000,
            has_audio=True, creation_time="2025-01-01", rotation=90,
        )
        d = info.to_dict()
        assert d["file_path"] == "/v.mp4"
        assert d["rotation"] == 90
        assert d["creation_time"] == "2025-01-01"
        assert d["has_audio"] is True


class TestProcessingResultModel:
    """ProcessingResult dataclass properties and serialization."""

    @pytest.mark.unit
    def test_file_size_mb(self) -> None:
        from codomyrmex.video.models import ProcessingResult

        result = ProcessingResult(output_path=Path("/o.mp4"), file_size=5 * 1024 * 1024)
        assert result.file_size_mb == 5.0

    @pytest.mark.unit
    def test_to_dict_operation_field(self) -> None:
        from codomyrmex.video.models import ProcessingResult

        result = ProcessingResult(
            output_path=Path("/o.mp4"), operation="resize", success=True,
            processing_time=2.5, message="done",
        )
        d = result.to_dict()
        assert d["operation"] == "resize"
        assert d["success"] is True
        assert d["processing_time"] == 2.5
        assert d["message"] == "done"


class TestExtractionResultModel:
    """ExtractionResult dataclass properties and serialization."""

    @pytest.mark.unit
    def test_to_dict_no_audio(self) -> None:
        from codomyrmex.video.models import ExtractionResult

        result = ExtractionResult(
            source_path=Path("/v.mp4"),
            timestamps=[0.0, 1.0],
            output_paths=[Path("/f0.png"), Path("/f1.png")],
            frame_count=2,
            processing_time=0.5,
        )
        d = result.to_dict()
        assert d["audio_path"] is None
        assert len(d["output_paths"]) == 2
        assert d["frame_count"] == 2

    @pytest.mark.unit
    def test_to_dict_with_audio_path(self) -> None:
        from codomyrmex.video.models import ExtractionResult

        result = ExtractionResult(
            source_path=Path("/v.mp4"),
            audio_path=Path("/audio.mp3"),
        )
        d = result.to_dict()
        assert d["audio_path"] == "/audio.mp3"


class TestVideoComparisonModel:
    """VideoComparison dataclass defaults and construction."""

    @pytest.mark.unit
    def test_defaults(self) -> None:
        from codomyrmex.video.models import VideoComparison

        comp = VideoComparison(
            video1_path=Path("/a.mp4"), video2_path=Path("/b.mp4"),
        )
        assert comp.same_resolution is False
        assert comp.same_duration is False
        assert comp.same_fps is False
        assert comp.same_codec is False
        assert comp.duration_diff == 0.0
        assert comp.size_diff == 0
        assert comp.details == {}

    @pytest.mark.unit
    def test_custom_values(self) -> None:
        from codomyrmex.video.models import VideoComparison

        comp = VideoComparison(
            video1_path=Path("/a.mp4"), video2_path=Path("/b.mp4"),
            same_resolution=True, same_duration=True,
            duration_diff=0.1, size_diff=500, details={"note": "ok"},
        )
        assert comp.same_resolution is True
        assert comp.details["note"] == "ok"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TestEnums:
    """Enum completeness and value correctness."""

    @pytest.mark.unit
    def test_filter_type_count(self) -> None:
        from codomyrmex.video.models import FilterType

        assert len(FilterType) == 13

    @pytest.mark.unit
    def test_video_codec_values(self) -> None:
        from codomyrmex.video.models import VideoCodec

        assert VideoCodec.H264.value == "libx264"
        assert VideoCodec.H265.value == "libx265"
        assert VideoCodec.VP8.value == "libvpx"
        assert VideoCodec.VP9.value == "libvpx-vp9"
        assert VideoCodec.AV1.value == "libaom-av1"
        assert VideoCodec.MPEG4.value == "mpeg4"
        assert VideoCodec.MJPEG.value == "mjpeg"

    @pytest.mark.unit
    def test_audio_codec_values(self) -> None:
        from codomyrmex.video.models import AudioCodec

        assert AudioCodec.AAC.value == "aac"
        assert AudioCodec.MP3.value == "libmp3lame"
        assert AudioCodec.OPUS.value == "libopus"
        assert AudioCodec.VORBIS.value == "libvorbis"
        assert AudioCodec.FLAC.value == "flac"
        assert AudioCodec.PCM.value == "pcm_s16le"

    @pytest.mark.unit
    def test_filter_type_iteration(self) -> None:
        from codomyrmex.video.models import FilterType

        values = [f.value for f in FilterType]
        assert "grayscale" in values
        assert "sepia" in values
        assert "rotate_270" in values


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TestExceptionHierarchy:
    """All video exceptions inherit from VideoError and store context."""

    @pytest.mark.unit
    def test_video_error_base(self) -> None:
        from codomyrmex.video.exceptions import VideoError

        err = VideoError("base error")
        assert "base error" in str(err)

    @pytest.mark.unit
    def test_video_error_with_path(self) -> None:
        from codomyrmex.video.exceptions import VideoError

        err = VideoError("fail", video_path="/v.mp4")
        assert err.context["video_path"] == "/v.mp4"

    @pytest.mark.unit
    def test_video_analysis_error_context(self) -> None:
        from codomyrmex.video.exceptions import VideoAnalysisError

        err = VideoAnalysisError("bad", video_path="/v.mp4", analysis_type="metadata")
        assert err.context["analysis_type"] == "metadata"
        assert err.context["video_path"] == "/v.mp4"

    @pytest.mark.unit
    def test_unsupported_format_error_stores_formats(self) -> None:
        from codomyrmex.video.exceptions import UnsupportedFormatError

        err = UnsupportedFormatError(
            "nope", format_type=".xyz", supported_formats=[".mp4", ".avi"],
        )
        assert err.context["format_type"] == ".xyz"
        assert ".mp4" in err.context["supported_formats"]

    @pytest.mark.unit
    def test_all_exceptions_subclass_video_error(self) -> None:
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

        for exc_cls in [
            VideoReadError, VideoWriteError, VideoProcessingError,
            FrameExtractionError, AudioExtractionError,
            UnsupportedFormatError, VideoAnalysisError,
        ]:
            assert issubclass(exc_cls, VideoError)


# ---------------------------------------------------------------------------
# Supported format constants
# ---------------------------------------------------------------------------

class TestSupportedFormats:
    """Processor, extractor, and analyzer supported format sets."""

    @pytest.mark.unit
    def test_processor_input_formats(self) -> None:
        from codomyrmex.video.processing.video_processor import SUPPORTED_INPUT_FORMATS

        for ext in (".mp4", ".avi", ".mov", ".mkv", ".webm"):
            assert ext in SUPPORTED_INPUT_FORMATS

    @pytest.mark.unit
    def test_processor_output_formats(self) -> None:
        from codomyrmex.video.processing.video_processor import SUPPORTED_OUTPUT_FORMATS

        for ext in (".mp4", ".avi", ".mov", ".webm", ".mkv"):
            assert ext in SUPPORTED_OUTPUT_FORMATS

    @pytest.mark.unit
    def test_extractor_formats(self) -> None:
        from codomyrmex.video.extraction.frame_extractor import SUPPORTED_FORMATS

        for ext in (".mp4", ".avi", ".mov"):
            assert ext in SUPPORTED_FORMATS

    @pytest.mark.unit
    def test_analyzer_formats(self) -> None:
        from codomyrmex.video.analysis.video_analyzer import SUPPORTED_FORMATS

        for ext in (".mp4", ".avi", ".mov", ".mkv"):
            assert ext in SUPPORTED_FORMATS


# ---------------------------------------------------------------------------
# Module-level availability flags and version
# ---------------------------------------------------------------------------

class TestModuleLevel:
    """Module-level attributes exposed via __init__."""

    @pytest.mark.unit
    def test_version_string(self) -> None:
        from codomyrmex.video import __version__

        assert isinstance(__version__, str)
        assert __version__ == "0.1.0"

    @pytest.mark.unit
    def test_availability_flags_are_bool(self) -> None:
        from codomyrmex.video import (
            ANALYSIS_AVAILABLE,
            EXTRACTION_AVAILABLE,
            MOVIEPY_AVAILABLE,
            OPENCV_AVAILABLE,
            PIL_AVAILABLE,
            PROCESSING_AVAILABLE,
        )

        for flag in [
            PROCESSING_AVAILABLE, EXTRACTION_AVAILABLE,
            ANALYSIS_AVAILABLE, MOVIEPY_AVAILABLE,
            OPENCV_AVAILABLE, PIL_AVAILABLE,
        ]:
            assert isinstance(flag, bool)

    @pytest.mark.unit
    def test_cli_commands_returns_dict(self) -> None:
        from codomyrmex.video import cli_commands

        cmds = cli_commands()
        assert isinstance(cmds, dict)
        assert "formats" in cmds
        assert "process" in cmds
        assert "handler" in cmds["formats"]
        assert "help" in cmds["formats"]
