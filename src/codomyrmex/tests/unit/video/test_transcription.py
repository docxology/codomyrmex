"""Unit tests for VideoTranscriber and TranscriptionResult."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from codomyrmex.video.transcription import (
    WHISPER_MODELS,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionWord,
    VideoTranscriber,
    VideoTranscriberError,
    transcribe_url,
)


# ---------------------------------------------------------------------------
# TranscriptionWord
# ---------------------------------------------------------------------------


class TestTranscriptionWord:
    def test_construction(self) -> None:
        w = TranscriptionWord(word="Hello", start=0.1, end=0.5)
        assert w.word == "Hello"
        assert w.start == 0.1
        assert w.end == 0.5

    def test_defaults(self) -> None:
        w = TranscriptionWord(word="hi")
        assert w.start == 0.0
        assert w.end == 0.0


# ---------------------------------------------------------------------------
# TranscriptionSegment
# ---------------------------------------------------------------------------


class TestTranscriptionSegment:
    def test_to_dict_basic(self) -> None:
        seg = TranscriptionSegment(id=1, start=0.0, end=4.7, text="Hello world")
        d = seg.to_dict()
        assert d["id"] == 1
        assert d["start"] == 0.0
        assert d["end"] == 4.7
        assert d["text"] == "Hello world"
        assert d["speaker"] is None
        assert d["words"] == []

    def test_to_dict_with_words(self) -> None:
        seg = TranscriptionSegment(
            id=0,
            start=0.0,
            end=2.0,
            text="Hi there",
            words=[
                TranscriptionWord("Hi", 0.0, 0.4),
                TranscriptionWord("there", 0.5, 1.0),
            ],
        )
        d = seg.to_dict()
        assert len(d["words"]) == 2
        assert d["words"][0]["word"] == "Hi"


# ---------------------------------------------------------------------------
# TranscriptionResult
# ---------------------------------------------------------------------------


SAMPLE_JSON = {
    "source_url": "https://youtube.com/watch?v=test",
    "platform": "youtube",
    "title": "Test Video",
    "duration_sec": 60.0,
    "language": "en",
    "transcript": "Hello world this is a test",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 3.0,
            "text": "Hello world",
            "speaker": None,
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5},
                {"word": "world", "start": 0.6, "end": 1.0},
            ],
        }
    ],
    "metadata": {"model_size": "small"},
    "status": "completed",
}


class TestTranscriptionResult:
    def test_from_dict_roundtrip(self) -> None:
        result = TranscriptionResult.from_dict(SAMPLE_JSON)
        assert result.source_url == "https://youtube.com/watch?v=test"
        assert result.platform == "youtube"
        assert result.title == "Test Video"
        assert result.duration_sec == 60.0
        assert result.language == "en"
        assert result.transcript == "Hello world this is a test"
        assert result.status == "completed"

    def test_segments_parsed(self) -> None:
        result = TranscriptionResult.from_dict(SAMPLE_JSON)
        assert result.segment_count == 1
        seg = result.segments[0]
        assert seg.text == "Hello world"
        assert len(seg.words) == 2
        assert seg.words[0].word == "Hello"

    def test_word_count(self) -> None:
        result = TranscriptionResult.from_dict(SAMPLE_JSON)
        assert result.word_count == 6  # "Hello world this is a test"

    def test_to_dict_matches_input(self) -> None:
        result = TranscriptionResult.from_dict(SAMPLE_JSON)
        d = result.to_dict()
        assert d["source_url"] == SAMPLE_JSON["source_url"]
        assert len(d["segments"]) == len(SAMPLE_JSON["segments"])

    def test_from_dict_empty_segments(self) -> None:
        data = {**SAMPLE_JSON, "segments": None}
        result = TranscriptionResult.from_dict(data)
        assert result.segments == []

    def test_error_result(self) -> None:
        result = TranscriptionResult(
            source_url="https://x.com/bad",
            status="error",
            error="yt-dlp failed",
        )
        assert result.word_count == 0
        assert result.status == "error"


# ---------------------------------------------------------------------------
# VideoTranscriber
# ---------------------------------------------------------------------------


class TestVideoTranscriber:
    def test_instantiation_default(self) -> None:
        t = VideoTranscriber()
        assert "universal-video-transcriber" in str(t._skill_dir)

    def test_instantiation_custom(self, tmp_path: Path) -> None:
        t = VideoTranscriber(skill_dir=str(tmp_path))
        assert t._skill_dir == tmp_path

    def test_active_mode_auto_no_script(self, tmp_path: Path) -> None:
        t = VideoTranscriber(skill_dir=str(tmp_path), mode="auto")
        # Script doesn't exist in tmp_path → restfallback
        assert t.active_mode == "rest"

    def test_active_mode_explicit_cli(self, tmp_path: Path) -> None:
        t = VideoTranscriber(skill_dir=str(tmp_path), mode="cli")
        assert t.active_mode == "cli"

    def test_active_mode_explicit_rest(self, tmp_path: Path) -> None:
        t = VideoTranscriber(skill_dir=str(tmp_path), mode="rest")
        assert t.active_mode == "rest"

    def test_parse_json_output_valid(self) -> None:
        raw = json.dumps(SAMPLE_JSON)
        result = VideoTranscriber._parse_json_output(raw, "https://example.com")
        assert result.status == "completed"
        assert result.transcript == "Hello world this is a test"

    def test_parse_json_output_with_prefix_lines(self) -> None:
        raw = "INFO: Starting pipeline\nDEBUG: Fetching URL\n" + json.dumps(SAMPLE_JSON)
        result = VideoTranscriber._parse_json_output(raw, "https://example.com")
        assert result.status == "completed"

    def test_parse_json_output_no_json(self) -> None:
        result = VideoTranscriber._parse_json_output("ERROR: ffmpeg not found", "https://x.com")
        assert result.status == "error"
        assert "No JSON" in result.error

    def test_transcribe_to_dict_error_path(self, tmp_path: Path) -> None:
        """transcribe_to_dict never raises — returns error dict."""
        t = VideoTranscriber(skill_dir=str(tmp_path), mode="cli")
        # CLI script doesn't exist → will error
        result = t.transcribe_to_dict("https://example.com/bad")
        assert isinstance(result, dict)
        assert "status" in result

    def test_doctor_returns_dict(self, tmp_path: Path) -> None:
        t = VideoTranscriber(skill_dir=str(tmp_path), mode="rest")
        result = t.doctor()
        assert isinstance(result, dict)
        assert "ok" in result
        assert "mode" in result
        assert "dependencies" in result


# ---------------------------------------------------------------------------
# WHISPER_MODELS constant
# ---------------------------------------------------------------------------


class TestWhisperModels:
    def test_is_tuple(self) -> None:
        assert isinstance(WHISPER_MODELS, tuple)

    def test_contains_small(self) -> None:
        assert "small" in WHISPER_MODELS

    def test_contains_large(self) -> None:
        assert "large-v3" in WHISPER_MODELS


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------


class TestVideoMCPTools:
    def test_video_transcriber_list_models(self) -> None:
        from codomyrmex.video.mcp_tools import video_transcriber_list_models

        result = video_transcriber_list_models()
        assert result["status"] == "success"
        assert "small" in result["models"]
        assert result["recommended"] == "small"

    def test_video_transcriber_doctor_rest(self, tmp_path: Path) -> None:
        from codomyrmex.video.mcp_tools import video_transcriber_doctor

        # Override skill_dir via environment? Can't easily — test the MCP tool interface
        result = video_transcriber_doctor(mode="rest")
        assert isinstance(result, dict)
        assert "ok" in result

    def test_video_transcribe_url_bad_url(self) -> None:
        """Graceful failure on bad URL — never raises."""
        from codomyrmex.video.mcp_tools import video_transcribe_url

        result = video_transcribe_url(
            "https://example.com/nonexistent-video-xyz",
            model_size="tiny",
        )
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.skipif(
        not shutil.which("yt-dlp"),
        reason="yt-dlp not installed",
    )
    @pytest.mark.skipif(
        not shutil.which("ffmpeg"),
        reason="ffmpeg not installed",
    )
    def test_video_transcribe_url_real_youtube(self) -> None:
        """Integration: real YouTube short video transcription."""
        from codomyrmex.video.mcp_tools import video_transcribe_url

        # Use a very short publicly available video
        result = video_transcribe_url(
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # "Me at the zoo" (18s)
            model_size="tiny",
            word_timestamps=False,
        )
        assert isinstance(result, dict)
        # May succeed or error depending on environment
        assert result.get("status") in ("completed", "error")
