"""
Unit tests for audio.exceptions — Zero-Mock compliant.

Covers: AudioError, TranscriptionError, SynthesisError, AudioFormatError,
ModelNotLoadedError, ProviderNotAvailableError, VoiceNotFoundError —
context field storage, inheritance, truncation logic, raise/catch patterns.
"""

from pathlib import Path

import pytest

from codomyrmex.audio.exceptions import (
    AudioError,
    AudioFormatError,
    ModelNotLoadedError,
    ProviderNotAvailableError,
    SynthesisError,
    TranscriptionError,
    VoiceNotFoundError,
)
from codomyrmex.exceptions import CodomyrmexError


# ── AudioError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAudioError:
    def test_is_codomyrmex_error(self):
        e = AudioError("audio fail")
        assert isinstance(e, CodomyrmexError)

    def test_is_exception(self):
        e = AudioError("audio fail")
        assert isinstance(e, Exception)

    def test_message_in_str(self):
        e = AudioError("something broke")
        assert "something broke" in str(e)

    def test_audio_path_string_stored(self):
        e = AudioError("fail", audio_path="/tmp/sound.wav")
        assert e.context["audio_path"] == "/tmp/sound.wav"

    def test_audio_path_path_object_stored_as_string(self):
        e = AudioError("fail", audio_path=Path("/tmp/sound.wav"))
        assert e.context["audio_path"] == "/tmp/sound.wav"
        assert isinstance(e.context["audio_path"], str)

    def test_audio_path_none_not_stored(self):
        e = AudioError("fail", audio_path=None)
        assert "audio_path" not in e.context

    def test_no_audio_path_context_empty(self):
        e = AudioError("fail")
        assert "audio_path" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(AudioError, match="bad audio"):
            raise AudioError("bad audio", audio_path="/tmp/x.wav")


# ── TranscriptionError ───────────────────────────────────────────────


@pytest.mark.unit
class TestTranscriptionError:
    def test_is_audio_error(self):
        e = TranscriptionError("transcription fail")
        assert isinstance(e, AudioError)

    def test_is_codomyrmex_error(self):
        e = TranscriptionError("fail")
        assert isinstance(e, CodomyrmexError)

    def test_message_in_str(self):
        e = TranscriptionError("whisper crashed")
        assert "whisper crashed" in str(e)

    def test_audio_path_stored_via_parent(self):
        e = TranscriptionError("fail", audio_path="/tmp/speech.mp3")
        assert e.context["audio_path"] == "/tmp/speech.mp3"

    def test_audio_path_path_object_stored(self):
        e = TranscriptionError("fail", audio_path=Path("/var/audio/clip.wav"))
        assert e.context["audio_path"] == "/var/audio/clip.wav"

    def test_language_stored(self):
        e = TranscriptionError("fail", language="en")
        assert e.context["language"] == "en"

    def test_model_size_stored(self):
        e = TranscriptionError("fail", model_size="large-v2")
        assert e.context["model_size"] == "large-v2"

    def test_none_language_not_stored(self):
        e = TranscriptionError("fail", language=None)
        assert "language" not in e.context

    def test_none_model_size_not_stored(self):
        e = TranscriptionError("fail", model_size=None)
        assert "model_size" not in e.context

    def test_all_fields_stored(self):
        e = TranscriptionError(
            "fail",
            audio_path="/tmp/clip.wav",
            language="fr",
            model_size="medium",
        )
        assert e.context["audio_path"] == "/tmp/clip.wav"
        assert e.context["language"] == "fr"
        assert e.context["model_size"] == "medium"

    def test_no_optional_fields_context_empty(self):
        e = TranscriptionError("fail")
        assert "audio_path" not in e.context
        assert "language" not in e.context
        assert "model_size" not in e.context

    def test_raise_and_catch_as_audio_error(self):
        with pytest.raises(AudioError):
            raise TranscriptionError("transcription failed", language="de")


# ── SynthesisError ───────────────────────────────────────────────────


