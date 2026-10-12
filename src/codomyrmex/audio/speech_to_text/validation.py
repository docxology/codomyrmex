"""Validate transcription inputs without acquiring model or native resources."""

from pathlib import Path

from codomyrmex.audio.exceptions import AudioFormatError, TranscriptionError

SUPPORTED_FORMATS = {
    ".wav",
    ".mp3",
    ".flac",
    ".ogg",
    ".m4a",
    ".webm",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".oga",
    ".opus",
}


def validate_audio_path(audio_path: str | Path) -> Path:
    """Require a regular file and supported suffix before loading a model."""
    path = Path(audio_path)
    if not path.exists():
        raise TranscriptionError(f"Audio file not found: {path}", audio_path=path)
    if not path.is_file():
        raise TranscriptionError(f"Audio path is not a file: {path}", audio_path=path)
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise AudioFormatError(
            f"Unsupported audio format: {path.suffix}",
            format_type=path.suffix,
            supported_formats=sorted(SUPPORTED_FORMATS),
        )
    return path
