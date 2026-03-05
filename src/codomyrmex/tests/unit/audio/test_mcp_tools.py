import wave
from pathlib import Path
from typing import Any

import pytest

from codomyrmex.audio.mcp_tools import (
    audio_batch_transcribe,
    audio_detect_language,
    audio_get_capabilities,
    audio_list_voices,
    audio_synthesize,
    audio_transcribe,
)


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
def test_audio_list_voices() -> None:
    """Test listing voices with invalid provider handles errors gracefully."""
    result = audio_list_voices("invalid_provider")
    assert result["status"] == "error"
    assert "Unknown provider" in result["message"]


@pytest.mark.unit
def test_audio_transcribe_invalid_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test transcribe handles missing files."""

    # Mock transcriber to prevent model download
    class MockTranscriber:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "MockTranscriber":
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def transcribe(self, path: str, *args: Any, **kwargs: Any) -> None:
            raise Exception("File not found")

    monkeypatch.setattr("codomyrmex.audio.speech_to_text.Transcriber", MockTranscriber)

    result = audio_transcribe("/path/does/not/exist.wav")
    assert result["success"] is False
    assert "error" in result


@pytest.mark.unit
def test_audio_detect_language_invalid_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test detect_language handles missing files."""

    # Mock transcriber to prevent model download
    class MockTranscriber:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "MockTranscriber":
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def detect_language(self, path: str, *args: Any, **kwargs: Any) -> None:
            raise Exception("File not found")

    monkeypatch.setattr("codomyrmex.audio.speech_to_text.Transcriber", MockTranscriber)

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
    temp_output_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test batch transcribe with invalid files returns failure list."""

    # Mock transcriber initialization to prevent downloading large models in tests
    class MockTranscriber:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "MockTranscriber":
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def transcribe(self, path: str, *args: Any, **kwargs: Any) -> None:
            raise Exception("File not found")

    monkeypatch.setattr("codomyrmex.audio.speech_to_text.Transcriber", MockTranscriber)

    result = audio_batch_transcribe(
        ["/invalid/1.wav", "/invalid/2.wav"], str(temp_output_dir), model_size="tiny"
    )
    assert result["success"] is True  # the tool itself succeeds in trying
    assert result["result"]["processed"] == 0
    assert result["result"]["failed"] == 2
