"""Tests for audio.speech_to_text.models."""

from pathlib import Path

from codomyrmex.audio.speech_to_text.models import (
    Segment,
    TranscriptionConfig,
    TranscriptionResult,
    WhisperModelSize,
    Word,
)


class TestWhisperModelSize:
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


class TestWord:
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


class TestSegment:
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
        assert "-->" in srt
        assert "Hello world." in srt

    def test_srt_time_format(self):
        s = Segment(id=0, start=3661.5, end=3662.0, text="test")
        srt = s.to_srt_format(1)
        # 3661.5 seconds = 1 hour, 1 minute, 1 second, 500 ms
        assert "01:01:01,500" in srt

    def test_to_vtt_format(self):
        s = Segment(id=0, start=0.0, end=2.5, text="Hello.")
        vtt = s.to_vtt_format()
        assert "-->" in vtt
        assert "Hello." in vtt
        # VTT uses dot separator for millis
        assert "," not in vtt or "." in vtt

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


class TestTranscriptionResult:
    def _make_result(self) -> TranscriptionResult:
        return TranscriptionResult(text="Hello world. How are you?")

    def test_construction(self):
        r = self._make_result()
        assert r.text == "Hello world. How are you?"
        assert r.language == "en"
        assert r.segments == []

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

    def test_to_vtt_starts_with_webvtt(self):
        r = TranscriptionResult(text="test")
        vtt = r.to_vtt()
        assert vtt.startswith("WEBVTT")

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

    def test_to_json_no_model_size(self):
        r = TranscriptionResult(text="t")
        j = r.to_json()
        assert j["model_size"] is None

    def test_to_json_no_source_path(self):
        r = TranscriptionResult(text="t")
        j = r.to_json()
        assert j["source_path"] is None

    def test_to_json_with_source_path(self):
        r = TranscriptionResult(text="t", source_path=Path("/audio.mp3"))
        j = r.to_json()
        assert "audio.mp3" in j["source_path"]

    def test_to_json_with_segment_words(self):
        w = Word(word="hello", start=0.0, end=0.3, probability=0.95)
        seg = Segment(id=0, start=0.0, end=1.0, text="hello", words=[w])
        r = TranscriptionResult(text="hello", segments=[seg])
        j = r.to_json()
        assert len(j["segments"]) == 1
        assert len(j["segments"][0]["words"]) == 1
        assert j["segments"][0]["words"][0]["word"] == "hello"

    def test_save_srt(self, tmp_path):
        r = TranscriptionResult(text="Test.")
        r.segments.append(Segment(id=0, start=0.0, end=1.0, text="Test."))
        out = r.save_srt(tmp_path / "out.srt")
        assert out.exists()
        content = out.read_text()
        assert "Test." in content

    def test_save_vtt(self, tmp_path):
        r = TranscriptionResult(text="Test.")
        r.segments.append(Segment(id=0, start=0.0, end=1.0, text="Test."))
        out = r.save_vtt(tmp_path / "out.vtt")
        assert out.exists()
        content = out.read_text()
        assert "WEBVTT" in content


class TestTranscriptionConfig:
    def test_defaults(self):
        config = TranscriptionConfig()
        assert config.language is None
        assert config.task == "transcribe"
        assert config.beam_size == 5
        assert config.best_of == 5
        assert config.word_timestamps is True
        assert config.vad_filter is True

    def test_custom_language(self):
        config = TranscriptionConfig(language="fr")
        assert config.language == "fr"

    def test_translate_task(self):
        config = TranscriptionConfig(task="translate")
        assert config.task == "translate"

    def test_temperature_tuple_default(self):
        config = TranscriptionConfig()
        assert isinstance(config.temperature, tuple)
        assert 0.0 in config.temperature
