"""
Unit tests for video.exceptions — Zero-Mock compliant.

Covers: VideoError (base), VideoReadError, VideoWriteError,
VideoProcessingError, FrameExtractionError, AudioExtractionError,
UnsupportedFormatError, VideoAnalysisError — context field storage,
video_path coercion to str, inheritance from CodomyrmexError, raise/catch.
"""

from pathlib import Path

import pytest

from codomyrmex.exceptions import CodomyrmexError
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

# ── VideoError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestVideoError:
    def test_is_codomyrmex_error(self):
        e = VideoError("video error")
        assert isinstance(e, CodomyrmexError)

    def test_message_stored(self):
        e = VideoError("video operation failed")
        assert "video operation failed" in str(e)

    def test_video_path_stored_as_str_when_str_provided(self):
        e = VideoError("err", video_path="/videos/clip.mp4")
        assert e.context["video_path"] == "/videos/clip.mp4"

    def test_video_path_stored_as_str_when_path_provided(self):
        p = Path("/tmp/test.mp4")
        e = VideoError("err", video_path=p)
        assert e.context["video_path"] == str(p)

    def test_video_path_not_stored_when_none(self):
        e = VideoError("err")
        assert "video_path" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(VideoError, match="video error"):
            raise VideoError("video error")

    def test_catch_as_codomyrmex_error(self):
        with pytest.raises(CodomyrmexError):
            raise VideoError("err")


# ── VideoReadError ────────────────────────────────────────────────────


@pytest.mark.unit
class TestVideoReadError:
    def test_is_video_error(self):
        e = VideoReadError("cannot read file")
        assert isinstance(e, VideoError)

    def test_message_stored(self):
        e = VideoReadError("file not found")
        assert "file not found" in str(e)

    def test_video_path_stored(self):
        e = VideoReadError("err", video_path="/videos/missing.mp4")
        assert e.context["video_path"] == "/videos/missing.mp4"

    def test_video_path_none_not_in_context(self):
        e = VideoReadError("err")
        assert "video_path" not in e.context

    def test_path_object_stored_as_str(self):
        p = Path("/tmp/read_test.mp4")
        e = VideoReadError("err", video_path=p)
        assert e.context["video_path"] == str(p)
        assert isinstance(e.context["video_path"], str)

    def test_raise_and_catch(self):
        with pytest.raises(VideoReadError):
            raise VideoReadError("codec missing", video_path="/video.mp4")

    def test_catch_as_video_error(self):
        with pytest.raises(VideoError):
            raise VideoReadError("read failed")


# ── VideoWriteError ───────────────────────────────────────────────────


@pytest.mark.unit
class TestVideoWriteError:
    def test_is_video_error(self):
        e = VideoWriteError("cannot write file")
        assert isinstance(e, VideoError)

    def test_message_stored(self):
        e = VideoWriteError("disk full")
        assert "disk full" in str(e)

    def test_video_path_stored_when_provided(self):
        e = VideoWriteError("err", video_path="/input/clip.mp4")
        assert e.context["video_path"] == "/input/clip.mp4"

    def test_output_path_stored_when_provided(self):
        e = VideoWriteError("err", output_path="/output/result.mp4")
        assert e.context["output_path"] == "/output/result.mp4"

    def test_output_path_stored_as_str_when_path_object(self):
        p = Path("/tmp/out.mp4")
        e = VideoWriteError("err", output_path=p)
        assert e.context["output_path"] == str(p)
        assert isinstance(e.context["output_path"], str)

    def test_output_path_not_stored_when_none(self):
        e = VideoWriteError("err")
        assert "output_path" not in e.context

    def test_both_paths_stored(self):
        e = VideoWriteError(
            "err",
            video_path="/in/source.mp4",
            output_path="/out/dest.mp4",
        )
        assert e.context["video_path"] == "/in/source.mp4"
        assert e.context["output_path"] == "/out/dest.mp4"

    def test_raise_and_catch(self):
        with pytest.raises(VideoWriteError):
            raise VideoWriteError("write failed", output_path="/tmp/out.mp4")


# ── VideoProcessingError ──────────────────────────────────────────────


