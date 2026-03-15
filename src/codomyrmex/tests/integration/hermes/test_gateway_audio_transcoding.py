"""Integration tests for Gateway Audio Transcoding (D1)."""

import math
import struct
import wave

import pytest

from codomyrmex.agents.hermes.gateway.platforms.media import AudioTranscriber


def _generate_sine_wave(
    freq: float = 440.0, duration: float = 0.5, rate: int = 16000
) -> bytes:
    """Generate a valid synthetic wav file in-memory for testing."""
    import io

    bio = io.BytesIO()

    with wave.open(bio, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)

        n_frames = int(duration * rate)
        # Note: In a genuine zero-mock, feeding a sine wave to a STT model will yield blank text
        # or hallucinations, but it *will* process sequentially without crashing.
        # For an integration test verifying purely the bridging, empty return is perfectly valid.

        for i in range(n_frames):
            value = int(math.sin(2 * math.pi * freq * (i / rate)) * 32767.0)
            data = struct.pack("<h", value)
            wav.writeframesraw(data)

    return bio.getvalue()


@pytest.mark.asyncio
async def test_audio_transcriber_integration() -> None:
    """Verify that raw bytes seamlessly route through the transcriber pipeline."""
    try:
        transcriber = AudioTranscriber()

        wav_bytes = _generate_sine_wave(duration=0.5)

        # We await the async wrapper. We expect successful execution without crashing on subprocesses.
        # The output from a pure sine wave will be an empty string typically.
        transcript = await transcriber.transcribe_bytes(wav_bytes, "synthetic_test.wav")

        # Assert return type and successful pipeline execution
        assert isinstance(transcript, str)
    except Exception as e:
        if "ProviderNotAvailableError" in type(e).__name__:
            pytest.skip("Audio Provider Unavailable")
        raise
