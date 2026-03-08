"""Tests for audio.text_to_speech.models."""

from pathlib import Path

from codomyrmex.audio.text_to_speech.models import (
    AudioFormat,
    SSMLOptions,
    SynthesisResult,
    TTSConfig,
    VoiceGender,
    VoiceInfo,
)


class TestAudioFormat:
    def test_values(self):
        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.MP3.value == "mp3"
        assert AudioFormat.OGG.value == "ogg"
        assert AudioFormat.FLAC.value == "flac"

    def test_construction(self):
        assert AudioFormat("mp3") == AudioFormat.MP3


class TestVoiceGender:
    def test_all_values(self):
        values = {g.value for g in VoiceGender}
        assert "male" in values
        assert "female" in values
        assert "neutral" in values
        assert "unknown" in values

    def test_construction(self):
        assert VoiceGender("male") == VoiceGender.MALE


class TestVoiceInfo:
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

    def test_custom_gender(self):
        v = VoiceInfo(id="v1", name="V", language="fr-FR", gender=VoiceGender.FEMALE)
        assert v.gender == VoiceGender.FEMALE

    def test_neural_flag(self):
        v = VoiceInfo(id="v1", name="V", language="en-US", is_neural=True)
        assert v.is_neural is True

    def test_to_dict_basic(self):
        v = VoiceInfo(id="v1", name="Voice", language="en-US")
        d = v.to_dict()
        assert d["id"] == "v1"
        assert d["name"] == "Voice"
        assert d["language"] == "en-US"

    def test_to_dict_gender_serialized(self):
        v = VoiceInfo(id="v1", name="V", language="en-US", gender=VoiceGender.MALE)
        d = v.to_dict()
        assert d["gender"] == "male"

    def test_to_dict_contains_sample_rate(self):
        v = VoiceInfo(id="v1", name="V", language="en-US", sample_rate=16000)
        d = v.to_dict()
        assert d["sample_rate"] == 16000

    def test_to_dict_contains_styles(self):
        v = VoiceInfo(id="v1", name="V", language="en-US")
        d = v.to_dict()
        assert "styles" in d

    def test_independent_default_styles(self):
        v1 = VoiceInfo(id="a", name="A", language="en-US")
        v2 = VoiceInfo(id="b", name="B", language="en-US")
        v1.styles.append("cheerful")
        assert v2.styles == []


class TestSynthesisResult:
    def _make_result(self, data: bytes = b"audio") -> SynthesisResult:
        return SynthesisResult(audio_data=data)

    def test_construction(self):
        r = SynthesisResult(audio_data=b"audio", text="Hello world")
        assert r.audio_data == b"audio"
        assert r.text == "Hello world"
        assert r.format == AudioFormat.WAV

    def test_size_bytes(self):
        r = self._make_result(b"12345")
        assert r.size_bytes == 5

    def test_size_kb(self):
        data = b"x" * 2048
        r = self._make_result(data)
        assert abs(r.size_kb - 2.0) < 0.01

    def test_size_kb_empty(self):
        r = self._make_result(b"")
        assert r.size_kb == 0.0

    def test_save(self, tmp_path):
        r = self._make_result(b"RIFF data")
        out = r.save(tmp_path / "output.wav")
        assert out.exists()
        assert out.read_bytes() == b"RIFF data"

    def test_save_returns_path(self, tmp_path):
        r = self._make_result(b"data")
        result = r.save(tmp_path / "out.wav")
        assert isinstance(result, Path)

    def test_save_accepts_string_path(self, tmp_path):
        r = self._make_result(b"data")
        out = r.save(str(tmp_path / "out.wav"))
        assert out.exists()

    def test_to_dict_excludes_audio_data(self):
        r = self._make_result(b"secret bytes")
        d = r.to_dict()
        assert "audio_data" not in d

    def test_to_dict_contains_text(self):
        r = SynthesisResult(audio_data=b"d", text="Hello world")
        d = r.to_dict()
        assert d["text"] == "Hello world"

    def test_to_dict_contains_size(self):
        r = self._make_result(b"12345")
        d = r.to_dict()
        assert d["size_bytes"] == 5

    def test_to_dict_format(self):
        r = SynthesisResult(audio_data=b"d", format=AudioFormat.MP3)
        d = r.to_dict()
        assert d["format"] == "mp3"

    def test_defaults(self):
        r = SynthesisResult(audio_data=b"")
        assert r.duration == 0.0
        assert r.sample_rate == 22050
        assert r.voice_id == ""
        assert r.text == ""
        assert r.processing_time == 0.0


class TestTTSConfig:
    def test_defaults(self):
        config = TTSConfig()
        assert config.voice is None
        assert config.language == "en-US"
        assert config.rate == 1.0
        assert config.pitch == 1.0
        assert config.volume == 1.0

    def test_default_format(self):
        config = TTSConfig()
        assert config.format == AudioFormat.WAV

    def test_custom_language(self):
        config = TTSConfig(language="fr-FR")
        assert config.language == "fr-FR"

    def test_custom_rate(self):
        config = TTSConfig(rate=1.5)
        assert config.rate == 1.5

    def test_custom_voice(self):
        config = TTSConfig(voice="en-US-Neural2-A")
        assert config.voice == "en-US-Neural2-A"

    def test_custom_format(self):
        config = TTSConfig(format=AudioFormat.FLAC)
        assert config.format == AudioFormat.FLAC

    def test_custom_volume(self):
        config = TTSConfig(volume=0.5)
        assert config.volume == 0.5

    def test_default_sample_rate(self):
        config = TTSConfig()
        assert config.sample_rate == 22050

    def test_style_default_none(self):
        config = TTSConfig()
        assert config.style is None

    def test_emotion_default_none(self):
        config = TTSConfig()
        assert config.emotion is None


class TestSSMLOptions:
    def test_defaults(self):
        opts = SSMLOptions()
        assert opts.use_ssml is False
        assert opts.auto_breaks is True
        assert opts.emphasis == "moderate"

    def test_enable_ssml(self):
        opts = SSMLOptions(use_ssml=True)
        assert opts.use_ssml is True

    def test_disable_auto_breaks(self):
        opts = SSMLOptions(auto_breaks=False)
        assert opts.auto_breaks is False

    def test_custom_emphasis(self):
        opts = SSMLOptions(emphasis="strong")
        assert opts.emphasis == "strong"

    def test_independent_default_prosody(self):
        o1 = SSMLOptions()
        o2 = SSMLOptions()
        o1.prosody["rate"] = "fast"
        assert o2.prosody == {}
