"""Integration tests for the speech-to-text providers."""

from pathlib import Path
from typing import Any

import pytest

from codomyrmex.audio.speech_to_text.models import WhisperModelSize
from codomyrmex.audio.speech_to_text.providers import (
    WHISPER_AVAILABLE,
    WhisperProvider,
)
from codomyrmex.audio.speech_to_text.transcriber import Transcriber

try:
    from codomyrmex.audio.text_to_speech.providers.pyttsx3_provider import (
        Pyttsx3Provider,
        PYTTSX3_AVAILABLE,
    )
except ImportError:
    PYTTSX3_AVAILABLE = False

    class Pyttsx3Provider:
        pass


# Constants for testing
TEST_TEXT = "This is a zero mock functional test of the text to speech system."


@pytest.fixture(scope="module")
def generated_audio_file(tmp_path_factory):
    """Fixture to generate an actual audio file using TTS for testing STT."""
    if not PYTTSX3_AVAILABLE:
        pytest.skip("pyttsx3 is not available to generate test audio")

    try:
        import pyttsx3

        # Ensure we can init the engine. It throws RuntimeError if eSpeak is not installed on Linux.
        pyttsx3.init()
    except Exception as e:
        pytest.skip(f"pyttsx3 native engine initialization failed: {e}")

    tmp_dir = tmp_path_factory.mktemp("stt_test_data")
    audio_path = tmp_dir / "test_audio.wav"

    # Generate real audio
    tts_provider = Pyttsx3Provider()
    result = getattr(tts_provider, "synthesize")(TEST_TEXT)
    result.save(audio_path)

    return audio_path


@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="faster-whisper is not available")
class TestWhisperProviderIntegration:
    """Integration tests for the WhisperProvider."""

    @pytest.mark.integration
    def test_transcribe_sync(self, generated_audio_file):
        """Test synchronous transcription of an audio file."""
        # Initialize provider with small model for speed
        provider = WhisperProvider(
            model_size=WhisperModelSize.TINY,
            compute_type="int8",
        )

        # Ensure we have the audio file
        assert Path(generated_audio_file).exists()

        # Transcribe
        result = provider.transcribe(str(generated_audio_file))

        # Basic validation
        assert result is not None
        assert isinstance(result.text, str)
        assert len(result.text) > 0
        assert result.segments is not None
        assert len(result.segments) > 0

        # Optional: check if some keywords are present
        # This might fail occasionally depending on the TTS quality and Whisper model
        text_lower = result.text.lower()
        # Look for at least one major keyword to prove it's the right audio
        assert any(
            word in text_lower
            for word in ["test", "functional", "mock", "system", "speech"]
        )

    @pytest.mark.integration
    def test_transcribe_with_language_hint(self, generated_audio_file):
        """Test transcription with an explicit language hint."""
        provider = WhisperProvider(
            model_size=WhisperModelSize.TINY,
            compute_type="int8",
        )

        from codomyrmex.audio.speech_to_text.models import TranscriptionConfig

        config = TranscriptionConfig(language="en")

        # Transcribe with language set to English
        result = provider.transcribe(str(generated_audio_file), config=config)

        assert result is not None
        assert result.language == "en"
        assert len(result.text) > 0


@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="faster-whisper is not available")
class TestTranscriberIntegration:
    """Integration tests for the Transcriber coordinator."""

    @pytest.mark.integration
    def test_transcriber_with_whisper(self, generated_audio_file):
        """Test that the Transcriber can successfully use the Whisper provider."""
        # Initialize transcriber explicitly with tiny model
        transcriber = Transcriber(
            model_size=WhisperModelSize.TINY,
            compute_type="int8",
        )

        result = transcriber.transcribe(str(generated_audio_file))

        assert result is not None
        assert len(result.text) > 0
