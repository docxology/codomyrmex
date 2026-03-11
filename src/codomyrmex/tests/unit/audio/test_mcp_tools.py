import wave
from pathlib import Path

import pytest

from codomyrmex.audio.mcp_tools import (
    audio_batch_transcribe,
    audio_detect_language,
    audio_get_capabilities,
    audio_list_voices,
    audio_synthesize,
    audio_transcribe,
)
from codomyrmex.audio.speech_to_text.providers import WHISPER_AVAILABLE
from codomyrmex.audio.text_to_speech.providers import PYTTSX3_AVAILABLE, EDGE_TTS_AVAILABLE

@pytest.fixture
def dummy_wav_file(tmp_path: Path) -> Path:
    """Create a short dummy valid WAV file."""
    file_path = tmp_path / "test_audio.wav"

    with wave.open(str(file_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # Create 0.1 seconds of silence
        wav_file.writeframes(b"\x00\x00" * 1600)

    return file_path


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    out_dir = tmp_path / "output"
    out_dir.mkdir(exist_ok=True)
    return out_dir


@pytest.mark.unit
def test_audio_get_capabilities() -> None:
    """Test getting capabilities."""
    result = audio_get_capabilities()
    assert result["status"] == "success"
    assert "stt_providers" in result["capabilities"]
    assert "tts_providers" in result["capabilities"]


@pytest.mark.unit
def test_audio_list_voices_invalid_provider() -> None:
    """Test listing voices with invalid provider handles errors gracefully."""
    result = audio_list_voices("invalid_provider")
    assert result["status"] == "error"
    assert "Unknown provider" in result["message"]


@pytest.mark.unit
@pytest.mark.skipif(not PYTTSX3_AVAILABLE, reason="pyttsx3 not available")
def test_audio_list_voices_pyttsx3() -> None:
    """Test listing voices for pyttsx3."""
    result = audio_list_voices("pyttsx3")
    assert result["status"] == "success"
    assert "voices" in result


@pytest.mark.unit
def test_audio_transcribe_nonexistent_file() -> None:
    """Test transcribe handles missing files."""
    # Use a real Transcriber if available, which should raise TranscriptionError for missing file
    # If not available, it should raise ProviderNotAvailableError
    # Both are handled by the try-except in audio_transcribe
    result = audio_transcribe("/path/does/not/exist.wav")
    assert result["success"] is False
    assert "error" in result
    assert result["error"]["context"]["audio_path"] == "/path/does/not/exist.wav"


@pytest.mark.unit
def test_audio_detect_language_nonexistent_file() -> None:
    """Test detect_language handles missing files."""
    result = audio_detect_language("/path/does/not/exist.wav")
    assert result["success"] is False
    assert "error" in result


@pytest.mark.unit
def test_audio_synthesize_invalid_provider(temp_output_dir: Path) -> None:
    """Test synthesis with invalid provider handles errors gracefully."""
    out_file = temp_output_dir / "out.wav"
    result = audio_synthesize("Hello world", str(out_file), provider="invalid_provider")
    assert result["success"] is False
    assert "error" in result


@pytest.mark.unit
def test_audio_batch_transcribe_invalid_files(
    temp_output_dir: Path
) -> None:
    """Test batch transcribe with invalid files returns failure list."""
    # If WHISPER is available, it returns success: True with failed count
    # If WHISPER is NOT available, it returns success: False with error
    result = audio_batch_transcribe(
        ["/invalid/1.wav", "/invalid/2.wav"], str(temp_output_dir), model_size="tiny"
    )

    if WHISPER_AVAILABLE:
        assert result["success"] is True
        assert result["result"]["processed"] == 0
        assert result["result"]["failed"] == 2
    else:
        assert result["success"] is False
        assert "error" in result


@pytest.mark.unit
@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="Whisper not available")
def test_audio_transcribe_invalid_format(dummy_wav_file: Path) -> None:
    """Test transcription with invalid format (e.g. by changing suffix)."""
    bad_format_path = dummy_wav_file.with_suffix(".txt")
    dummy_wav_file.rename(bad_format_path)

    result = audio_transcribe(str(bad_format_path))
    assert result["success"] is False
    assert "AudioFormatError" in result["error"]["type"]
