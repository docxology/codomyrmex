# Text-to-Speech Providers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Defines the abstract TTS provider interface and two concrete implementations: `EdgeTTSProvider` for high-quality neural synthesis via Microsoft Edge TTS, and `Pyttsx3Provider` for offline synthesis using platform-native TTS engines.

## Architecture

Strategy pattern: `TTSProvider` (ABC) defines the contract; two concrete providers implement it. The `get_provider()` factory in `__init__.py` resolves provider names to classes. Providers are conditionally imported based on dependency availability.

## Key Classes

### `TTSProvider` (ABC in `base.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `synthesize` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Synchronous speech synthesis |
| `synthesize_async` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Asynchronous synthesis |
| `list_voices` | `language: str or None` | `list[VoiceInfo]` | List available voices, optionally filtered by language |
| `get_voice` | `voice_id: str` | `VoiceInfo or None` | Get voice info by ID |
| `get_supported_languages` | -- | `list[str]` | Language codes supported by this provider |
| `default_voice` | *(property)* | `str` | Default voice identifier |

### `EdgeTTSProvider` (`edge_tts_provider.py`)

Neural TTS via Microsoft Edge service. Outputs MP3 at 24kHz. Default voice: `en-US-AriaNeural`.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `synthesize_async` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Primary synthesis method; streams audio chunks from Edge TTS |
| `synthesize_to_file_async` | `text: str, output_path: str or Path, config: TTSConfig or None` | `Path` | Stream synthesis directly to disk (more efficient for large text) |
| `list_voices_async` | `language: str or None` | `list[VoiceInfo]` | Async voice listing |

### `Pyttsx3Provider` (`pyttsx3_provider.py`)

Offline TTS using system engines. Outputs WAV at ~22kHz.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `synthesize` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Synthesize via pyttsx3 engine; saves to temp file then reads bytes |
| `synthesize_async` | *(inherited)* | `SynthesisResult` | Runs synchronous synthesis in thread pool |

### `get_provider()` (factory in `__init__.py`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider_name` | `str` | `"pyttsx3"`, `"edge-tts"`, `"edge_tts"`, or `"edgetts"` |
| `**kwargs` | `object` | Passed to provider constructor |

Returns an initialized `TTSProvider`. Raises `ValueError` for unknown names.

## Dependencies

- **Internal**: `audio.text_to_speech.models`, `audio.exceptions`
- **External**: `edge-tts` (optional), `pyttsx3` (optional); guarded by `try/except ImportError`

## Constraints

- `edge-tts` requires an internet connection for synthesis and voice listing.
- `pyttsx3` depends on platform TTS engines (SAPI5, NSSpeech, espeak).
- Both libraries installed via `uv sync --extra audio`.
- Zero-mock: real synthesis only, `ProviderNotAvailableError` when dependencies are missing.

## Error Handling

- `ProviderNotAvailableError`: raised when required library is not installed.
- `SynthesisError`: raised for empty text or runtime synthesis failures.
- `VoiceNotFoundError`: raised when a requested voice ID is not available.
- All errors logged before propagation.
