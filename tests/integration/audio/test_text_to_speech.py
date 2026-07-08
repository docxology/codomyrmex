"""Integration tests for the text-to-speech providers."""

from pathlib import Path

import pytest

from codomyrmex.audio.exceptions import ProviderNotAvailableError
from codomyrmex.audio.text_to_speech.models import AudioFormat
from codomyrmex.audio.text_to_speech.providers import (
    EDGE_TTS_AVAILABLE,
    PYTTSX3_AVAILABLE,
    EdgeTTSProvider,
    Pyttsx3Provider,
)
from codomyrmex.audio.text_to_speech.synthesizer import Synthesizer

# Constants for testing
TEST_TEXT = (
    "This is a zero mock functional test of the Codomyrmex text to speech system."
)


@pytest.mark.integration
@pytest.mark.skipif(not PYTTSX3_AVAILABLE, reason="pyttsx3 is not installed")
class TestPyttsx3ProviderIntegration:
    """Zero-mock integration tests for the Pyttsx3 provider (local offline)."""

    def test_synthesize_sync(self, tmp_path: Path):
        """Test synchronous synthesis with pyttsx3."""
        provider = Pyttsx3Provider()

        # Generate audio
        result = provider.synthesize(TEST_TEXT)

        # Basic assertions
        assert result.audio_data
        assert len(result.audio_data) > 0
        assert result.format == AudioFormat.WAV
        assert result.provider == "pyttsx3"
        assert result.text == TEST_TEXT

        # Save to disk and verify file
        output_file = tmp_path / "test_sync.wav"
        saved_file = result.save(output_file)

        assert saved_file.exists()
        assert saved_file.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_synthesize_async(self, tmp_path: Path):
        """Test asynchronous synthesis with pyttsx3."""
        provider = Pyttsx3Provider()

        # Generate audio asynchronously
        result = await provider.synthesize_async(TEST_TEXT)

        # Verify result
        assert result.audio_data
        assert len(result.audio_data) > 0
        assert result.format == AudioFormat.WAV

        # Save to disk and verify file
        output_file = tmp_path / "test_async.wav"
        saved_file = result.save(output_file)

        assert saved_file.exists()
        assert saved_file.stat().st_size > 0


@pytest.mark.integration
@pytest.mark.skipif(not EDGE_TTS_AVAILABLE, reason="edge-tts is not installed")
class TestEdgeTTSProviderIntegration:
    """Zero-mock integration tests for the Edge TTS provider (cloud)."""

    def test_synthesize_sync(self, tmp_path: Path):
        """Test synchronous synthesis with Edge TTS."""
        provider = EdgeTTSProvider()

        # Generate audio
        try:
            result = provider.synthesize(TEST_TEXT)
        except ProviderNotAvailableError as err:
            pytest.skip(f"Edge TTS requires working internet connection: {err}")

        # Basic assertions
        assert result.audio_data
        assert len(result.audio_data) > 0
        assert result.format == AudioFormat.MP3
        assert result.provider == "edge-tts"
        assert result.text == TEST_TEXT

        # Save to disk and verify file
        output_file = tmp_path / "test_sync.mp3"
        saved_file = result.save(output_file)

        assert saved_file.exists()
        assert saved_file.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_synthesize_async(self, tmp_path: Path):
        """Test asynchronous synthesis with Edge TTS."""
        provider = EdgeTTSProvider()

        # Generate audio asynchronously
        try:
            result = await provider.synthesize_async(TEST_TEXT)
        except ProviderNotAvailableError as err:
            pytest.skip(f"Edge TTS requires working internet connection: {err}")

        # Verify result
        assert result.audio_data
        assert len(result.audio_data) > 0
        assert result.format == AudioFormat.MP3

        # Save to disk and verify file
        output_file = tmp_path / "test_async.mp3"
        saved_file = result.save(output_file)

        assert saved_file.exists()
        assert saved_file.stat().st_size > 0


@pytest.mark.integration
class TestSynthesizerInterfaceIntegration:
    """Test the main Synthesizer class functionality with providers."""

    @pytest.mark.skipif(not PYTTSX3_AVAILABLE, reason="pyttsx3 is not installed")
    def test_synthesizer_pyttsx3(self, tmp_path: Path):
        """Test Synthesizer interface with pyttsx3."""
        synth = Synthesizer(provider="pyttsx3")
        result = synth.synthesize(TEST_TEXT)
        assert result.format == AudioFormat.WAV

    @pytest.mark.skipif(not EDGE_TTS_AVAILABLE, reason="edge-tts is not installed")
    def test_synthesizer_edge_tts(self, tmp_path: Path):
        """Test Synthesizer interface with edge-tts."""
        synth = Synthesizer(provider="edge-tts")
        try:
            result = synth.synthesize(TEST_TEXT)
            assert result.format == AudioFormat.MP3
        except ProviderNotAvailableError as err:
            pytest.skip(f"Edge TTS requires working internet connection: {err}")
