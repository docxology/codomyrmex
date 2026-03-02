"""Unit tests for the transcription interface and data models.

Tests cover:
- TranscriptionResult dataclass creation and properties
- TranscriptionResult export methods (to_srt, to_vtt, to_txt, to_json)
- TranscriptionResult file save methods (save_srt, save_vtt)
- TranscriptionConfig defaults and custom values
- Segment time formatting (_format_time_srt, _format_time_vtt)
- Word dataclass properties
- WhisperModelSize enum completeness
- WHISPER_LANGUAGES list integrity
"""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestTranscriptionResultCreation:
    """Tests for TranscriptionResult dataclass construction and properties."""

    def test_minimal_transcription_result(self) -> None:
        """Test TranscriptionResult with only required text field."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionResult

        result = TranscriptionResult(text="Hello world.")
        assert result.text == "Hello world."
        assert result.segments == []
        assert result.language == "en"
        assert result.duration == 0.0

    def test_transcription_result_word_count(self) -> None:
        """Test word_count property splits on whitespace."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionResult

        result = TranscriptionResult(text="one two three four five")
        assert result.word_count == 5

    def test_transcription_result_word_count_empty(self) -> None:
        """Test word_count property for empty text returns one empty string split."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionResult

        result = TranscriptionResult(text="")
        # "".split() returns [] which has length 0... but actually
        # "".split() returns [''] which is length 1? Let's verify:
        # Actually "".split() returns [] in Python. So word_count=0.
        assert result.word_count == 0

    def test_transcription_result_segment_count(self) -> None:
        """Test segment_count property."""
        from codomyrmex.audio.speech_to_text.models import Segment, TranscriptionResult

        segments = [
            Segment(id=0, start=0.0, end=1.0, text="one"),
            Segment(id=1, start=1.0, end=2.0, text="two"),
            Segment(id=2, start=2.0, end=3.0, text="three"),
        ]
        result = TranscriptionResult(text="one two three", segments=segments)
        assert result.segment_count == 3

    def test_transcription_result_language_probability_default(self) -> None:
        """Test language_probability defaults to 1.0."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionResult

        result = TranscriptionResult(text="test")
        assert result.language_probability == 1.0

    def test_transcription_result_source_path_default(self) -> None:
        """Test source_path defaults to None."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionResult

        result = TranscriptionResult(text="test")
        assert result.source_path is None

    def test_transcription_result_with_source_path(self) -> None:
        """Test TranscriptionResult stores source_path."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionResult

        result = TranscriptionResult(
            text="test", source_path=Path("/audio/file.mp3")
        )
        assert result.source_path == Path("/audio/file.mp3")


