"""Integration tests for the speech-to-text providers."""

from pathlib import Path

import pytest

from codomyrmex.audio.speech_to_text.models import WhisperModelSize
from codomyrmex.audio.speech_to_text.providers import (
    WHISPER_AVAILABLE,
    WhisperProvider,
)
from codomyrmex.audio.speech_to_text.transcriber import Transcriber
from codomyrmex.audio.text_to_speech.providers import (
    PYTTSX3_AVAILABLE,
    Pyttsx3Provider,
)

# Constants for testing
TEST_TEXT = "This is a zero mock functional test of the text to speech system."


@pytest.fixture(scope="module")
def generated_audio_file(tmp_path_factory):
    """Fixture to generate an actual audio file using TTS for testing STT."""
    if not PYTTSX3_AVAILABLE:
        pytest.skip("pyttsx3 is not available to generate test audio")

    tmp_dir = tmp_path_factory.mktemp("stt_test_data")
    audio_path = tmp_dir / "test_audio.wav"

    # Generate real audio
    tts_provider = Pyttsx3Provider()
    result = tts_provider.synthesize(TEST_TEXT)
    result.save(audio_path)

    return audio_path


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="faster-whisper is not installed")
class TestWhisperProviderIntegration:
    """Zero-mock integration tests for the Whisper provider."""

    def test_transcribe_sync(self, generated_audio_file: Path):
        """Test synchronous transcription with Whisper tiny model."""
        # Use the tiny model for testing to minimize download/execution time
        provider = WhisperProvider(model_size=WhisperModelSize.TINY)

        # Transcribe audio
        result = provider.transcribe(generated_audio_file)

        # Basic assertions
        assert result.text
        assert len(result.text) > 0
        assert len(result.segments) > 0

        # Verify language detection (assuming it detects English)
        assert result.language == "en"
        assert result.duration > 0

        # Verify text content roughly matches (whisper isn't perfect, especially tiny)
        lower_text = result.text.lower()
        assert "zero" in lower_text or "mock" in lower_text or "test" in lower_text

    @pytest.mark.asyncio
    async def test_transcribe_async(self, generated_audio_file: Path):
        """Test asynchronous transcription with Whisper."""
        provider = WhisperProvider(model_size=WhisperModelSize.TINY)

        # Transcribe audio asynchronously
        result = await provider.transcribe_async(generated_audio_file)

        # Verify result
        assert result.text
        assert len(result.segments) > 0
        assert result.language == "en"

    def test_export_formats(self, generated_audio_file: Path, tmp_path: Path):
        """Test that TranscriptionResult correctly formats and saves VTT/SRT."""
        provider = WhisperProvider(model_size=WhisperModelSize.TINY)
        result = provider.transcribe(generated_audio_file)

        # Save SRT
        srt_file = tmp_path / "test.srt"
        saved_srt = result.save_srt(srt_file)
        assert saved_srt.exists()
        srt_text = srt_file.read_text("utf-8")
        assert "-->" in srt_text
        assert "1" in srt_text

        # Save VTT
        vtt_file = tmp_path / "test.vtt"
        saved_vtt = result.save_vtt(vtt_file)
        assert saved_vtt.exists()
        vtt_text = vtt_file.read_text("utf-8")
        assert vtt_text.startswith("WEBVTT")


@pytest.mark.integration
@pytest.mark.slow
class TestTranscriberInterfaceIntegration:
    """Test the main Transcriber class functionality."""

    @pytest.mark.skipif(not WHISPER_AVAILABLE, reason="faster-whisper is not installed")
    def test_transcriber_whisper(self, generated_audio_file: Path):
        """Test Transcriber interface with whisper provider."""
        transcriber = Transcriber(provider="whisper", model_size=WhisperModelSize.TINY)
        result = transcriber.transcribe(generated_audio_file)

        assert result.text
        assert result.language == "en"