@pytest.mark.unit
class TestVideoProcessingError:
    def test_is_video_error(self):
        e = VideoProcessingError("processing failed")
        assert isinstance(e, VideoError)

    def test_message_stored(self):
        e = VideoProcessingError("resize operation failed")
        assert "resize operation failed" in str(e)

    def test_video_path_stored_when_provided(self):
        e = VideoProcessingError("err", video_path="/clip.mp4")
        assert e.context["video_path"] == "/clip.mp4"

    def test_operation_stored_when_provided(self):
        e = VideoProcessingError("err", operation="resize")
        assert e.context["operation"] == "resize"

    def test_operation_not_stored_when_none(self):
        e = VideoProcessingError("err")
        assert "operation" not in e.context

    def test_both_fields_stored(self):
        e = VideoProcessingError("err", video_path="/v.mp4", operation="crop")
        assert e.context["video_path"] == "/v.mp4"
        assert e.context["operation"] == "crop"

    def test_various_operations(self):
        for op in ["resize", "crop", "rotate", "trim", "merge", "filter"]:
            e = VideoProcessingError("err", operation=op)
            assert e.context["operation"] == op

    def test_raise_and_catch(self):
        with pytest.raises(VideoProcessingError):
            raise VideoProcessingError("rotate failed", operation="rotate")


# ── FrameExtractionError ──────────────────────────────────────────────


@pytest.mark.unit
class TestFrameExtractionError:
    def test_is_video_error(self):
        e = FrameExtractionError("frame extraction failed")
        assert isinstance(e, VideoError)

    def test_message_stored(self):
        e = FrameExtractionError("invalid timestamp")
        assert "invalid timestamp" in str(e)

    def test_video_path_stored_when_provided(self):
        e = FrameExtractionError("err", video_path="/clip.mp4")
        assert e.context["video_path"] == "/clip.mp4"

    def test_timestamp_stored_when_provided(self):
        e = FrameExtractionError("err", timestamp=12.5)
        assert e.context["timestamp"] == pytest.approx(12.5)

    def test_timestamp_zero_stored(self):
        """timestamp=0.0 uses 'is not None' guard — must be stored."""
        e = FrameExtractionError("err", timestamp=0.0)
        assert "timestamp" in e.context
        assert e.context["timestamp"] == pytest.approx(0.0)

    def test_timestamp_not_stored_when_none(self):
        e = FrameExtractionError("err")
        assert "timestamp" not in e.context

    def test_frame_number_stored_when_provided(self):
        e = FrameExtractionError("err", frame_number=42)
        assert e.context["frame_number"] == 42

    def test_frame_number_zero_stored(self):
        e = FrameExtractionError("err", frame_number=0)
        assert "frame_number" in e.context
        assert e.context["frame_number"] == 0

    def test_frame_number_not_stored_when_none(self):
        e = FrameExtractionError("err")
        assert "frame_number" not in e.context

    def test_all_fields_stored(self):
        e = FrameExtractionError(
            "err",
            video_path="/clip.mp4",
            timestamp=3.14,
            frame_number=100,
        )
        assert e.context["video_path"] == "/clip.mp4"
        assert e.context["timestamp"] == pytest.approx(3.14)
        assert e.context["frame_number"] == 100

    def test_none_fields_not_in_context(self):
        e = FrameExtractionError("err")
        assert "timestamp" not in e.context
        assert "frame_number" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(FrameExtractionError):
            raise FrameExtractionError("frame corrupted", frame_number=500)


# ── AudioExtractionError ──────────────────────────────────────────────


@pytest.mark.unit
class TestAudioExtractionError:
    def test_is_video_error(self):
        e = AudioExtractionError("audio extraction failed")
        assert isinstance(e, VideoError)

    def test_message_stored(self):
        e = AudioExtractionError("no audio track")
        assert "no audio track" in str(e)

    def test_video_path_stored_when_provided(self):
        e = AudioExtractionError("err", video_path="/silent.mp4")
        assert e.context["video_path"] == "/silent.mp4"

    def test_audio_format_stored_when_provided(self):
        e = AudioExtractionError("err", audio_format="mp3")
        assert e.context["audio_format"] == "mp3"

    def test_audio_format_not_stored_when_none(self):
        e = AudioExtractionError("err")
        assert "audio_format" not in e.context

    def test_both_fields_stored(self):
        e = AudioExtractionError("err", video_path="/v.mp4", audio_format="wav")
        assert e.context["video_path"] == "/v.mp4"
        assert e.context["audio_format"] == "wav"

    def test_supported_audio_formats(self):
        for fmt in ["mp3", "wav", "aac", "flac", "ogg"]:
            e = AudioExtractionError("err", audio_format=fmt)
            assert e.context["audio_format"] == fmt

    def test_raise_and_catch(self):
        with pytest.raises(AudioExtractionError):
            raise AudioExtractionError("unsupported codec", audio_format="opus")


# ── UnsupportedFormatError ────────────────────────────────────────────