@pytest.mark.unit
class TestTranscriptionResultExport:
    """Tests for TranscriptionResult export formats."""

    def _make_result_with_segments(self):
        """Build a TranscriptionResult with two segments for export tests."""
        from codomyrmex.audio.speech_to_text.models import (
            Segment,
            TranscriptionResult,
            WhisperModelSize,
            Word,
        )

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

    def test_to_srt_contains_indices(self) -> None:
        """Test SRT output contains 1-based segment indices."""
        result = self._make_result_with_segments()
        srt = result.to_srt()
        assert "1\n" in srt
        assert "2\n" in srt

    def test_to_srt_contains_timestamps(self) -> None:
        """Test SRT output contains properly formatted timestamps."""
        result = self._make_result_with_segments()
        srt = result.to_srt()
        assert "00:00:00,000 --> 00:00:01,000" in srt

    def test_to_srt_contains_text(self) -> None:
        """Test SRT output contains segment text."""
        result = self._make_result_with_segments()
        srt = result.to_srt()
        assert "Hello world." in srt
        assert "Goodbye." in srt

    def test_to_vtt_starts_with_header(self) -> None:
        """Test VTT output starts with WEBVTT header."""
        result = self._make_result_with_segments()
        vtt = result.to_vtt()
        assert vtt.startswith("WEBVTT")

    def test_to_vtt_uses_dot_milliseconds(self) -> None:
        """Test VTT timestamps use period separator (not comma like SRT)."""
        result = self._make_result_with_segments()
        vtt = result.to_vtt()
        assert "00:00:00.000 --> 00:00:01.000" in vtt

    def test_to_txt_returns_plain_text(self) -> None:
        """Test to_txt returns the raw transcription text."""
        result = self._make_result_with_segments()
        assert result.to_txt() == "Hello world. Goodbye."

    def test_to_json_returns_dict(self) -> None:
        """Test to_json returns a dictionary."""
        result = self._make_result_with_segments()
        data = result.to_json()
        assert isinstance(data, dict)

    def test_to_json_contains_text(self) -> None:
        """Test to_json includes the full text."""
        result = self._make_result_with_segments()
        data = result.to_json()
        assert data["text"] == "Hello world. Goodbye."

    def test_to_json_contains_language(self) -> None:
        """Test to_json includes detected language."""
        result = self._make_result_with_segments()
        data = result.to_json()
        assert data["language"] == "en"

    def test_to_json_model_size_as_string(self) -> None:
        """Test to_json serializes model_size enum to string value."""
        result = self._make_result_with_segments()
        data = result.to_json()
        assert data["model_size"] == "base"

    def test_to_json_model_size_none(self) -> None:
        """Test to_json handles model_size=None."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionResult

        result = TranscriptionResult(text="test")
        data = result.to_json()
        assert data["model_size"] is None

    def test_to_json_segments_include_words(self) -> None:
        """Test to_json segments contain word-level detail."""
        result = self._make_result_with_segments()
        data = result.to_json()
        seg0 = data["segments"][0]
        assert len(seg0["words"]) == 2
        assert seg0["words"][0]["word"] == "Hello"
        assert seg0["words"][0]["probability"] == 0.98


@pytest.mark.unit
class TestTranscriptionResultSave:
    """Tests for TranscriptionResult save_srt and save_vtt file methods."""

    def _make_result(self):
        """Build a minimal TranscriptionResult with one segment."""
        from codomyrmex.audio.speech_to_text.models import (
            Segment,
            TranscriptionResult,
        )

        segments = [
            Segment(id=0, start=0.0, end=2.0, text="Testing save."),
        ]
        return TranscriptionResult(text="Testing save.", segments=segments)

    def test_save_srt_creates_file(self, tmp_path: Path) -> None:
        """Test save_srt creates an SRT file on disk."""
        result = self._make_result()
        output = tmp_path / "output.srt"
        saved = result.save_srt(output)
        assert saved.exists()

    def test_save_srt_returns_path(self, tmp_path: Path) -> None:
        """Test save_srt returns a Path object."""
        result = self._make_result()
        output = tmp_path / "output.srt"
        saved = result.save_srt(output)
        assert isinstance(saved, Path)

    def test_save_srt_content_is_valid(self, tmp_path: Path) -> None:
        """Test save_srt file content is valid SRT."""
        result = self._make_result()
        output = tmp_path / "output.srt"
        result.save_srt(output)
        content = output.read_text(encoding="utf-8")
        assert "1\n" in content
        assert "Testing save." in content

    def test_save_srt_accepts_string_path(self, tmp_path: Path) -> None:
        """Test save_srt accepts a string path."""
        result = self._make_result()
        output = str(tmp_path / "output.srt")
        saved = result.save_srt(output)
        assert Path(saved).exists()

    def test_save_vtt_creates_file(self, tmp_path: Path) -> None:
        """Test save_vtt creates a VTT file on disk."""
        result = self._make_result()
        output = tmp_path / "output.vtt"
        saved = result.save_vtt(output)
        assert saved.exists()

    def test_save_vtt_content_starts_with_header(self, tmp_path: Path) -> None:
        """Test save_vtt file starts with WEBVTT header."""
        result = self._make_result()
        output = tmp_path / "output.vtt"
        result.save_vtt(output)
        content = output.read_text(encoding="utf-8")
        assert content.startswith("WEBVTT")


@pytest.mark.unit
class TestSegmentTimeFormatting:
    """Tests for Segment SRT and VTT time formatting static methods."""

    def test_format_time_srt_zero(self) -> None:
        """Test SRT time formatting for 0 seconds."""
        from codomyrmex.audio.speech_to_text.models import Segment

        assert Segment._format_time_srt(0.0) == "00:00:00,000"

    def test_format_time_srt_with_milliseconds(self) -> None:
        """Test SRT time formatting preserves milliseconds."""
        from codomyrmex.audio.speech_to_text.models import Segment

        assert Segment._format_time_srt(1.5) == "00:00:01,500"

    def test_format_time_srt_minutes(self) -> None:
        """Test SRT time formatting handles minutes."""
        from codomyrmex.audio.speech_to_text.models import Segment

        # 90 seconds = 1 minute 30 seconds
        assert Segment._format_time_srt(90.0) == "00:01:30,000"

    def test_format_time_srt_hours(self) -> None:
        """Test SRT time formatting handles hours."""
        from codomyrmex.audio.speech_to_text.models import Segment

        # 3661.123 = 1h 1m 1.123s
        assert Segment._format_time_srt(3661.123) == "01:01:01,123"

    def test_format_time_vtt_zero(self) -> None:
        """Test VTT time formatting for 0 seconds."""
        from codomyrmex.audio.speech_to_text.models import Segment

        assert Segment._format_time_vtt(0.0) == "00:00:00.000"

    def test_format_time_vtt_uses_period(self) -> None:
        """Test VTT time formatting uses period for millisecond separator."""
        from codomyrmex.audio.speech_to_text.models import Segment

        formatted = Segment._format_time_vtt(1.5)
        assert "." in formatted
        assert "," not in formatted

    def test_format_time_srt_uses_comma(self) -> None:
        """Test SRT time formatting uses comma for millisecond separator."""
        from codomyrmex.audio.speech_to_text.models import Segment

        formatted = Segment._format_time_srt(1.5)
        assert "," in formatted
        assert formatted.count(".") == 0

    def test_segment_duration_property(self) -> None:
        """Test Segment duration computed property."""
        from codomyrmex.audio.speech_to_text.models import Segment

        segment = Segment(id=0, start=1.5, end=4.0, text="test")
        assert segment.duration == 2.5

    def test_segment_to_srt_format_output(self) -> None:
        """Test complete SRT format output for a segment."""
        from codomyrmex.audio.speech_to_text.models import Segment

        segment = Segment(id=0, start=0.0, end=2.5, text="  Hello world.  ")
        srt = segment.to_srt_format(1)
        lines = srt.split("\n")
        assert lines[0] == "1"
        assert lines[1] == "00:00:00,000 --> 00:00:02,500"
        assert lines[2] == "Hello world."

    def test_segment_to_vtt_format_output(self) -> None:
        """Test complete VTT format output for a segment."""
        from codomyrmex.audio.speech_to_text.models import Segment

        segment = Segment(id=0, start=0.0, end=2.5, text="  Hello world.  ")
        vtt = segment.to_vtt_format()
        lines = vtt.split("\n")
        assert lines[0] == "00:00:00.000 --> 00:00:02.500"
        assert lines[1] == "Hello world."


@pytest.mark.unit
class TestTranscriptionConfig:
    """Tests for TranscriptionConfig defaults and custom values."""

    def test_transcription_config_defaults(self) -> None:
        """Test TranscriptionConfig default values."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionConfig

        config = TranscriptionConfig()
        assert config.language is None
        assert config.task == "transcribe"
        assert config.beam_size == 5
        assert config.best_of == 5
        assert config.patience == 1.0
        assert config.word_timestamps is True
        assert config.vad_filter is True
        assert config.vad_parameters is None

    def test_transcription_config_temperature_default(self) -> None:
        """Test TranscriptionConfig default temperature is a tuple."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionConfig

        config = TranscriptionConfig()
        assert isinstance(config.temperature, tuple)
        assert config.temperature[0] == 0.0

    def test_transcription_config_custom_language(self) -> None:
        """Test TranscriptionConfig with custom language."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionConfig

        config = TranscriptionConfig(language="es")
        assert config.language == "es"

    def test_transcription_config_translate_task(self) -> None:
        """Test TranscriptionConfig with translate task."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionConfig

        config = TranscriptionConfig(task="translate")
        assert config.task == "translate"

    def test_transcription_config_threshold_defaults(self) -> None:
        """Test TranscriptionConfig threshold default values."""
        from codomyrmex.audio.speech_to_text.models import TranscriptionConfig

        config = TranscriptionConfig()
        assert config.compression_ratio_threshold == 2.4
        assert config.log_prob_threshold == -1.0
        assert config.no_speech_threshold == 0.6


@pytest.mark.unit
class TestWordDataclass:
    """Tests for Word dataclass and its properties."""

    def test_word_duration(self) -> None:
        """Test Word duration computed property."""
        from codomyrmex.audio.speech_to_text.models import Word

        word = Word(word="hello", start=1.0, end=1.5, probability=0.9)
        assert word.duration == 0.5

    def test_word_default_probability(self) -> None:
        """Test Word default probability is 1.0."""
        from codomyrmex.audio.speech_to_text.models import Word

        word = Word(word="test", start=0.0, end=0.5)
        assert word.probability == 1.0

    def test_word_zero_duration(self) -> None:
        """Test Word with zero duration."""
        from codomyrmex.audio.speech_to_text.models import Word

        word = Word(word="a", start=1.0, end=1.0, probability=0.5)
        assert word.duration == 0.0

    def test_word_stores_text(self) -> None:
        """Test Word stores the word text accurately."""
        from codomyrmex.audio.speech_to_text.models import Word

        word = Word(word="supercalifragilistic", start=0.0, end=2.0)
        assert word.word == "supercalifragilistic"


@pytest.mark.unit
class TestWhisperModelSizeEnum:
    """Tests for WhisperModelSize enum completeness."""

    def test_model_size_count(self) -> None:
        """Test WhisperModelSize has exactly 7 members."""
        from codomyrmex.audio.speech_to_text.models import WhisperModelSize

        assert len(list(WhisperModelSize)) == 7

    def test_model_sizes_are_strings(self) -> None:
        """Test all WhisperModelSize values are strings."""
        from codomyrmex.audio.speech_to_text.models import WhisperModelSize

        for size in WhisperModelSize:
            assert isinstance(size.value, str)

    def test_model_size_ordering(self) -> None:
        """Test WhisperModelSize values in expected order."""
        from codomyrmex.audio.speech_to_text.models import WhisperModelSize

        values = [s.value for s in WhisperModelSize]
        assert values == ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]


@pytest.mark.unit
class TestWhisperLanguages:
    """Tests for WHISPER_LANGUAGES list integrity."""

    def test_whisper_languages_is_list(self) -> None:
        """Test WHISPER_LANGUAGES is a list."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_LANGUAGES

        assert isinstance(WHISPER_LANGUAGES, list)

    def test_whisper_languages_contains_common_languages(self) -> None:
        """Test WHISPER_LANGUAGES contains widely-spoken languages."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_LANGUAGES

        for lang in ("en", "es", "fr", "de", "zh", "ja", "ko", "ar", "hi", "pt"):
            assert lang in WHISPER_LANGUAGES, f"Missing language: {lang}"

    def test_whisper_languages_minimum_count(self) -> None:
        """Test WHISPER_LANGUAGES has at least 90 entries."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_LANGUAGES

        assert len(WHISPER_LANGUAGES) >= 90

    def test_whisper_languages_all_lowercase(self) -> None:
        """Test all WHISPER_LANGUAGES codes are lowercase."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_LANGUAGES

        for lang in WHISPER_LANGUAGES:
            assert lang == lang.lower(), f"Language code not lowercase: {lang!r}"

    def test_whisper_languages_no_duplicates(self) -> None:
        """Test WHISPER_LANGUAGES has no duplicate entries."""
        from codomyrmex.audio.speech_to_text.providers import WHISPER_LANGUAGES

        assert len(WHISPER_LANGUAGES) == len(set(WHISPER_LANGUAGES))