@pytest.mark.unit
class TestSynthesisError:
    def test_is_audio_error(self):
        e = SynthesisError("synthesis fail")
        assert isinstance(e, AudioError)

    def test_short_text_stored_as_is(self):
        e = SynthesisError("fail", text="Hello world")
        assert e.context["text"] == "Hello world"

    def test_long_text_truncated_at_100(self):
        long_text = "w" * 200
        e = SynthesisError("fail", text=long_text)
        result = e.context["text"]
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")

    def test_text_exactly_100_not_truncated(self):
        exact_text = "a" * 100
        e = SynthesisError("fail", text=exact_text)
        assert e.context["text"] == exact_text
        assert not e.context["text"].endswith("...")

    def test_none_text_not_stored(self):
        e = SynthesisError("fail", text=None)
        assert "text" not in e.context

    def test_voice_id_stored(self):
        e = SynthesisError("fail", voice_id="fTtv3eikoepIosk8dTZ5")
        assert e.context["voice_id"] == "fTtv3eikoepIosk8dTZ5"

    def test_none_voice_id_not_stored(self):
        e = SynthesisError("fail", voice_id=None)
        assert "voice_id" not in e.context

    def test_all_fields_stored(self):
        e = SynthesisError("fail", text="say this", voice_id="v_123")
        assert e.context["text"] == "say this"
        assert e.context["voice_id"] == "v_123"

    def test_no_optional_fields_context_clean(self):
        e = SynthesisError("tts crashed")
        assert "text" not in e.context
        assert "voice_id" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(SynthesisError, match="output failed"):
            raise SynthesisError("output failed", voice_id="v_abc")


# ── AudioFormatError ─────────────────────────────────────────────────


@pytest.mark.unit
class TestAudioFormatError:
    def test_is_audio_error(self):
        e = AudioFormatError("format fail")
        assert isinstance(e, AudioError)

    def test_format_type_stored(self):
        e = AudioFormatError("fail", format_type="AIFF")
        assert e.context["format_type"] == "AIFF"

    def test_none_format_type_not_stored(self):
        e = AudioFormatError("fail", format_type=None)
        assert "format_type" not in e.context

    def test_supported_formats_stored(self):
        fmts = ["WAV", "MP3", "FLAC"]
        e = AudioFormatError("fail", supported_formats=fmts)
        assert e.context["supported_formats"] == fmts

    def test_none_supported_formats_not_stored(self):
        e = AudioFormatError("fail", supported_formats=None)
        assert "supported_formats" not in e.context

    def test_empty_list_supported_formats_not_stored(self):
        # empty list is falsy — not stored per source logic
        e = AudioFormatError("fail", supported_formats=[])
        assert "supported_formats" not in e.context

    def test_all_fields_stored(self):
        e = AudioFormatError(
            "unsupported format",
            format_type="AIFF",
            supported_formats=["WAV", "MP3"],
        )
        assert e.context["format_type"] == "AIFF"
        assert "WAV" in e.context["supported_formats"]

    def test_no_fields_context_clean(self):
        e = AudioFormatError("bad format")
        assert "format_type" not in e.context
        assert "supported_formats" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(AudioFormatError):
            raise AudioFormatError("unsupported", format_type="AIFF")


# ── ModelNotLoadedError ──────────────────────────────────────────────


@pytest.mark.unit
class TestModelNotLoadedError:
    def test_is_audio_error(self):
        e = ModelNotLoadedError("model not found")
        assert isinstance(e, AudioError)

    def test_model_name_stored(self):
        e = ModelNotLoadedError("fail", model_name="whisper")
        assert e.context["model_name"] == "whisper"

    def test_none_model_name_not_stored(self):
        e = ModelNotLoadedError("fail", model_name=None)
        assert "model_name" not in e.context

    def test_model_size_stored(self):
        e = ModelNotLoadedError("fail", model_size="large-v3")
        assert e.context["model_size"] == "large-v3"

    def test_none_model_size_not_stored(self):
        e = ModelNotLoadedError("fail", model_size=None)
        assert "model_size" not in e.context

    def test_all_fields_stored(self):
        e = ModelNotLoadedError("fail", model_name="whisper", model_size="base")
        assert e.context["model_name"] == "whisper"
        assert e.context["model_size"] == "base"

    def test_no_fields_context_clean(self):
        e = ModelNotLoadedError("model unavailable")
        assert "model_name" not in e.context
        assert "model_size" not in e.context

    def test_raise_and_catch_as_audio_error(self):
        with pytest.raises(AudioError):
            raise ModelNotLoadedError("not loaded", model_name="whisper")


# ── ProviderNotAvailableError ────────────────────────────────────────


