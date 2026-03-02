# Codomyrmex Agents -- src/codomyrmex/audio/speech_to_text/providers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides pluggable speech-to-text (STT) provider implementations. Defines an abstract `STTProvider` base class and a concrete `WhisperProvider` that uses the `faster-whisper` library (CTranslate2-accelerated Whisper) for local audio transcription with word-level timestamps and VAD filtering.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `base.py` | `STTProvider` | Abstract base class defining the STT provider interface (transcribe, detect_language, stream) |
| `whisper_provider.py` | `WhisperProvider` | Concrete provider using `faster-whisper` for local transcription with 99+ language support |
| `__init__.py` | `get_provider()` | Factory function to instantiate STT providers by name |

## Operating Contracts

- All providers must implement the `STTProvider` ABC: `transcribe()`, `transcribe_async()`, `transcribe_stream()`, `detect_language()`, `get_supported_languages()`, `is_loaded`, `unload()`.
- `WhisperProvider.__init__()` raises `ProviderNotAvailableError` if `faster-whisper` is not installed.
- `WhisperProvider.transcribe()` raises `ModelNotLoadedError` if the model failed to load, `AudioFormatError` for unsupported formats, `TranscriptionError` for other failures.
- Supported audio formats: `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`, `.webm`, `.mp4`, `.mpeg`, `.mpga`, `.oga`, `.opus`.
- The `get_provider()` factory raises `ValueError` for unrecognized provider names.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `audio.speech_to_text.models` (TranscriptionConfig, TranscriptionResult, WhisperModelSize, Segment, Word), `audio.exceptions` (TranscriptionError, AudioFormatError, ModelNotLoadedError, ProviderNotAvailableError), `faster-whisper` (optional external)
- **Used by**: `audio.speech_to_text` parent module, any consumer of STT functionality

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
