"""Zero-mock tests for audio MCP tools."""

from pathlib import Path

from codomyrmex.audio.mcp_tools import (
    audio_list_formats,
    audio_get_info,
    audio_transcribe,
)


def test_audio_list_formats() -> None:
    """Test audio_list_formats tool."""
    result = audio_list_formats()

    assert result["status"] == "success"
    assert "supported_formats" in result
    formats = result["supported_formats"]
    assert "wav" in formats
    assert "mp3" in formats
    assert "flac" in formats


def test_audio_get_info(tmp_path: Path) -> None:
    """Test audio_get_info tool."""
    # Test valid file
    audio_file = tmp_path / "test_audio.mp3"
    audio_file.write_bytes(b"dummy audio data")

    result = audio_get_info(str(audio_file))

    assert result["status"] == "success"
    assert "metadata" in result
    assert result["metadata"]["filename"] == "test_audio.mp3"
    assert result["metadata"]["extension"] == "mp3"
    assert result["metadata"]["size_bytes"] == 16

    # Test file not found
    missing_file = tmp_path / "missing.wav"
    result_missing = audio_get_info(str(missing_file))

    assert result_missing["status"] == "error"
    assert "not found" in result_missing["message"].lower()

    # Test path is not a file
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    result_dir = audio_get_info(str(dir_path))

    assert result_dir["status"] == "error"
    assert "not a file" in result_dir["message"].lower()


def test_audio_transcribe(tmp_path: Path) -> None:
    """Test audio_transcribe tool.

    We test the error cases to ensure the tool handles missing files
    and invalid enums gracefully, avoiding expensive real transcription
    calls in unit tests while adhering to zero-mock policies.
    """
    # Test file not found
    missing_file = tmp_path / "missing.wav"
    result_missing = audio_transcribe(str(missing_file))

    assert result_missing["status"] == "error"
    assert "not found" in result_missing["message"].lower()

    # Test invalid model size
    valid_file = tmp_path / "valid.wav"
    valid_file.write_bytes(b"dummy data")

    result_invalid_model = audio_transcribe(str(valid_file), model_size="super_huge")

    assert result_invalid_model["status"] == "error"
    assert "invalid model size" in result_invalid_model["message"].lower()

    # Due to zero mock, we avoid testing transcription on a fake audio file
    # because it will pass through Transcriber and fail deeply in the Whisper library
    # or take significant time/download models. Testing the tool's bounds and input
    # validation is sufficient for the MCP tool wrapper itself.

    # We test that the transcribe wrapper catches internal errors (like an invalid audio file format)
    result_invalid_audio = audio_transcribe(str(valid_file))

    assert result_invalid_audio["status"] == "error"
    assert "message" in result_invalid_audio
