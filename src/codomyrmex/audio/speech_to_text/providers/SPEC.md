# Speech-to-Text Providers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Defines the abstract STT provider interface and the Whisper-based concrete implementation for local audio transcription. The provider pattern allows swapping transcription backends without changing consumer code.

## Architecture

Strategy pattern: `STTProvider` (ABC) defines the contract; `WhisperProvider` implements it using `faster-whisper` (CTranslate2). The `get_provider()` factory in `__init__.py` resolves provider names to classes. Providers are conditionally imported based on dependency availability.

## Key Classes

### `STTProvider` (ABC in `base.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `transcribe` | `audio_path: str or Path, config: TranscriptionConfig or None` | `TranscriptionResult` | Synchronous audio transcription |
| `transcribe_async` | `audio_path: str or Path, config: TranscriptionConfig or None` | `TranscriptionResult` | Async transcription (thread pool) |
| `transcribe_stream` | `audio_path: str or Path, config: TranscriptionConfig or None` | `AsyncIterator[TranscriptionResult]` | Streaming partial results |
| `detect_language` | `audio_path: str or Path` | `tuple[str, float]` | Detect language and confidence |
| `get_supported_languages` | -- | `list[str]` | ISO 639-1 language codes |
| `is_loaded` | *(property)* | `bool` | Whether model is ready |
| `unload` | -- | `None` | Free model memory |

### `WhisperProvider` (`whisper_provider.py`)

Extends `STTProvider`. Uses `faster-whisper.WhisperModel` for inference.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `model_size: WhisperModelSize, device: str, compute_type: str, download_root: str or None, local_files_only: bool` | -- | Load Whisper model; raises `ProviderNotAvailableError` if library missing |
| `transcribe` | *(inherited)* | `TranscriptionResult` | Full transcription with segments, words, language detection |
| `_validate_audio_path` | `audio_path: str or Path` | `Path` | Check file exists and format is supported |

### `get_provider()` (factory in `__init__.py`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider_name` | `str` | Provider name (currently only `"whisper"`) |
| `**kwargs` | `object` | Passed to provider constructor |

Returns an initialized `STTProvider`. Raises `ValueError` for unknown names.

## Dependencies

- **Internal**: `audio.speech_to_text.models`, `audio.exceptions`
- **External**: `faster-whisper` (optional; guarded by `try/except ImportError`)

## Constraints

- `faster-whisper` must be installed for `WhisperProvider` to function. Install via `uv sync --extra audio`.
- Audio files must be in a supported format (wav, mp3, flac, ogg, m4a, webm, mp4, mpeg, mpga, oga, opus).
- Zero-mock: real transcription only, `ProviderNotAvailableError` when dependencies are missing.

## Error Handling

- `ProviderNotAvailableError`: raised when required library is not installed.
- `ModelNotLoadedError`: raised when model fails to load or is accessed before loading.
- `AudioFormatError`: raised for unsupported audio file formats.
- `TranscriptionError`: raised for runtime transcription failures.
- All errors logged before propagation.