@pytest.mark.unit
class TestProviderNotAvailableError:
    def test_is_audio_error(self):
        e = ProviderNotAvailableError("no provider")
        assert isinstance(e, AudioError)

    def test_provider_name_stored(self):
        e = ProviderNotAvailableError("fail", provider_name="elevenlabs")
        assert e.context["provider_name"] == "elevenlabs"

    def test_none_provider_name_not_stored(self):
        e = ProviderNotAvailableError("fail", provider_name=None)
        assert "provider_name" not in e.context

    def test_missing_packages_stored(self):
        pkgs = ["openai-whisper", "torch"]
        e = ProviderNotAvailableError("fail", missing_packages=pkgs)
        assert e.context["missing_packages"] == pkgs

    def test_none_missing_packages_not_stored(self):
        e = ProviderNotAvailableError("fail", missing_packages=None)
        assert "missing_packages" not in e.context

    def test_empty_missing_packages_not_stored(self):
        # empty list is falsy — not stored per source logic
        e = ProviderNotAvailableError("fail", missing_packages=[])
        assert "missing_packages" not in e.context

    def test_all_fields_stored(self):
        e = ProviderNotAvailableError(
            "missing deps",
            provider_name="whisper",
            missing_packages=["openai-whisper"],
        )
        assert e.context["provider_name"] == "whisper"
        assert "openai-whisper" in e.context["missing_packages"]

    def test_no_fields_context_clean(self):
        e = ProviderNotAvailableError("no audio SDK installed")
        assert "provider_name" not in e.context
        assert "missing_packages" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(ProviderNotAvailableError, match="install"):
            raise ProviderNotAvailableError(
                "install uv sync --extra audio", provider_name="elevenlabs"
            )


# ── VoiceNotFoundError ───────────────────────────────────────────────


@pytest.mark.unit
class TestVoiceNotFoundError:
    def test_is_audio_error(self):
        e = VoiceNotFoundError("voice not found")
        assert isinstance(e, AudioError)

    def test_voice_id_stored(self):
        e = VoiceNotFoundError("fail", voice_id="nonexistent_voice")
        assert e.context["voice_id"] == "nonexistent_voice"

    def test_none_voice_id_not_stored(self):
        e = VoiceNotFoundError("fail", voice_id=None)
        assert "voice_id" not in e.context

    def test_available_voices_stored(self):
        voices = ["voice_a", "voice_b", "voice_c"]
        e = VoiceNotFoundError("fail", available_voices=voices)
        assert e.context["available_voices"] == voices

    def test_available_voices_capped_at_10(self):
        many_voices = [f"v_{i}" for i in range(20)]
        e = VoiceNotFoundError("fail", available_voices=many_voices)
        assert len(e.context["available_voices"]) == 10
        assert e.context["available_voices"] == many_voices[:10]

    def test_available_voices_fewer_than_10_stored_all(self):
        five_voices = [f"v_{i}" for i in range(5)]
        e = VoiceNotFoundError("fail", available_voices=five_voices)
        assert len(e.context["available_voices"]) == 5

    def test_none_available_voices_not_stored(self):
        e = VoiceNotFoundError("fail", available_voices=None)
        assert "available_voices" not in e.context

    def test_empty_available_voices_not_stored(self):
        # empty list is falsy — not stored per source logic
        e = VoiceNotFoundError("fail", available_voices=[])
        assert "available_voices" not in e.context

    def test_all_fields_stored(self):
        e = VoiceNotFoundError(
            "voice missing",
            voice_id="bad_id",
            available_voices=["v_1", "v_2"],
        )
        assert e.context["voice_id"] == "bad_id"
        assert "v_1" in e.context["available_voices"]

    def test_no_fields_context_clean(self):
        e = VoiceNotFoundError("voice unavailable")
        assert "voice_id" not in e.context
        assert "available_voices" not in e.context

    def test_raise_and_catch_as_audio_error(self):
        with pytest.raises(AudioError):
            raise VoiceNotFoundError("no such voice", voice_id="xyz")


# ── Cross-hierarchy checks ───────────────────────────────────────────


@pytest.mark.unit
class TestAudioExceptionHierarchy:
    def test_all_inherit_from_audio_error(self):
        for cls in [
            TranscriptionError,
            SynthesisError,
            AudioFormatError,
            ModelNotLoadedError,
            ProviderNotAvailableError,
            VoiceNotFoundError,
        ]:
            assert issubclass(cls, AudioError), f"{cls.__name__} must inherit AudioError"

    def test_all_inherit_from_codomyrmex_error(self):
        for cls in [
            AudioError,
            TranscriptionError,
            SynthesisError,
            AudioFormatError,
            ModelNotLoadedError,
            ProviderNotAvailableError,
            VoiceNotFoundError,
        ]:
            assert issubclass(cls, CodomyrmexError), (
                f"{cls.__name__} must inherit CodomyrmexError"
            )

    def test_catch_transcription_as_audio_error(self):
        caught = None
        try:
            raise TranscriptionError("whisper fail")
        except AudioError as exc:
            caught = exc
        assert caught is not None
        assert isinstance(caught, TranscriptionError)

    def test_catch_synthesis_as_codomyrmex_error(self):
        caught = None
        try:
            raise SynthesisError("tts fail")
        except CodomyrmexError as exc:
            caught = exc
        assert caught is not None