@pytest.mark.unit
class TestUnsupportedFormatError:
    def test_is_video_error(self):
        e = UnsupportedFormatError("format not supported")
        assert isinstance(e, VideoError)

    def test_message_stored(self):
        e = UnsupportedFormatError("wmv not supported")
        assert "wmv not supported" in str(e)

    def test_format_type_stored_when_provided(self):
        e = UnsupportedFormatError("err", format_type="wmv")
        assert e.context["format_type"] == "wmv"

    def test_format_type_not_stored_when_none(self):
        e = UnsupportedFormatError("err")
        assert "format_type" not in e.context

    def test_supported_formats_stored_when_provided(self):
        fmts = ["mp4", "avi", "mov", "mkv"]
        e = UnsupportedFormatError("err", supported_formats=fmts)
        assert e.context["supported_formats"] == fmts

    def test_supported_formats_not_stored_when_none(self):
        e = UnsupportedFormatError("err")
        assert "supported_formats" not in e.context

    def test_supported_formats_not_stored_when_empty(self):
        """Empty list is falsy — not stored per source logic."""
        e = UnsupportedFormatError("err", supported_formats=[])
        assert "supported_formats" not in e.context

    def test_both_fields_stored(self):
        e = UnsupportedFormatError(
            "err",
            format_type="rm",
            supported_formats=["mp4", "avi"],
        )
        assert e.context["format_type"] == "rm"
        assert e.context["supported_formats"] == ["mp4", "avi"]

    def test_does_not_inherit_video_path_from_base(self):
        """UnsupportedFormatError calls super().__init__(message) without video_path."""
        e = UnsupportedFormatError("err", format_type="wmv")
        assert "video_path" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(UnsupportedFormatError):
            raise UnsupportedFormatError("unsupported", format_type="3gp")


# ── VideoAnalysisError ────────────────────────────────────────────────


@pytest.mark.unit
class TestVideoAnalysisError:
    def test_is_video_error(self):
        e = VideoAnalysisError("analysis failed")
        assert isinstance(e, VideoError)

    def test_message_stored(self):
        e = VideoAnalysisError("metadata extraction failed")
        assert "metadata extraction failed" in str(e)

    def test_video_path_stored_when_provided(self):
        e = VideoAnalysisError("err", video_path="/analyze.mp4")
        assert e.context["video_path"] == "/analyze.mp4"

    def test_analysis_type_stored_when_provided(self):
        e = VideoAnalysisError("err", analysis_type="duration")
        assert e.context["analysis_type"] == "duration"

    def test_analysis_type_not_stored_when_none(self):
        e = VideoAnalysisError("err")
        assert "analysis_type" not in e.context

    def test_both_fields_stored(self):
        e = VideoAnalysisError("err", video_path="/v.mp4", analysis_type="codec_detection")
        assert e.context["video_path"] == "/v.mp4"
        assert e.context["analysis_type"] == "codec_detection"

    def test_analysis_types(self):
        for atype in ["metadata", "duration", "codec_detection", "resolution_detection"]:
            e = VideoAnalysisError("err", analysis_type=atype)
            assert e.context["analysis_type"] == atype

    def test_raise_and_catch(self):
        with pytest.raises(VideoAnalysisError):
            raise VideoAnalysisError("analysis crashed", analysis_type="metadata")


# ── Inheritance chain ─────────────────────────────────────────────────


@pytest.mark.unit
class TestInheritanceChain:
    def test_all_inherit_from_video_error(self):
        for cls in [
            VideoReadError,
            VideoWriteError,
            VideoProcessingError,
            FrameExtractionError,
            AudioExtractionError,
            UnsupportedFormatError,
            VideoAnalysisError,
        ]:
            assert issubclass(cls, VideoError), f"{cls.__name__} must subclass VideoError"

    def test_all_inherit_from_codomyrmex_error(self):
        for cls in [
            VideoError,
            VideoReadError,
            VideoWriteError,
            VideoProcessingError,
            FrameExtractionError,
            AudioExtractionError,
            UnsupportedFormatError,
            VideoAnalysisError,
        ]:
            assert issubclass(cls, CodomyrmexError), (
                f"{cls.__name__} must subclass CodomyrmexError"
            )

    def test_all_are_exceptions(self):
        for cls in [
            VideoError,
            VideoReadError,
            VideoWriteError,
            VideoProcessingError,
            FrameExtractionError,
            AudioExtractionError,
            UnsupportedFormatError,
            VideoAnalysisError,
        ]:
            assert issubclass(cls, Exception), f"{cls.__name__} must subclass Exception"
