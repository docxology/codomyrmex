<!-- markdownlint-disable MD060 -->
# Text-to-Speech Providers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Defines the abstract TTS provider interface and two concrete implementations: `EdgeTTSProvider` for high-quality neural synthesis via Microsoft Edge TTS, and `Pyttsx3Provider` for offline synthesis using platform-native TTS engines.

## Architecture

Strategy pattern: `TTSProvider` (ABC) defines the contract; two concrete providers implement it. The `get_provider()` factory in `__init__.py` resolves provider names to classes. Providers are conditionally imported based on dependency availability.

## Key Classes

### `TTSProvider` (ABC in `base.py`)

| Method | Parameters | Returns | Description |
| -------- | ----------- | --------- | ------------- |
| `synthesize` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Synchronous speech synthesis |
| `synthesize_async` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Asynchronous synthesis |
| `list_voices` | `language: str or None` | `list[VoiceInfo]` | List available voices, optionally filtered by language |
| `get_voice` | `voice_id: str` | `VoiceInfo or None` | Get voice info by ID |
| `get_supported_languages` | -- | `list[str]` | Language codes supported by this provider |
| `default_voice` | *(property)* | `str` | Default voice identifier |

### `EdgeTTSProvider` (`edge_tts_provider.py`)

Neural TTS via Microsoft Edge service. Outputs MP3 at 24kHz. Default voice: `en-US-AriaNeural`.
Each remote operation uses a provider-owned IPv4 `aiohttp` connector and
awaited cleanup so failed or interrupted requests do not leave transports
behind during event-loop shutdown.

| Method | Parameters | Returns | Description |
| -------- | ----------- | --------- | ------------- |
| `synthesize_async` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Primary synthesis method; streams audio chunks from Edge TTS |
| `synthesize_to_file_async` | `text: str, output_path: str or Path, config: TTSConfig or None` | `Path` | Stream synthesis directly to disk (more efficient for large text) |
| `list_voices_async` | `language: str or None` | `list[VoiceInfo]` | Async voice listing |

### `Pyttsx3Provider` (`pyttsx3_provider.py`)

Offline TTS using system engines. Outputs WAV at ~22kHz.

| Method | Parameters | Returns | Description |
| -------- | ----------- | --------- | ------------- |
| `synthesize` | `text: str, config: TTSConfig or None` | `SynthesisResult` | Synthesize via pyttsx3 engine; saves to temp file then reads bytes |
| `synthesize_async` | *(inherited)* | `SynthesisResult` | Runs synchronous synthesis in thread pool |

### `get_provider()` (factory in `__init__.py`)

| Parameter | Type | Description |
| ----------- | ------ | ------------- |
| `provider_name` | `str` | `"pyttsx3"`, `"edge-tts"`, `"edge_tts"`, or `"edgetts"` |
| `**kwargs` | `object` | Passed to provider constructor |

Returns an initialized `TTSProvider`. Raises `ValueError` for unknown names.

## Dependencies

- **Internal**: `audio.text_to_speech.models`, `audio.exceptions`
- **External**: `edge-tts` (optional), `pyttsx3` (optional); availability
  requires the Python package and, on Linux, a discoverable eSpeak/eSpeak-ng
  shared library.

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

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../../README.md)

## Edge stream transport ownership

For in-memory and direct-file synthesis, the installed `edge-tts` library owns
one connector per stream session. The provider does not supply a shared connector:
individual text chunks and the library's existing HTTP 403 recovery may each open
a new session, and the previous session closes its owned connector. Socket
connect/read timeouts remain 10/60 seconds. The voice-inventory request retains its
explicit IPv4 connector and awaited cleanup. No provider retry policy was added.

```bash
uv run --locked pytest -q tests/unit/audio/test_edge_tts_lifecycle.py
```

The local regression uses the actual Edge `Communicate` configuration and actual
aiohttp sessions across successive lifetimes. Live Edge synthesis requires the
remote service; HTTP 403 is an unavailable service observation, not successful
synthesis acceptance.

Both Edge synthesis paths use the same supported-prosody conversion. Speaking
rate is a multiplier mapped to `int((rate - 1) * 100)` percent; pitch preserves the
existing neutral-at-one mapping `int((pitch - 1) * 50)` Hz. Volume is a gain in
[0, 1], mapped to `int((volume - 1) * 100)` percent (1 is +0%, 0.5 is -50%, and
0 is -100%). Edge's integer setting resolution truncates toward zero. Nonfinite
settings, nonpositive speaking rate, and out-of-range volume raise `SynthesisError`.
Direct-file synthesis now honors pitch and volume, and rejects empty/whitespace
text before the Edge library opens the output file. Local tests construct real
Edge request configurations and exercise direct-file rejection with real temporary
paths; they do not establish the acoustic result of a live remote synthesis.
