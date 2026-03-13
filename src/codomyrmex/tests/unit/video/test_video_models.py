"""Tests for video.models."""

from pathlib import Path

from codomyrmex.video.models import (
    AudioCodec,
    ExtractionResult,
    FilterType,
    ProcessingResult,
    VideoCodec,
    VideoComparison,
    VideoInfo,
)


class TestFilterType:
    def test_has_grayscale(self):
        assert FilterType.GRAYSCALE.value == "grayscale"

    def test_has_rotations(self):
        assert FilterType.ROTATE_90.value == "rotate_90"
        assert FilterType.ROTATE_180.value == "rotate_180"
        assert FilterType.ROTATE_270.value == "rotate_270"

    def test_count(self):
        assert len(FilterType) >= 10


class TestVideoCodec:
    def test_h264(self):
        assert VideoCodec.H264.value == "libx264"

    def test_h265(self):
        assert VideoCodec.H265.value == "libx265"

    def test_count(self):
        assert len(VideoCodec) >= 5


class TestAudioCodec:
    def test_aac(self):
        assert AudioCodec.AAC.value == "aac"

    def test_opus(self):
        assert AudioCodec.OPUS.value == "libopus"


class TestVideoInfo:
    def test_construction(self):
        p = Path("/videos/test.mp4")
        info = VideoInfo(file_path=p, duration=120.0, width=1920, height=1080, fps=30.0)
        assert info.file_path == p
        assert info.duration == 120.0
        assert info.width == 1920
        assert info.height == 1080

    def test_resolution(self):
        info = VideoInfo(file_path=Path("v.mp4"), width=1280, height=720)
        assert info.resolution == (1280, 720)

    def test_aspect_ratio(self):
        info = VideoInfo(file_path=Path("v.mp4"), width=1920, height=1080)
        assert abs(info.aspect_ratio - 16 / 9) < 0.01

    def test_aspect_ratio_zero_height(self):
        info = VideoInfo(file_path=Path("v.mp4"), width=1920, height=0)
        assert info.aspect_ratio == 0.0

    def test_file_size_mb(self):
        info = VideoInfo(file_path=Path("v.mp4"), file_size=1024 * 1024)
        assert info.file_size_mb == 1.0

    def test_to_dict(self):
        info = VideoInfo(
            file_path=Path("/v.mp4"),
            width=640,
            height=480,
            fps=24.0,
            video_codec="h264",
            has_audio=True,
        )
        d = info.to_dict()
        assert d["width"] == 640
        assert d["height"] == 480
        assert d["fps"] == 24.0
        assert d["has_audio"] is True
        assert "file_path" in d

    def test_defaults(self):
        info = VideoInfo(file_path=Path("v.mp4"))
        assert info.duration == 0.0
        assert info.has_audio is False
        assert info.audio_codec is None


class TestProcessingResult:
    def test_construction(self):
        r = ProcessingResult(output_path=Path("/out/video.mp4"))
        assert r.success is True
        assert r.operation == ""

    def test_file_size_mb(self):
        r = ProcessingResult(output_path=Path("o.mp4"), file_size=2 * 1024 * 1024)
        assert r.file_size_mb == 2.0

    def test_to_dict(self):
        r = ProcessingResult(
            output_path=Path("/out/video.mp4"),
            duration=60.0,
            operation="resize",
            success=True,
            message="done",
        )
        d = r.to_dict()
        assert "output_path" in d
        assert d["duration"] == 60.0
        assert d["operation"] == "resize"
        assert d["success"] is True
        assert d["message"] == "done"


class TestExtractionResult:
    def test_construction(self):
        r = ExtractionResult(source_path=Path("/video.mp4"))
        assert r.frame_count == 0
        assert r.frames == []
        assert r.audio_path is None

    def test_to_dict_no_audio(self):
        r = ExtractionResult(
            source_path=Path("/video.mp4"),
            timestamps=[0.5, 1.0, 1.5],
            output_paths=[Path("/f1.jpg"), Path("/f2.jpg"), Path("/f3.jpg")],
            frame_count=3,
        )
        d = r.to_dict()
        assert d["timestamps"] == [0.5, 1.0, 1.5]
        assert len(d["output_paths"]) == 3
        assert d["audio_path"] is None
        assert d["frame_count"] == 3

    def test_to_dict_with_audio(self):
        r = ExtractionResult(
            source_path=Path("/video.mp4"), audio_path=Path("/audio.wav")
        )
        d = r.to_dict()
        assert d["audio_path"] is not None
        assert "audio.wav" in d["audio_path"]

    def test_independent_default_lists(self):
        r1 = ExtractionResult(source_path=Path("a.mp4"))
        r2 = ExtractionResult(source_path=Path("b.mp4"))
        r1.timestamps.append(1.0)
        assert r2.timestamps == []


class TestVideoComparison:
    def test_construction(self):
        vc = VideoComparison(video1_path=Path("v1.mp4"), video2_path=Path("v2.mp4"))
        assert vc.same_resolution is False
        assert vc.same_duration is False
        assert vc.duration_diff == 0.0
        assert vc.size_diff == 0

    def test_with_match_flags(self):
        vc = VideoComparison(
            video1_path=Path("v1.mp4"),
            video2_path=Path("v2.mp4"),
            same_resolution=True,
            same_fps=True,
            duration_diff=0.5,
            size_diff=1024,
        )
        assert vc.same_resolution is True
        assert vc.same_fps is True
        assert vc.duration_diff == 0.5
        assert vc.size_diff == 1024

    def test_independent_default_details(self):
        vc1 = VideoComparison(video1_path=Path("a.mp4"), video2_path=Path("b.mp4"))
        vc2 = VideoComparison(video1_path=Path("c.mp4"), video2_path=Path("d.mp4"))
        vc1.details["key"] = "val"
        assert vc2.details == {}
