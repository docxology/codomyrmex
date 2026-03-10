"""Unit tests for audio speech-to-text data models and configurations.

Covers:
- WhisperModelSize enum
- Word dataclass
- Segment dataclass (including SRT/VTT formatting)
- TranscriptionResult dataclass (including SRT/VTT/JSON/TXT export)
- TranscriptionConfig defaults and custom values
- WHISPER_LANGUAGES integrity
"""

from pathlib import Path

import pytest

from codomyrmex.audio.speech_to_text.models import (
    Segment,
    TranscriptionConfig,
    TranscriptionResult,
    WhisperModelSize,
    Word,
)


@pytest.mark.unit
class TestWhisperModelSize:
    """Tests for WhisperModelSize enum."""

    def test_all_sizes_present(self):
        values = {s.value for s in WhisperModelSize}
        assert "tiny" in values
        assert "base" in values
        assert "small" in values
        assert "medium" in values
        assert "large" in values
        assert "large-v2" in values
        assert "large-v3" in values

    def test_construction(self):
        assert WhisperModelSize("tiny") == WhisperModelSize.TINY

    def test_model_size_ordering(self) -> None:
        """Test WhisperModelSize values in expected order."""
        values = [s.value for s in WhisperModelSize]
        assert values == [
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "large-v2",
            "large-v3",
        ]


@pytest.mark.unit
class TestWord:
    """Tests for Word dataclass."""

    def test_construction(self):
        w = Word(word="hello", start=0.0, end=0.5)
        assert w.word == "hello"
        assert w.start == 0.0
        assert w.end == 0.5
        assert w.probability == 1.0

    def test_duration(self):
        w = Word(word="world", start=1.0, end=1.8)
        assert abs(w.duration - 0.8) < 1e-9

    def test_with_probability(self):
        w = Word(word="uncertain", start=2.0, end=2.5, probability=0.75)
        assert w.probability == 0.75

    def test_zero_duration(self) -> None:
        """Test Word with zero duration."""
        word = Word(word="a", start=1.0, end=1.0, probability=0.5)
        assert word.duration == 0.0


@pytest.mark.unit
class TestSegment:
    """Tests for Segment dataclass."""

    def test_construction(self):
        s = Segment(id=0, start=0.0, end=5.0, text="Hello world.")
        assert s.id == 0
        assert s.start == 0.0
        assert s.end == 5.0
        assert s.text == "Hello world."

    def test_duration(self):
        s = Segment(id=0, start=1.0, end=4.0, text="test")
        assert abs(s.duration - 3.0) < 1e-9

    def test_to_srt_format(self):
        s = Segment(id=0, start=0.0, end=2.5, text="Hello world.")
        srt = s.to_srt_format(1)
        assert "1\n" in srt
        assert "00:00:00,000 --> 00:00:02,500" in srt
        assert "Hello world." in srt

    def test_srt_time_format(self):
        s = Segment(id=0, start=3661.5, end=3662.0, text="test")
        srt = s.to_srt_format(1)
        # 3661.5 seconds = 1 hour, 1 minute, 1 second, 500 ms
        assert "01:01:01,500" in srt

    def test_to_vtt_format(self):
        s = Segment(id=0, start=0.0, end=2.5, text="Hello.")
        vtt = s.to_vtt_format()
        assert "00:00:00.000 --> 00:00:02.500" in vtt
        assert "Hello." in vtt
        assert "," not in vtt

    def test_vtt_time_format(self):
        s = Segment(id=0, start=3661.5, end=3662.0, text="test")
        vtt = s.to_vtt_format()
        assert "01:01:01.500" in vtt

    def test_defaults(self):
        s = Segment(id=0, start=0.0, end=1.0, text="t")
        assert s.words == []
        assert s.avg_logprob == 0.0
        assert s.no_speech_prob == 0.0

    def test_independent_default_words(self):
        s1 = Segment(id=0, start=0.0, end=1.0, text="a")
        s2 = Segment(id=1, start=1.0, end=2.0, text="b")
        s1.words.append(Word(word="hi", start=0.0, end=0.5))
        assert s2.words == []


