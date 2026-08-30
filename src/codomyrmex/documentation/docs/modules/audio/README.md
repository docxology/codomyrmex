<!-- readme: generated -->

# audio

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/audio/`

## Overview

Audio processing module for Codomyrmex.

This module provides audio processing capabilities including:
- Speech-to-text (STT) transcription using Whisper
- Text-to-speech (TTS) synthesis using pyttsx3 and Edge TTS

## Submodules

| Submodule | Description |
|-----------|-------------|
| `speech_to_text:` | Audio transcription and language detection |
| `text_to_speech:` | Speech synthesis and voice management |

## Public Exports

`audio` exports 14 public symbols via `__all__`:

`EDGE_TTS_AVAILABLE`, `PYTTSX3_AVAILABLE`, `STT_AVAILABLE`, `TTS_AVAILABLE`, `WHISPER_AVAILABLE`, `AudioError`, `AudioFormatError`, `ModelNotLoadedError`, `ProviderNotAvailableError`, `SynthesisError`, `TranscriptionError`, `VoiceNotFoundError`, `__version__`, `cli_commands`

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../audio/](../../../../audio/)
