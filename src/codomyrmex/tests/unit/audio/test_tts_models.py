"""Unit tests for audio text-to-speech data models and configurations.

Covers:
- AudioFormat enum
- VoiceGender enum
- VoiceInfo dataclass (including dict serialization)
- SynthesisResult dataclass (including file I/O and dict serialization)
- TTSConfig defaults and custom values
- SSMLOptions defaults and custom values
"""

from pathlib import Path

import pytest

from codomyrmex.audio.text_to_speech.models import (
    AudioFormat,
    SSMLOptions,
    SynthesisResult,
    TTSConfig,
    VoiceGender,
    VoiceInfo,
)


@pytest.mark.unit
class TestAudioFormat:
    """Tests for AudioFormat enum."""

    def test_values(self):
        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.OGG.value == "ogg"
        assert AudioFormat.FLAC.value == "flac"

    def test_construction(self):
        assert AudioFormat("mp3") == AudioFormat.MP3


@pytest.mark.unit
class TestVoiceGender:
    """Tests for VoiceGender enum."""

    def test_all_values(self):
        values = {g.value for g in VoiceGender}
        assert "male" in values
        assert "female" in values
        assert "neutral" in values
        assert "unknown" in values

    def test_construction(self):
        assert VoiceGender("male") == VoiceGender.MALE


@pytest.mark.unit
class TestVoiceInfo:
    """Tests for VoiceInfo dataclass."""

    def test_construction(self):
        v = VoiceInfo(id="en-US-Neural2-A", name="Neural A", language="en-US")
        assert v.id == "en-US-Neural2-A"
        assert v.name == "Neural A"
        assert v.language == "en-US"

    def test_defaults(self):
        v = VoiceInfo(id="v1", name="Voice 1", language="en-US")
        assert v.gender == VoiceGender.UNKNOWN
        assert v.provider == ""
        assert v.sample_rate == 22050
        assert v.is_neural is False
        assert v.styles == []

    def test_to_dict(self):
        v = VoiceInfo(
            id="v1",
            name="V",
            language="en-US",
            gender=VoiceGender.FEMALE,
            sample_rate=16000,
        )
        d = v.to_dict()
        assert d["id"] == "v1"
        assert d["gender"] == "female"
        assert d["sample_rate"] == 16000
        assert "styles" in d

    def test_independent_default_styles(self):
        v1 = VoiceInfo(id="a", name="A", language="en-US")
        v2 = VoiceInfo(id="b", name="B", language="en-US")
        v1.styles.append("cheerful")
        assert v2.styles == []


@pytest.mark.unit
class TestSynthesisResult:
    """Tests for SynthesisResult dataclass."""

    def _make_result(self, data: bytes = b"audio") -> SynthesisResult:
        return SynthesisResult(audio_data=data)

    def test_construction(self):
        r = SynthesisResult(audio_data=b"audio", text="Hello world")
        assert r.audio_data == b"audio"
        assert r.text == "Hello world"
        assert r.format == AudioFormat.WAV

    def test_size_properties(self):
        r = self._make_result(b"x" * 2048)
        assert r.size_bytes == 2048
        assert abs(r.size_kb - 2.0) < 0.01

    def test_save(self, tmp_path: Path):
        r = self._make_result(b"RIFF data")
        out = r.save(tmp_path / "output.wav")
        assert out.exists()
        assert out.read_bytes() == b"RIFF data"
        assert isinstance(out, Path)

    def test_save_accepts_string_path(self, tmp_path: Path):
        r = self._make_result(b"data")
        out_str = str(tmp_path / "out_str.wav")
        out = r.save(out_str)
        assert out.exists()

    def test_to_dict_serialization(self):
        r = SynthesisResult(
            audio_data=b"secret",
            text="Hello",
            format=AudioFormat.MP3,
            duration=2.5,
        )
        d = r.to_dict()
        assert "audio_data" not in d
        assert d["text"] == "Hello"
        assert d["format"] == "mp3"
        assert d["size_bytes"] == 6
        assert d["duration"] == 2.5


@pytest.mark.unit
class TestTTSConfig:
    """Tests for TTSConfig."""

    def test_defaults(self):
        config = TTSConfig()
        assert config.voice is None
        assert config.language == "en-US"
        assert config.rate == 1.0
        assert config.pitch == 1.0
        assert config.volume == 1.0
        assert config.format == AudioFormat.WAV
        assert config.sample_rate == 22050

    def test_custom_values(self):
        config = TTSConfig(
            voice="aria",
            language="fr-FR",
            rate=1.5,
            format=AudioFormat.FLAC,
            style="cheerful",
        )
        assert config.voice == "aria"
        assert config.language == "fr-FR"
        assert config.rate == 1.5
        assert config.format == AudioFormat.FLAC
        assert config.style == "cheerful"


@pytest.mark.unit
class TestSSMLOptions:
    """Tests for SSMLOptions."""

    def test_defaults(self):
        opts = SSMLOptions()
        assert opts.use_ssml is False
        assert opts.auto_breaks is True
        assert opts.emphasis == "moderate"
        assert opts.prosody == {}

    def test_custom_values(self):
        opts = SSMLOptions(use_ssml=True, emphasis="strong", prosody={"rate": "fast"})
        assert opts.use_ssml is True
        assert opts.emphasis == "strong"
        assert opts.prosody["rate"] == "fast"

    def test_independent_default_prosody(self):
        o1 = SSMLOptions()
        o2 = SSMLOptions()
        o1.prosody["rate"] = "fast"
        assert o2.prosody == {}