@pytest.mark.unit
class TestTranscriptionResult:
    """Tests for TranscriptionResult dataclass."""

    def _make_result(self) -> TranscriptionResult:
        return TranscriptionResult(text="Hello world. How are you?")

    def _make_result_with_segments(self):
        """Build a TranscriptionResult with two segments for export tests."""
        words1 = [
            Word(word="Hello", start=0.0, end=0.3, probability=0.98),
            Word(word="world", start=0.4, end=0.8, probability=0.95),
        ]
        words2 = [
            Word(word="Goodbye", start=2.5, end=3.0, probability=0.90),
        ]
        segments = [
            Segment(id=0, start=0.0, end=1.0, text="Hello world.", words=words1),
            Segment(id=1, start=2.5, end=4.0, text="Goodbye.", words=words2),
        ]
        return TranscriptionResult(
            text="Hello world. Goodbye.",
            segments=segments,
            language="en",
            language_probability=0.99,
            duration=4.0,
            processing_time=0.5,
            model_size=WhisperModelSize.BASE,
        )

    def test_construction(self):
        r = self._make_result()
        assert r.text == "Hello world. How are you?"
        assert r.language == "en"
        assert r.segments == []

    def test_minimal_transcription_result(self) -> None:
        """Test TranscriptionResult with only required text field."""
        result = TranscriptionResult(text="Hello world.")
        assert result.text == "Hello world."
        assert result.segments == []
        assert result.language == "en"
        assert result.duration == 0.0

    def test_word_count(self):
        r = TranscriptionResult(text="one two three")
        assert r.word_count == 3

    def test_word_count_empty(self):
        r = TranscriptionResult(text="")
        assert r.word_count == 0

    def test_segment_count(self):
        r = TranscriptionResult(text="t")
        r.segments.append(Segment(id=0, start=0.0, end=1.0, text="t"))
        assert r.segment_count == 1

    def test_to_txt(self):
        r = TranscriptionResult(text="plain text here")
        assert r.to_txt() == "plain text here"

    def test_to_srt_empty(self):
        r = TranscriptionResult(text="")
        assert r.to_srt() == ""

    def test_to_srt_with_segment(self):
        r = TranscriptionResult(text="Hello.")
        r.segments.append(Segment(id=0, start=0.0, end=1.0, text="Hello."))
        srt = r.to_srt()
        assert "Hello." in srt
        assert "1\n" in srt
        assert "00:00:00,000 --> 00:00:01,000" in srt

    def test_to_vtt_starts_with_webvtt(self):
        r = TranscriptionResult(text="test")
        vtt = r.to_vtt()
        assert vtt.startswith("WEBVTT")

    def test_to_vtt_uses_dot_milliseconds(self) -> None:
        """Test VTT timestamps use period separator."""
        result = self._make_result_with_segments()
        vtt = result.to_vtt()
        assert "00:00:00.000 --> 00:00:01.000" in vtt

    def test_to_json_basic(self):
        r = TranscriptionResult(
            text="Hello.",
            language="fr",
            duration=5.0,
            model_size=WhisperModelSize.SMALL,
        )
        j = r.to_json()
        assert j["text"] == "Hello."
        assert j["language"] == "fr"
        assert j["duration"] == 5.0
        assert j["model_size"] == "small"
        assert j["segments"] == []

    def test_to_json_with_segment_words(self):
        w = Word(word="hello", start=0.0, end=0.3, probability=0.95)
        seg = Segment(id=0, start=0.0, end=1.0, text="hello", words=[w])
        r = TranscriptionResult(text="hello", segments=[seg])
        j = r.to_json()
        assert len(j["segments"]) == 1
        assert len(j["segments"][0]["words"]) == 1
        assert j["segments"][0]["words"][0]["word"] == "hello"

    def test_save_srt(self, tmp_path: Path):
        r = TranscriptionResult(text="Test.")
        r.segments.append(Segment(id=0, start=0.0, end=1.0, text="Test."))
        out = r.save_srt(tmp_path / "out.srt")
        assert out.exists()
        assert isinstance(out, Path)
        content = out.read_text()
        assert "Test." in content

    def test_save_vtt(self, tmp_path: Path):
        r = TranscriptionResult(text="Test.")
        r.segments.append(Segment(id=0, start=0.0, end=1.0, text="Test."))
        out = r.save_vtt(tmp_path / "out.vtt")
        assert out.exists()
        content = out.read_text()
        assert "WEBVTT" in content

    def test_source_path_handling(self) -> None:
        """Test TranscriptionResult stores and serializes source_path."""
        p = Path("/audio/file.mp3")
        result = TranscriptionResult(text="test", source_path=p)
        assert result.source_path == p
        j = result.to_json()
        assert "/audio/file.mp3" in j["source_path"]


@pytest.mark.unit
class TestTranscriptionConfig:
    """Tests for TranscriptionConfig."""

    def test_defaults(self):
        config = TranscriptionConfig()
        assert config.language is None
        assert config.task == "transcribe"
        assert config.beam_size == 5
        assert config.best_of == 5
        assert config.word_timestamps is True
        assert config.vad_filter is True

    def test_custom_values(self):
        config = TranscriptionConfig(language="fr", task="translate", beam_size=10)
        assert config.language == "fr"
        assert config.task == "translate"
        assert config.beam_size == 10

    def test_temperature_tuple_default(self):
        config = TranscriptionConfig()
        assert isinstance(config.temperature, tuple)
        assert 0.0 in config.temperature


@pytest.mark.unit
class TestWhisperLanguages:
    """Tests for WHISPER_LANGUAGES list integrity."""

    def test_whisper_languages_contains_common_languages(self) -> None:
        """Test WHISPER_LANGUAGES contains widely-spoken languages."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_LANGUAGES

        for lang in ("en", "es", "fr", "de", "zh", "ja"):
            assert lang in WHISPER_LANGUAGES

    def test_whisper_languages_all_lowercase(self) -> None:
        """Test all WHISPER_LANGUAGES codes are lowercase."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_LANGUAGES

        for lang in WHISPER_LANGUAGES:
            assert lang == lang.lower()
