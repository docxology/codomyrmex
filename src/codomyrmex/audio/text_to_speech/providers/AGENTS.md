# Codomyrmex Agents -- src/codomyrmex/audio/text_to_speech/providers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides pluggable text-to-speech (TTS) provider implementations. Defines an abstract `TTSProvider` base class and two concrete providers: `EdgeTTSProvider` (Microsoft Edge neural voices, requires internet) and `Pyttsx3Provider` (offline synthesis using system TTS engines).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `base.py` | `TTSProvider` | Abstract base class defining the TTS provider interface (synthesize, list_voices, get_voice) |
| `edge_tts_provider.py` | `EdgeTTSProvider` | Neural TTS via Microsoft Edge service; 300+ voices in 40+ languages; free, requires internet |
| `pyttsx3_provider.py` | `Pyttsx3Provider` | Offline TTS using system engines (SAPI5 on Windows, NSSpeechSynthesizer on macOS, espeak on Linux) |
| `__init__.py` | `get_provider()` | Factory function to instantiate TTS providers by name (`"pyttsx3"`, `"edge-tts"`) |

## Operating Contracts

- All providers must implement the `TTSProvider` ABC: `synthesize()`, `synthesize_async()`, `list_voices()`, `get_voice()`, `get_supported_languages()`, `default_voice`.
- Both providers raise `ProviderNotAvailableError` if their respective library is not installed.
- `synthesize()` raises `SynthesisError` for empty text or runtime failures, `VoiceNotFoundError` for invalid voice IDs.
- `EdgeTTSProvider` loads voice list lazily from the Edge TTS service on first use.
- `Pyttsx3Provider` loads system voices eagerly at initialization.
- The `get_provider()` factory raises `ValueError` for unrecognized provider names.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `audio.text_to_speech.models` (TTSConfig, SynthesisResult, VoiceInfo, AudioFormat, VoiceGender), `audio.exceptions` (SynthesisError, VoiceNotFoundError, ProviderNotAvailableError), `edge-tts` (optional), `pyttsx3` (optional)
- **Used by**: `audio.text_to_speech` parent module, any consumer of TTS functionality

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
